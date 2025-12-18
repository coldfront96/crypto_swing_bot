"""
Excel trade logging system
"""
import pandas as pd
import os
from datetime import datetime
import logging
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

class TradeLogger:
    def __init__(self, excel_path: str = "data/trade_history.xlsx"):
        self.excel_path = excel_path
        self.ensure_data_directory()
        self.initialize_excel_file()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
    
    def initialize_excel_file(self):
        """Create or load Excel file"""
        columns = [
            'Trade_ID', 'Symbol', 'Side', 'Status',
            'Entry_Price', 'Exit_Price', 'Quantity',
            'Entry_Time', 'Exit_Time', 'Duration',
            'Stop_Loss', 'Take_Profit',
            'PnL_USD', 'PnL_Percent', 'Risk_Reward',
            'Trade_Reason', 'Strategy_Used',
            'Confidence', 'Notes'
        ]
        
        if not os.path.exists(self.excel_path):
            df = pd.DataFrame(columns=columns)
            df.to_excel(self.excel_path, index=False, sheet_name='Trades')
            logging.info(f"Created trade log: {self.excel_path}")
    
    def log_trade_entry(self, trade_data: dict) -> str:
        """Log when a trade is opened"""
        try:
            trade_id = f"{trade_data['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            log_entry = {
                'Trade_ID': trade_id,
                'Symbol': trade_data['symbol'],
                'Side': trade_data['side'],
                'Status': 'OPEN',
                'Entry_Price': trade_data['entry_price'],
                'Exit_Price': None,
                'Quantity': trade_data['quantity'],
                'Entry_Time': datetime.now(),
                'Exit_Time': None,
                'Duration': None,
                'Stop_Loss': trade_data['stop_loss'],
                'Take_Profit': trade_data['take_profit'],
                'PnL_USD': 0,
                'PnL_Percent': 0,
                'Risk_Reward': trade_data.get('risk_reward', '2:1'),
                'Trade_Reason': trade_data.get('reason', ''),
                'Strategy_Used': trade_data.get('strategy', 'Swing_Trading'),
                'Confidence': trade_data.get('confidence', 'MEDIUM'),
                'Notes': trade_data.get('notes', '')
            }
            
            df = pd.read_excel(self.excel_path) if os.path.exists(self.excel_path) else pd.DataFrame()
            df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
            df.to_excel(self.excel_path, index=False)
            
            logging.info(f"Logged trade entry: {trade_id}")
            return trade_id
            
        except Exception as e:
            logging.error(f"Failed to log trade entry: {e}")
            return None
    
    def log_trade_exit(self, trade_id: str, exit_data: dict) -> bool:
        """Log when a trade is closed"""
        try:
            df = pd.read_excel(self.excel_path)
            trade_idx = df[df['Trade_ID'] == trade_id].index
            
            if len(trade_idx) == 0:
                return False
            
            idx = trade_idx[0]
            entry_price = df.at[idx, 'Entry_Price']
            exit_price = exit_data['exit_price']
            quantity = df.at[idx, 'Quantity']
            side = df.at[idx, 'Side']
            
            # Calculate P&L
            if side == 'LONG':
                pnl_usd = (exit_price - entry_price) * quantity
            else:
                pnl_usd = (entry_price - exit_price) * quantity
            
            pnl_percent = (pnl_usd / (entry_price * quantity)) * 100
            
            # Update record
            df.at[idx, 'Status'] = 'CLOSED'
            df.at[idx, 'Exit_Price'] = exit_price
            df.at[idx, 'Exit_Time'] = datetime.now()
            df.at[idx, 'Duration'] = str(datetime.now() - pd.to_datetime(df.at[idx, 'Entry_Time']))
            df.at[idx, 'PnL_USD'] = round(pnl_usd, 2)
            df.at[idx, 'PnL_Percent'] = round(pnl_percent, 2)
            df.at[idx, 'Notes'] = exit_data.get('notes', '')
            
            df.to_excel(self.excel_path, index=False)
            logging.info(f"Logged trade exit: {trade_id}, P&L: ${pnl_usd:.2f}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to log trade exit: {e}")
            return False
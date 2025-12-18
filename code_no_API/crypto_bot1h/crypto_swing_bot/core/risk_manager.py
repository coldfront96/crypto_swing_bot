"""
Risk management and position sizing
"""
import logging

class RiskManager:
    def __init__(self, total_capital: float = 100.0):
        self.total_capital = total_capital
        self.risk_per_trade = 0.015  # 1.5% risk per trade
        self.max_positions = 1       # Max concurrent trades
        self.min_risk_reward = 2.0   # Minimum 2:1 reward:risk
        
    def calculate_position_size(self, entry_price: float, stop_loss_price: float) -> float:
        """Calculate position size based on risk parameters"""
        try:
            # Calculate risk amount
            risk_amount = self.total_capital * self.risk_per_trade
            
            # Calculate risk per unit
            price_risk = abs(entry_price - stop_loss_price)
            if price_risk <= 0:
                raise ValueError("Invalid stop loss price")
            
            # Calculate quantity
            quantity = risk_amount / price_risk
            
            # Minimum notional check
            notional = quantity * entry_price
            if notional < 10:  # Binance minimum
                quantity = 10 / entry_price
                logging.warning(f"Position size adjusted to meet minimum: {quantity:.6f}")
            
            return round(quantity, 6)
            
        except Exception as e:
            logging.error(f"Position size calculation failed: {e}")
            return 0
    
    def calculate_take_profit(self, entry_price: float, stop_loss_price: float, side: str = "LONG") -> float:
        """Calculate take profit based on risk:reward ratio"""
        risk = abs(entry_price - stop_loss_price)
        reward = risk * self.min_risk_reward
        
        if side == "LONG":
            return round(entry_price + reward, 2)
        else:
            return round(entry_price - reward, 2)
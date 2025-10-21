"""
Wallet Status Monitor - Tracks portfolio, positions, and market conditions
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any


class WalletStatusMonitor:
    """
    Monitors wallet status, portfolio, and market conditions
    Provides real-time status for master agent decision making
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Simulated wallet state
        self.portfolio_value = 100000.0  # Starting portfolio
        self.available_balance = 25000.0  # Available for new trades
        self.current_positions = self._initialize_positions()
        
        # Market data simulation
        self.market_data = {}
        
        print("✅ Wallet Status Monitor initialized")
    
    def _initialize_positions(self) -> List[Dict[str, Any]]:
        """Initialize simulated positions"""
        return [
            {
                'symbol': 'BTC-USD',
                'quantity': 0.2,
                'avg_price': 48000.0,
                'current_price': 49500.0,
                'value': 9900.0,
                'pnl': 300.0,
                'pnl_percent': 3.13
            },
            {
                'symbol': 'ETH-USD',
                'quantity': 3.5,
                'avg_price': 2900.0,
                'current_price': 2850.0,
                'value': 9975.0,
                'pnl': -175.0,
                'pnl_percent': -1.72
            }
        ]
    
    async def get_current_status(self) -> Dict[str, Any]:
        """Get comprehensive wallet and market status"""
        # Update simulated market data
        await self._update_market_data()
        
        # Update position values
        await self._update_positions()
        
        # Calculate portfolio metrics
        total_position_value = sum(pos['value'] for pos in self.current_positions)
        self.portfolio_value = self.available_balance + total_position_value
        
        return {
            'available_balance': self.available_balance,
            'portfolio_value': self.portfolio_value,
            'current_positions': self.current_positions.copy(),
            'total_positions_value': total_position_value,
            'cash_percentage': (self.available_balance / self.portfolio_value) * 100,
            'market_conditions': self._get_market_conditions(),
            'risk_metrics': self._calculate_risk_metrics(),
            'research_triggers': self._identify_research_needs(),
            'timestamp': datetime.now()
        }
    
    async def _update_market_data(self):
        """Update simulated market data"""
        # Simulate price movements
        btc_change = random.uniform(-0.02, 0.03)  # -2% to +3%
        eth_change = random.uniform(-0.015, 0.025)  # -1.5% to +2.5%
        
        self.market_data = {
            'BTC-USD': {
                'price': 49500 * (1 + btc_change),
                'volume': random.randint(20000000, 40000000),
                'change_24h': btc_change * 100
            },
            'ETH-USD': {
                'price': 2850 * (1 + eth_change),
                'volume': random.randint(8000000, 15000000),
                'change_24h': eth_change * 100
            },
            'market_volatility': random.uniform(0.3, 0.8),
            'fear_greed_index': random.randint(40, 75)
        }
    
    async def _update_positions(self):
        """Update position values based on current market data"""
        for position in self.current_positions:
            symbol = position['symbol']
            if symbol in self.market_data:
                current_price = self.market_data[symbol]['price']
                position['current_price'] = current_price
                position['value'] = position['quantity'] * current_price
                position['pnl'] = position['value'] - (position['quantity'] * position['avg_price'])
                position['pnl_percent'] = (position['pnl'] / (position['quantity'] * position['avg_price'])) * 100
    
    def _get_market_conditions(self) -> Dict[str, Any]:
        """Get current market conditions"""
        volatility = self.market_data.get('market_volatility', 0.5)
        
        return {
            'volatility': volatility,
            'trend': 'bullish' if volatility < 0.6 else 'neutral',
            'liquidity': 'high',
            'sentiment': 'positive' if self.market_data.get('fear_greed_index', 50) > 55 else 'neutral',
            'market_regime': self._determine_market_regime(volatility)
        }
    
    def _determine_market_regime(self, volatility: float) -> str:
        """Determine current market regime"""
        if volatility < 0.4:
            return 'low_volatility'
        elif volatility < 0.7:
            return 'normal'
        else:
            return 'high_volatility'
    
    def _calculate_risk_metrics(self) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        total_value = self.portfolio_value
        
        # Calculate concentration
        concentrations = {}
        for position in self.current_positions:
            symbol = position['symbol']
            concentrations[symbol] = (position['value'] / total_value) * 100
        
        # Calculate drawdown (simplified)
        max_drawdown = max([abs(pos['pnl_percent']) for pos in self.current_positions] + [0])
        
        return {
            'max_position_concentration': max(concentrations.values()) if concentrations else 0,
            'total_drawdown': max_drawdown,
            'var_95': total_value * 0.05,  # Simplified VaR
            'sharpe_ratio': 1.2,  # Placeholder
            'beta': 0.85  # Placeholder
        }
    
    def _identify_research_needs(self) -> List[str]:
        """Identify what research is needed based on current status"""
        triggers = []
        
        # Check available funds
        cash_percentage = (self.available_balance / self.portfolio_value) * 100
        if cash_percentage > 15:
            triggers.append('sufficient_funds_available')
        
        # Check for losing positions
        losing_positions = [p for p in self.current_positions if p['pnl_percent'] < -5]
        if losing_positions:
            triggers.append('losing_positions_present')
        
        # Check portfolio diversification
        if len(self.current_positions) < 5:
            triggers.append('portfolio_under_diversified')
        
        # Check market conditions
        market_conditions = self._get_market_conditions()
        if market_conditions['volatility'] > 0.7:
            triggers.append('high_volatility_environment')
        
        if market_conditions['sentiment'] == 'positive':
            triggers.append('favorable_market_sentiment')
        
        return triggers
    
    async def simulate_trade_execution(self, symbol: str, action: str, quantity: float, price: float):
        """Simulate trade execution and update wallet"""
        trade_value = quantity * price
        
        if action == 'BUY':
            if trade_value > self.available_balance:
                raise ValueError("Insufficient funds for buy order")
            
            # Check if position already exists
            existing_position = next((p for p in self.current_positions if p['symbol'] == symbol), None)
            
            if existing_position:
                # Update existing position
                total_quantity = existing_position['quantity'] + quantity
                total_cost = (existing_position['quantity'] * existing_position['avg_price']) + trade_value
                existing_position['avg_price'] = total_cost / total_quantity
                existing_position['quantity'] = total_quantity
            else:
                # Create new position
                new_position = {
                    'symbol': symbol,
                    'quantity': quantity,
                    'avg_price': price,
                    'current_price': price,
                    'value': trade_value,
                    'pnl': 0.0,
                    'pnl_percent': 0.0
                }
                self.current_positions.append(new_position)
            
            # Update available balance
            self.available_balance -= trade_value
            
        elif action == 'SELL':
            # Find position to sell
            position = next((p for p in self.current_positions if p['symbol'] == symbol), None)
            if not position:
                raise ValueError(f"No position found for {symbol}")
            
            if quantity > position['quantity']:
                raise ValueError("Sell quantity exceeds position quantity")
            
            # Calculate P&L for the sold portion
            pnl = (price - position['avg_price']) * quantity
            
            # Update position
            if quantity == position['quantity']:
                # Close entire position
                self.current_positions.remove(position)
            else:
                # Partial sell
                position['quantity'] -= quantity
                position['value'] = position['quantity'] * position['current_price']
            
            # Update available balance
            self.available_balance += trade_value
            
            print(f"💰 Trade executed: {action} {quantity} {symbol} at ${price:.2f} - P&L: ${pnl:.2f}")
        
        # Update portfolio value
        await self.get_current_status()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_pnl = sum(pos['pnl'] for pos in self.current_positions)
        winning_positions = len([p for p in self.current_positions if p['pnl'] > 0])
        
        return {
            'total_pnl': total_pnl,
            'total_pnl_percent': (total_pnl / self.portfolio_value) * 100,
            'winning_positions': winning_positions,
            'total_positions': len(self.current_positions),
            'win_rate': (winning_positions / len(self.current_positions)) * 100 if self.current_positions else 0
        }
"""
Order Book Manager - Handles trade execution through order books
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List, Any

from .datatypes import TradingDecision


class OrderBookManager:
    """
    Manages order book interactions and trade execution
    Simulates order placement, fills, and execution
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Simulated order books
        self.order_books = {
            'BTC-USD': self._initialize_order_book('BTC-USD', 49500),
            'ETH-USD': self._initialize_order_book('ETH-USD', 2850)
        }
        
        # Execution statistics
        self.execution_history = []
        self.slippage_stats = {}
        
        print("✅ Order Book Manager initialized")
    
    def _initialize_order_book(self, symbol: str, base_price: float) -> Dict[str, Any]:
        """Initialize simulated order book"""
        spread = base_price * 0.001  # 0.1% spread
        
        # Generate bid/ask levels
        bids = []
        asks = []
        
        for i in range(5):
            bid_price = base_price - (spread * (i + 1))
            ask_price = base_price + (spread * (i + 1))
            
            bids.append({
                'price': bid_price,
                'quantity': random.uniform(0.5, 2.0) if 'BTC' in symbol else random.uniform(10, 50),
                'level': i + 1
            })
            
            asks.append({
                'price': ask_price,
                'quantity': random.uniform(0.5, 2.0) if 'BTC' in symbol else random.uniform(10, 50),
                'level': i + 1
            })
        
        return {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'last_price': base_price,
            'volume_24h': random.randint(1000000, 5000000),
            'spread': spread,
            'timestamp': datetime.now()
        }
    
    async def execute_trade(self, decision: TradingDecision) -> Dict[str, Any]:
        """Execute a trading decision through the order book"""
        symbol = decision.symbol
        
        if symbol not in self.order_books:
            return {
                'success': False,
                'error': f'Order book not available for {symbol}',
                'execution_price': 0,
                'slippage': 0
            }
        
        try:
            # Simulate order execution
            execution_result = await self._simulate_order_execution(decision)
            
            # Update order book after execution
            await self._update_order_book(symbol, decision, execution_result)
            
            # Record execution
            execution_record = {
                'symbol': symbol,
                'action': decision.action,
                'quantity': decision.quantity,
                'target_price': decision.target_price,
                'execution_price': execution_result['execution_price'],
                'slippage': execution_result['slippage'],
                'timestamp': datetime.now(),
                'confidence': decision.confidence
            }
            
            self.execution_history.append(execution_record)
            
            # Update slippage statistics
            self._update_slippage_stats(symbol, execution_result['slippage'])
            
            return {
                'success': True,
                'execution_price': execution_result['execution_price'],
                'slippage': execution_result['slippage'],
                'filled_quantity': decision.quantity,
                'order_id': f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_price': 0,
                'slippage': 0
            }
    
    async def _simulate_order_execution(self, decision: TradingDecision) -> Dict[str, Any]:
        """Simulate order execution with realistic market impact"""
        symbol = decision.symbol
        order_book = self.order_books[symbol]
        
        # Calculate market impact based on order size
        order_size_ratio = decision.quantity / order_book['asks'][0]['quantity'] if decision.action == 'BUY' else decision.quantity / order_book['bids'][0]['quantity']
        
        # Base slippage calculation
        base_slippage = order_book['spread'] * 0.5  # Half the spread as base slippage
        
        # Size-based slippage (larger orders = more slippage)
        size_slippage = base_slippage * min(order_size_ratio * 2, 5)  # Cap at 5x base slippage
        
        # Volatility-based slippage
        volatility_factor = random.uniform(0.8, 1.2)
        
        total_slippage = size_slippage * volatility_factor
        
        # Determine execution price
        if decision.action == 'BUY':
            # For buys, we pay more than the best ask
            execution_price = order_book['asks'][0]['price'] + total_slippage
        else:  # SELL
            # For sells, we get less than the best bid
            execution_price = order_book['bids'][0]['price'] - total_slippage
        
        # Calculate slippage percentage
        reference_price = order_book['asks'][0]['price'] if decision.action == 'BUY' else order_book['bids'][0]['price']
        slippage_percent = (abs(execution_price - reference_price) / reference_price) * 100
        
        # Simulate execution delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        return {
            'execution_price': execution_price,
            'slippage': slippage_percent,
            'reference_price': reference_price,
            'market_impact': order_size_ratio
        }
    
    async def _update_order_book(self, symbol: str, decision: TradingDecision, execution_result: Dict[str, Any]):
        """Update order book after trade execution"""
        order_book = self.order_books[symbol]
        
        # Update last price
        order_book['last_price'] = execution_result['execution_price']
        
        # Simulate order book replenishment
        if decision.action == 'BUY':
            # Remove liquidity from asks
            quantity_to_fill = decision.quantity
            for ask in order_book['asks']:
                if quantity_to_fill <= 0:
                    break
                if ask['quantity'] > quantity_to_fill:
                    ask['quantity'] -= quantity_to_fill
                    quantity_to_fill = 0
                else:
                    quantity_to_fill -= ask['quantity']
                    ask['quantity'] = 0
        else:  # SELL
            # Remove liquidity from bids
            quantity_to_fill = decision.quantity
            for bid in order_book['bids']:
                if quantity_to_fill <= 0:
                    break
                if bid['quantity'] > quantity_to_fill:
                    bid['quantity'] -= quantity_to_fill
                    quantity_to_fill = 0
                else:
                    quantity_to_fill -= bid['quantity']
                    bid['quantity'] = 0
        
        # Replenish order book
        await self._replenish_order_book(symbol)
        
        order_book['timestamp'] = datetime.now()
    
    async def _replenish_order_book(self, symbol: str):
        """Replenish order book liquidity"""
        order_book = self.order_books[symbol]
        base_price = order_book['last_price']
        
        # Replenish bids
        for i, bid in enumerate(order_book['bids']):
            if bid['quantity'] < 0.1:  # Threshold for replenishment
                bid['quantity'] = random.uniform(0.5, 2.0) if 'BTC' in symbol else random.uniform(10, 50)
                # Slight price adjustment
                bid['price'] = base_price - (order_book['spread'] * (i + 1) * random.uniform(0.9, 1.1))
        
        # Replenish asks
        for i, ask in enumerate(order_book['asks']):
            if ask['quantity'] < 0.1:  # Threshold for replenishment
                ask['quantity'] = random.uniform(0.5, 2.0) if 'BTC' in symbol else random.uniform(10, 50)
                # Slight price adjustment
                ask['price'] = base_price + (order_book['spread'] * (i + 1) * random.uniform(0.9, 1.1))
    
    def _update_slippage_stats(self, symbol: str, slippage: float):
        """Update slippage statistics"""
        if symbol not in self.slippage_stats:
            self.slippage_stats[symbol] = {
                'total_trades': 0,
                'total_slippage': 0.0,
                'max_slippage': 0.0,
                'min_slippage': float('inf')
            }
        
        stats = self.slippage_stats[symbol]
        stats['total_trades'] += 1
        stats['total_slippage'] += slippage
        stats['max_slippage'] = max(stats['max_slippage'], slippage)
        stats['min_slippage'] = min(stats['min_slippage'], slippage)
    
    def get_order_book_state(self, symbol: str) -> Dict[str, Any]:
        """Get current order book state"""
        if symbol not in self.order_books:
            return {}
        
        order_book = self.order_books[symbol]
        best_bid = order_book['bids'][0]['price'] if order_book['bids'] else 0
        best_ask = order_book['asks'][0]['price'] if order_book['asks'] else 0
        
        return {
            'symbol': symbol,
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': best_ask - best_bid if best_ask and best_bid else 0,
            'spread_percent': ((best_ask - best_bid) / best_bid * 100) if best_bid else 0,
            'mid_price': (best_bid + best_ask) / 2 if best_bid and best_ask else 0,
            'bid_depth': sum(bid['quantity'] for bid in order_book['bids']),
            'ask_depth': sum(ask['quantity'] for ask in order_book['asks']),
            'last_price': order_book['last_price'],
            'volume_24h': order_book['volume_24h'],
            'timestamp': order_book['timestamp']
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_trades = len(self.execution_history)
        
        if total_trades == 0:
            return {
                'total_trades': 0,
                'average_slippage': 0,
                'success_rate': 0
            }
        
        successful_trades = len([h for h in self.execution_history if h.get('execution_price', 0) > 0])
        total_slippage = sum(h.get('slippage', 0) for h in self.execution_history)
        
        return {
            'total_trades': total_trades,
            'successful_trades': successful_trades,
            'success_rate': (successful_trades / total_trades) * 100,
            'average_slippage': total_slippage / total_trades,
            'slippage_by_symbol': {
                symbol: {
                    'average_slippage': stats['total_slippage'] / stats['total_trades'],
                    'max_slippage': stats['max_slippage'],
                    'min_slippage': stats['min_slippage'],
                    'total_trades': stats['total_trades']
                }
                for symbol, stats in self.slippage_stats.items()
            }
        }
"""
Master-Slave Architecture for TradingAgents-crypto
Centralized coordination with specialized research slaves
"""

from .master_agent import MarketTradingAgent
from .slave_orchestrator import SlaveOrchestrator, SlaveAgent
from .wallet_monitor import WalletStatusMonitor
from .order_manager import OrderBookManager
from .performance_optimizer import PerformanceOptimizer
from .datatypes import ResearchReport, TradingDecision

__all__ = [
    'MarketTradingAgent',
    'SlaveOrchestrator', 
    'SlaveAgent',
    'WalletStatusMonitor',
    'OrderBookManager',
    'PerformanceOptimizer',
    'ResearchReport',
    'TradingDecision'
]
"""
Data types for Master-Slave architecture
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any


@dataclass
class ResearchReport:
    """Standardized research report from slave agents"""
    agent_type: str
    findings: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    confidence: float
    timestamp: datetime


@dataclass
class TradingDecision:
    """Final trading decision made by master agent"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    quantity: float
    target_price: float
    confidence: float
    reasoning: str
    risk_assessment: Dict[str, Any]
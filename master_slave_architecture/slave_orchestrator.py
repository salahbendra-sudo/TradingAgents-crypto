"""
Slave Orchestrator - Manages specialized research slave agents
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from .datatypes import ResearchReport


class SlaveAgent:
    """Base class for all slave agents"""
    
    def __init__(self, agent_type: str, config: Dict[str, Any] = None):
        self.agent_type = agent_type
        self.config = config or {}
        self.performance_history = []
        
    async def execute_research(self, task: str, wallet_status: Dict[str, Any]) -> ResearchReport:
        """Execute research task and return report"""
        raise NotImplementedError("Subclasses must implement execute_research")
    
    def get_performance_score(self) -> float:
        """Get performance score based on historical accuracy"""
        if not self.performance_history:
            return 0.7  # Default confidence
        
        # Calculate average performance
        return sum(self.performance_history) / len(self.performance_history)


class TechnicalAnalysisSlave(SlaveAgent):
    """Technical analysis specialist slave"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__('technical_analysis', config)
        
    async def execute_research(self, task: str, wallet_status: Dict[str, Any]) -> ResearchReport:
        """Execute technical analysis research"""
        print(f"🔧 Technical Analysis Slave executing: {task}")
        
        # Simulate technical analysis research
        await asyncio.sleep(1)  # Simulate processing time
        
        findings = {
            'rsi_levels': {'BTC-USD': 45.2, 'ETH-USD': 62.8},
            'support_resistance': {
                'BTC-USD': {'support': 48000, 'resistance': 52000},
                'ETH-USD': {'support': 2800, 'resistance': 3200}
            },
            'trend_direction': {'BTC-USD': 'bullish', 'ETH-USD': 'neutral'},
            'entry_signals': {
                'BTC-USD': 'strong_buy' if task == 'research_buy_opportunities' else 'hold',
                'ETH-USD': 'buy' if task == 'research_buy_opportunities' else 'hold'
            }
        }
        
        recommendations = []
        
        if task == 'research_buy_opportunities':
            recommendations = [
                {
                    'symbol': 'BTC-USD',
                    'action': 'BUY',
                    'confidence': 0.85,
                    'reasoning': 'RSI oversold, strong support at 48k, bullish trend'
                },
                {
                    'symbol': 'ETH-USD', 
                    'action': 'BUY',
                    'confidence': 0.70,
                    'reasoning': 'Neutral trend but good risk/reward near support'
                }
            ]
        elif task == 'find_exit_strategies':
            recommendations = [
                {
                    'symbol': 'BTC-USD',
                    'action': 'HOLD',
                    'confidence': 0.60,
                    'reasoning': 'No clear exit signal, wait for resistance test'
                }
            ]
        
        confidence = 0.78 if task == 'research_buy_opportunities' else 0.65
        
        return ResearchReport(
            agent_type=self.agent_type,
            findings=findings,
            recommendations=recommendations,
            confidence=confidence,
            timestamp=datetime.now()
        )


class FundamentalAnalysisSlave(SlaveAgent):
    """Fundamental analysis specialist slave"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__('fundamental_analysis', config)
        
    async def execute_research(self, task: str, wallet_status: Dict[str, Any]) -> ResearchReport:
        """Execute fundamental analysis research"""
        print(f"📊 Fundamental Analysis Slave executing: {task}")
        
        # Simulate fundamental analysis research
        await asyncio.sleep(1.5)
        
        findings = {
            'market_cap_analysis': {
                'BTC-USD': 'dominant_position',
                'ETH-USD': 'strong_fundamentals'
            },
            'adoption_metrics': {
                'BTC-USD': 'institutional_adoption_increasing',
                'ETH-USD': 'defi_growth_strong'
            },
            'regulatory_environment': 'neutral_to_positive',
            'macro_factors': 'favorable_for_crypto'
        }
        
        recommendations = [
            {
                'symbol': 'BTC-USD',
                'action': 'BUY',
                'confidence': 0.80,
                'reasoning': 'Strong fundamentals, institutional adoption increasing'
            },
            {
                'symbol': 'ETH-USD',
                'action': 'BUY', 
                'confidence': 0.75,
                'reasoning': 'DeFi ecosystem growth, strong developer activity'
            }
        ]
        
        return ResearchReport(
            agent_type=self.agent_type,
            findings=findings,
            recommendations=recommendations,
            confidence=0.75,
            timestamp=datetime.now()
        )


class SentimentAnalysisSlave(SlaveAgent):
    """Market sentiment analysis specialist slave"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__('sentiment_analysis', config)
        
    async def execute_research(self, task: str, wallet_status: Dict[str, Any]) -> ResearchReport:
        """Execute sentiment analysis research"""
        print(f"😊 Sentiment Analysis Slave executing: {task}")
        
        # Simulate sentiment analysis research
        await asyncio.sleep(1.2)
        
        findings = {
            'social_sentiment': {
                'BTC-USD': 0.72,  # Positive sentiment
                'ETH-USD': 0.65   # Slightly positive
            },
            'news_sentiment': {
                'BTC-USD': 0.68,
                'ETH-USD': 0.62
            },
            'fear_greed_index': 65,  # Greed territory
            'market_mood': 'optimistic'
        }
        
        recommendations = [
            {
                'symbol': 'BTC-USD',
                'action': 'BUY',
                'confidence': 0.70,
                'reasoning': 'Positive social sentiment, greed index suggests momentum'
            },
            {
                'symbol': 'ETH-USD',
                'action': 'HOLD',
                'confidence': 0.55,
                'reasoning': 'Moderate sentiment, wait for clearer signals'
            }
        ]
        
        return ResearchReport(
            agent_type=self.agent_type,
            findings=findings,
            recommendations=recommendations,
            confidence=0.68,
            timestamp=datetime.now()
        )


class RiskAssessmentSlave(SlaveAgent):
    """Risk assessment specialist slave"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__('risk_assessment', config)
        
    async def execute_research(self, task: str, wallet_status: Dict[str, Any]) -> ResearchReport:
        """Execute risk assessment research"""
        print(f"🛡️  Risk Assessment Slave executing: {task}")
        
        # Simulate risk assessment research
        await asyncio.sleep(1.3)
        
        findings = {
            'market_volatility': 0.45,
            'portfolio_risk': 'moderate',
            'correlation_analysis': {
                'BTC-USD': 0.85,
                'ETH-USD': 0.78
            },
            'liquidity_analysis': 'high_liquidity',
            'systemic_risks': 'low'
        }
        
        if task == 'analyze_loss_recovery':
            recommendations = [
                {
                    'symbol': 'BTC-USD',
                    'action': 'HOLD',
                    'confidence': 0.65,
                    'reasoning': 'Risk of selling at bottom, better to hold through volatility'
                }
            ]
        else:
            recommendations = [
                {
                    'symbol': 'BTC-USD',
                    'action': 'BUY',
                    'confidence': 0.72,
                    'reasoning': 'Acceptable risk levels, good risk/reward ratio'
                },
                {
                    'symbol': 'ETH-USD',
                    'action': 'BUY',
                    'confidence': 0.68,
                    'reasoning': 'Moderate risk, suitable for current portfolio'
                }
            ]
        
        return ResearchReport(
            agent_type=self.agent_type,
            findings=findings,
            recommendations=recommendations,
            confidence=0.70,
            timestamp=datetime.now()
        )


class SlaveOrchestrator:
    """
    Orchestrates all slave agents and manages their execution
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize slave agents
        self.slave_agents = {
            'technical': TechnicalAnalysisSlave(config),
            'fundamental': FundamentalAnalysisSlave(config),
            'sentiment': SentimentAnalysisSlave(config),
            'risk': RiskAssessmentSlave(config)
        }
        
        print("✅ Slave Orchestrator initialized with 4 specialized agents")
    
    async def execute_research_task(self, 
                                  agent_type: str, 
                                  task: str, 
                                  wallet_status: Dict[str, Any]) -> ResearchReport:
        """Execute research task with specified slave agent"""
        if agent_type not in self.slave_agents:
            raise ValueError(f"Unknown slave agent type: {agent_type}")
        
        agent = self.slave_agents[agent_type]
        
        try:
            report = await agent.execute_research(task, wallet_status)
            
            # Track performance (simplified)
            agent.performance_history.append(report.confidence)
            
            return report
            
        except Exception as e:
            print(f"❌ Slave agent {agent_type} failed: {e}")
            # Return empty report on failure
            return ResearchReport(
                agent_type=agent_type,
                findings={},
                recommendations=[],
                confidence=0.0,
                timestamp=datetime.now()
            )
    
    def get_available_slaves(self) -> List[str]:
        """Get list of available slave agents"""
        return list(self.slave_agents.keys())
    
    def get_slave_performance(self) -> Dict[str, float]:
        """Get performance scores for all slave agents"""
        return {
            agent_type: agent.get_performance_score()
            for agent_type, agent in self.slave_agents.items()
        }
    
    async def execute_parallel_research(self, 
                                      research_tasks: Dict[str, str],
                                      wallet_status: Dict[str, Any]) -> Dict[str, ResearchReport]:
        """Execute multiple research tasks in parallel"""
        tasks = []
        agent_types = []
        
        for agent_type, task in research_tasks.items():
            if agent_type in self.slave_agents:
                tasks.append(
                    self.execute_research_task(agent_type, task, wallet_status)
                )
                agent_types.append(agent_type)
        
        # Execute all research tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        research_report = {}
        for agent_type, result in zip(agent_types, results):
            if isinstance(result, Exception):
                print(f"❌ Parallel research failed for {agent_type}: {result}")
                research_report[agent_type] = ResearchReport(
                    agent_type=agent_type,
                    findings={},
                    recommendations=[],
                    confidence=0.0,
                    timestamp=datetime.now()
                )
            else:
                research_report[agent_type] = result
        
        return research_report
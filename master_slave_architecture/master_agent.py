"""
Market Trading Agent - Master Agent
Central coordinator that manages wallet status, activates slave research,
and executes final trading decisions.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from .slave_orchestrator import SlaveOrchestrator
from .wallet_monitor import WalletStatusMonitor
from .order_manager import OrderBookManager
from .datatypes import ResearchReport, TradingDecision


class MarketTradingAgent:
    """
    Master Agent - Central coordinator for the trading system
    
    Responsibilities:
    - Monitor wallet and portfolio status
    - Activate slave agents for research
    - Interpret research reports into trading decisions
    - Execute trades through order books
    - Manage overall risk and system state
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Core components
        self.wallet_monitor = WalletStatusMonitor(config)
        self.slave_orchestrator = SlaveOrchestrator(config)
        self.order_manager = OrderBookManager(config)
        
        # Trading parameters
        self.min_confidence_threshold = 0.65
        self.max_risk_per_trade = 0.02  # 2% of portfolio
        self.max_position_size = 0.15   # 15% max per position
        self.daily_loss_limit = 0.03    # 3% daily loss limit
        
        # State tracking
        self.last_research_time = None
        self.trade_history = []
        self.performance_metrics = {}
        
        print("✅ Market Trading Agent (Master) initialized")
    
    async def run_trading_cycle(self):
        """Main trading cycle - runs continuously"""
        print("🚀 Starting Master Agent trading cycle...")
        
        while True:
            try:
                # 1. Monitor current wallet status
                wallet_status = await self.wallet_monitor.get_current_status()
                
                # 2. Check if research is needed
                if self._needs_research(wallet_status):
                    print("🔍 Research needed - activating slave agents...")
                    
                    # 3. Activate slave agents for research
                    research_report = await self._activate_slaves_for_research(wallet_status)
                    
                    # 4. Interpret research into trading decisions
                    trading_decisions = await self._interpret_research_report(research_report, wallet_status)
                    
                    # 5. Execute validated trades
                    await self._execute_trades(trading_decisions, wallet_status)
                    
                    # Update last research time
                    self.last_research_time = datetime.now()
                
                # Wait before next cycle
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"❌ Error in trading cycle: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
    
    def _needs_research(self, wallet_status: Dict[str, Any]) -> bool:
        """Determine if research is needed based on wallet status"""
        conditions = []
        
        # Check available funds
        if wallet_status['available_balance'] > wallet_status['portfolio_value'] * 0.1:
            conditions.append("sufficient_funds_available")
        
        # Check portfolio diversification
        if len(wallet_status['current_positions']) < 8:  # Room for more positions
            conditions.append("portfolio_not_full")
        
        # Check for losing positions
        losing_positions = [p for p in wallet_status['current_positions'] 
                          if p.get('pnl_percent', 0) < -0.05]
        if losing_positions:
            conditions.append("losing_positions_present")
        
        # Regular research interval (every 2 hours)
        if (self.last_research_time is None or 
            datetime.now() - self.last_research_time > timedelta(hours=2)):
            conditions.append("regular_research_interval")
        
        # Market condition triggers
        if wallet_status['market_conditions'].get('volatility', 0) > 0.7:
            conditions.append("high_volatility_environment")
        
        return len(conditions) > 0
    
    async def _activate_slaves_for_research(self, wallet_status: Dict[str, Any]) -> Dict[str, ResearchReport]:
        """Activate relevant slave agents based on current needs"""
        research_tasks = {}
        
        # Determine research needs from wallet status
        if wallet_status['available_balance'] > wallet_status['portfolio_value'] * 0.15:
            # Significant funds available - research new investments
            research_tasks['technical'] = 'research_buy_opportunities'
            research_tasks['fundamental'] = 'assess_market_fundamentals'
            research_tasks['sentiment'] = 'analyze_market_sentiment'
        
        # Check for losing positions
        losing_positions = [p for p in wallet_status['current_positions'] 
                          if p.get('pnl_percent', 0) < -0.08]
        if losing_positions:
            research_tasks['risk'] = 'analyze_loss_recovery'
            research_tasks['technical'] = 'find_exit_strategies'
        
        # High volatility environment
        if wallet_status['market_conditions'].get('volatility', 0) > 0.8:
            research_tasks['risk'] = 'assess_volatility_risk'
            research_tasks['technical'] = 'analyze_volatility_patterns'
        
        # Execute research tasks
        research_report = {}
        for agent_type, task in research_tasks.items():
            try:
                report = await self.slave_orchestrator.execute_research_task(
                    agent_type, task, wallet_status
                )
                research_report[agent_type] = report
                print(f"✅ {agent_type} research completed - Confidence: {report.confidence:.2f}")
            except Exception as e:
                print(f"❌ {agent_type} research failed: {e}")
        
        return research_report
    
    async def _interpret_research_report(self, 
                                       research_report: Dict[str, ResearchReport],
                                       wallet_status: Dict[str, Any]) -> List[TradingDecision]:
        """Interpret slave research reports into executable trading decisions"""
        consolidated_decisions = {}
        
        # Consolidate recommendations from all agents
        for agent_type, report in research_report.items():
            for recommendation in report.recommendations:
                symbol = recommendation.get('symbol', 'UNKNOWN')
                
                if symbol not in consolidated_decisions:
                    consolidated_decisions[symbol] = {
                        'buy_votes': 0.0,
                        'sell_votes': 0.0,
                        'hold_votes': 0.0,
                        'total_confidence': 0.0,
                        'agent_recommendations': [],
                        'reasoning': []
                    }
                
                # Weight votes by agent confidence and report confidence
                vote_weight = recommendation.get('confidence', 0.5) * report.confidence
                action = recommendation.get('action', 'HOLD')
                
                if action == 'BUY':
                    consolidated_decisions[symbol]['buy_votes'] += vote_weight
                elif action == 'SELL':
                    consolidated_decisions[symbol]['sell_votes'] += vote_weight
                else:
                    consolidated_decisions[symbol]['hold_votes'] += vote_weight
                
                consolidated_decisions[symbol]['total_confidence'] += vote_weight
                consolidated_decisions[symbol]['agent_recommendations'].append({
                    'agent': agent_type,
                    'action': action,
                    'confidence': vote_weight,
                    'reasoning': recommendation.get('reasoning', '')
                })
        
        # Make final decisions
        final_decisions = []
        for symbol, decision_data in consolidated_decisions.items():
            if decision_data['total_confidence'] == 0:
                continue
                
            # Determine final action based on weighted votes
            buy_score = decision_data['buy_votes'] / decision_data['total_confidence']
            sell_score = decision_data['sell_votes'] / decision_data['total_confidence']
            hold_score = decision_data['hold_votes'] / decision_data['total_confidence']
            
            final_action = 'HOLD'
            final_confidence = hold_score
            
            if buy_score > sell_score and buy_score > hold_score:
                final_action = 'BUY'
                final_confidence = buy_score
            elif sell_score > buy_score and sell_score > hold_score:
                final_action = 'SELL'
                final_confidence = sell_score
            
            # Only proceed if confidence meets threshold
            if final_confidence >= self.min_confidence_threshold:
                trading_decision = TradingDecision(
                    symbol=symbol,
                    action=final_action,
                    quantity=0,  # Will be calculated based on risk
                    target_price=self._calculate_target_price(symbol, final_action),
                    confidence=final_confidence,
                    reasoning=f"Consensus: {final_action} (Confidence: {final_confidence:.2f})",
                    risk_assessment=self._assess_trade_risk(symbol, final_action, wallet_status)
                )
                
                # Calculate position size
                trading_decision.quantity = self._calculate_position_size(
                    trading_decision, wallet_status
                )
                
                final_decisions.append(trading_decision)
        
        return final_decisions
    
    def _calculate_target_price(self, symbol: str, action: str) -> float:
        """Calculate target price for trade (simplified)"""
        # In real implementation, this would use current market data
        # For simulation, return a placeholder
        return 50000.0 if 'BTC' in symbol else 3000.0
    
    def _assess_trade_risk(self, symbol: str, action: str, wallet_status: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk for a potential trade"""
        return {
            'symbol': symbol,
            'action': action,
            'market_volatility': wallet_status['market_conditions'].get('volatility', 0),
            'position_concentration': self._calculate_concentration(symbol, wallet_status),
            'correlation_risk': 0.3,  # Simplified
            'liquidity_risk': 0.1,    # Simplified
        }
    
    def _calculate_position_size(self, 
                               decision: TradingDecision, 
                               wallet_status: Dict[str, Any]) -> float:
        """Calculate position size based on risk management"""
        portfolio_value = wallet_status['portfolio_value']
        
        # Base position size (2% risk per trade)
        base_size = portfolio_value * self.max_risk_per_trade
        
        # Adjust for confidence
        confidence_factor = decision.confidence
        
        # Adjust for volatility (inverse relationship)
        volatility = decision.risk_assessment.get('market_volatility', 0.5)
        volatility_factor = 1 / (volatility * 10) if volatility > 0 else 1
        
        # Adjust for concentration
        concentration = decision.risk_assessment.get('position_concentration', 0)
        concentration_factor = 1 - min(concentration, 0.5)  # Reduce if already concentrated
        
        final_size = base_size * confidence_factor * volatility_factor * concentration_factor
        
        # Apply maximum position limit
        max_position = portfolio_value * self.max_position_size
        return min(final_size, max_position)
    
    def _calculate_concentration(self, symbol: str, wallet_status: Dict[str, Any]) -> float:
        """Calculate current concentration in this symbol"""
        positions = wallet_status['current_positions']
        portfolio_value = wallet_status['portfolio_value']
        
        for position in positions:
            if position.get('symbol') == symbol:
                return position.get('value', 0) / portfolio_value
        
        return 0.0
    
    async def _execute_trades(self, 
                            trading_decisions: List[TradingDecision],
                            wallet_status: Dict[str, Any]):
        """Execute validated trading decisions"""
        executed_trades = []
        
        for decision in trading_decisions:
            # Final validation check
            if self._validate_trade_decision(decision, wallet_status):
                try:
                    # Execute through order manager
                    execution_result = await self.order_manager.execute_trade(decision)
                    
                    if execution_result['success']:
                        executed_trades.append({
                            'decision': decision,
                            'execution': execution_result,
                            'timestamp': datetime.now()
                        })
                        
                        print(f"✅ Executed {decision.action} {decision.symbol} - "
                              f"Quantity: {decision.quantity:.4f}, "
                              f"Confidence: {decision.confidence:.2f}")
                    else:
                        print(f"❌ Trade execution failed: {execution_result['error']}")
                        
                except Exception as e:
                    print(f"❌ Trade execution error: {e}")
            else:
                print(f"⏸️  Trade validation failed for {decision.symbol}")
        
        # Update trade history
        self.trade_history.extend(executed_trades)
    
    def _validate_trade_decision(self, 
                               decision: TradingDecision, 
                               wallet_status: Dict[str, Any]) -> bool:
        """Validate trade decision against risk parameters"""
        risk_checks = [
            decision.confidence >= self.min_confidence_threshold,
            decision.quantity > 0,
            decision.quantity <= wallet_status['available_balance'],
            self._calculate_position_risk(decision) < self.max_risk_per_trade,
            self._check_daily_loss_limit()
        ]
        
        return all(risk_checks)
    
    def _calculate_position_risk(self, decision: TradingDecision) -> float:
        """Calculate risk for this position"""
        # Simplified risk calculation
        return decision.quantity * decision.risk_assessment.get('market_volatility', 0.5)
    
    def _check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been reached"""
        # Simplified - in real implementation, track daily P&L
        return True
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'master_agent': 'active',
            'last_research_time': self.last_research_time,
            'total_trades_executed': len(self.trade_history),
            'slave_agents_available': len(self.slave_orchestrator.get_available_slaves()),
            'performance_metrics': self.performance_metrics
        }
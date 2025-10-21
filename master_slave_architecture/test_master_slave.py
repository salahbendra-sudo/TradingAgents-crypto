"""
Comprehensive Test Suite for Master-Slave Architecture
"""

import asyncio
import unittest
from datetime import datetime
from typing import Dict, Any

from .master_agent import MarketTradingAgent, ResearchReport, TradingDecision
from .slave_orchestrator import SlaveOrchestrator
from .wallet_monitor import WalletStatusMonitor
from .order_manager import OrderBookManager


class TestMasterSlaveArchitecture(unittest.TestCase):
    """Test suite for Master-Slave architecture"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'test_mode': True,
            'min_confidence_threshold': 0.65,
            'max_risk_per_trade': 0.02
        }
    
    def test_master_agent_initialization(self):
        """Test Master Agent initialization"""
        master = MarketTradingAgent(self.config)
        
        self.assertIsNotNone(master.wallet_monitor)
        self.assertIsNotNone(master.slave_orchestrator)
        self.assertIsNotNone(master.order_manager)
        self.assertEqual(master.min_confidence_threshold, 0.65)
        
        print("✅ Master Agent initialization test passed")
    
    def test_slave_orchestrator_initialization(self):
        """Test Slave Orchestrator initialization"""
        orchestrator = SlaveOrchestrator(self.config)
        
        available_slaves = orchestrator.get_available_slaves()
        expected_slaves = ['technical', 'fundamental', 'sentiment', 'risk']
        
        self.assertEqual(len(available_slaves), 4)
        for slave in expected_slaves:
            self.assertIn(slave, available_slaves)
        
        print("✅ Slave Orchestrator initialization test passed")
    
    def test_wallet_monitor_initialization(self):
        """Test Wallet Monitor initialization"""
        wallet_monitor = WalletStatusMonitor(self.config)
        
        self.assertGreater(wallet_monitor.portfolio_value, 0)
        self.assertGreater(wallet_monitor.available_balance, 0)
        self.assertIsInstance(wallet_monitor.current_positions, list)
        
        print("✅ Wallet Monitor initialization test passed")
    
    def test_order_manager_initialization(self):
        """Test Order Manager initialization"""
        order_manager = OrderBookManager(self.config)
        
        self.assertIn('BTC-USD', order_manager.order_books)
        self.assertIn('ETH-USD', order_manager.order_books)
        
        btc_order_book = order_manager.get_order_book_state('BTC-USD')
        self.assertIsNotNone(btc_order_book)
        self.assertIn('best_bid', btc_order_book)
        self.assertIn('best_ask', btc_order_book)
        
        print("✅ Order Manager initialization test passed")
    
    async def test_slave_research_execution(self):
        """Test slave agent research execution"""
        orchestrator = SlaveOrchestrator(self.config)
        
        # Test wallet status
        wallet_status = {
            'available_balance': 25000,
            'portfolio_value': 100000,
            'current_positions': [],
            'market_conditions': {'volatility': 0.5}
        }
        
        # Test technical analysis slave
        report = await orchestrator.execute_research_task(
            'technical', 'research_buy_opportunities', wallet_status
        )
        
        self.assertIsInstance(report, ResearchReport)
        self.assertEqual(report.agent_type, 'technical_analysis')
        self.assertGreater(report.confidence, 0)
        self.assertIsInstance(report.recommendations, list)
        
        print("✅ Slave research execution test passed")
    
    async def test_research_report_interpretation(self):
        """Test research report interpretation by master agent"""
        master = MarketTradingAgent(self.config)
        
        # Create sample research reports
        research_report = {
            'technical': ResearchReport(
                agent_type='technical_analysis',
                findings={'rsi_levels': {'BTC-USD': 45}},
                recommendations=[
                    {'symbol': 'BTC-USD', 'action': 'BUY', 'confidence': 0.85, 'reasoning': 'test'}
                ],
                confidence=0.78,
                timestamp=datetime.now()
            ),
            'fundamental': ResearchReport(
                agent_type='fundamental_analysis',
                findings={},
                recommendations=[
                    {'symbol': 'BTC-USD', 'action': 'BUY', 'confidence': 0.80, 'reasoning': 'test'}
                ],
                confidence=0.75,
                timestamp=datetime.now()
            )
        }
        
        wallet_status = {
            'portfolio_value': 100000,
            'available_balance': 25000,
            'current_positions': [],
            'market_conditions': {'volatility': 0.5}
        }
        
        decisions = await master._interpret_research_report(research_report, wallet_status)
        
        self.assertIsInstance(decisions, list)
        if decisions:
            decision = decisions[0]
            self.assertIsInstance(decision, TradingDecision)
            self.assertIn(decision.action, ['BUY', 'SELL', 'HOLD'])
            self.assertGreater(decision.confidence, 0)
        
        print("✅ Research report interpretation test passed")
    
    async def test_trade_execution_simulation(self):
        """Test trade execution simulation"""
        order_manager = OrderBookManager(self.config)
        
        # Create test trading decision
        decision = TradingDecision(
            symbol='BTC-USD',
            action='BUY',
            quantity=0.1,
            target_price=50000,
            confidence=0.8,
            reasoning='Test trade',
            risk_assessment={}
        )
        
        execution_result = await order_manager.execute_trade(decision)
        
        self.assertIsInstance(execution_result, dict)
        self.assertIn('success', execution_result)
        
        if execution_result['success']:
            self.assertIn('execution_price', execution_result)
            self.assertIn('slippage', execution_result)
        
        print("✅ Trade execution simulation test passed")
    
    async def test_wallet_status_monitoring(self):
        """Test wallet status monitoring"""
        wallet_monitor = WalletStatusMonitor(self.config)
        
        status = await wallet_monitor.get_current_status()
        
        # Check required fields
        required_fields = [
            'available_balance', 'portfolio_value', 'current_positions',
            'market_conditions', 'risk_metrics', 'research_triggers'
        ]
        
        for field in required_fields:
            self.assertIn(field, status)
        
        # Check data types
        self.assertIsInstance(status['available_balance'], (int, float))
        self.assertIsInstance(status['portfolio_value'], (int, float))
        self.assertIsInstance(status['current_positions'], list)
        self.assertIsInstance(status['market_conditions'], dict)
        
        print("✅ Wallet status monitoring test passed")
    
    async def test_full_integration_cycle(self):
        """Test full integration cycle"""
        master = MarketTradingAgent(self.config)
        
        # Get initial wallet status
        wallet_status = await master.wallet_monitor.get_current_status()
        
        # Check if research is needed
        needs_research = master._needs_research(wallet_status)
        self.assertIsInstance(needs_research, bool)
        
        if needs_research:
            # Activate slaves for research
            research_report = await master._activate_slaves_for_research(wallet_status)
            self.assertIsInstance(research_report, dict)
            
            # Interpret research
            if research_report:
                decisions = await master._interpret_research_report(research_report, wallet_status)
                self.assertIsInstance(decisions, list)
        
        print("✅ Full integration cycle test passed")


async def run_all_tests():
    """Run all tests asynchronously"""
    print("\n" + "="*60)
    print("🧪 RUNNING MASTER-SLAVE ARCHITECTURE TESTS")
    print("="*60)
    
    test_suite = TestMasterSlaveArchitecture()
    test_suite.setUp()
    
    # Run synchronous tests
    test_suite.test_master_agent_initialization()
    test_suite.test_slave_orchestrator_initialization()
    test_suite.test_wallet_monitor_initialization()
    test_suite.test_order_manager_initialization()
    
    # Run asynchronous tests
    await test_suite.test_slave_research_execution()
    await test_suite.test_research_report_interpretation()
    await test_suite.test_trade_execution_simulation()
    await test_suite.test_wallet_status_monitoring()
    await test_suite.test_full_integration_cycle()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED SUCCESSFULLY!")
    print("="*60)


async def demo_master_slave_system():
    """Demonstrate the Master-Slave system in action"""
    print("\n" + "="*60)
    print("🚀 DEMONSTRATING MASTER-SLAVE TRADING SYSTEM")
    print("="*60)
    
    # Initialize the system
    master = MarketTradingAgent()
    
    print("\n📊 Initial System Status:")
    status = master.get_system_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n💰 Initial Wallet Status:")
    wallet_status = await master.wallet_monitor.get_current_status()
    print(f"   Portfolio Value: ${wallet_status['portfolio_value']:,.2f}")
    print(f"   Available Balance: ${wallet_status['available_balance']:,.2f}")
    print(f"   Positions: {len(wallet_status['current_positions'])}")
    
    print("\n🔍 Running Research Cycle...")
    
    # Run one research cycle
    if master._needs_research(wallet_status):
        research_report = await master._activate_slaves_for_research(wallet_status)
        
        print(f"\n📋 Research Report Summary:")
        for agent_type, report in research_report.items():
            print(f"   {agent_type}: {len(report.recommendations)} recommendations "
                  f"(Confidence: {report.confidence:.2f})")
        
        if research_report:
            decisions = await master._interpret_research_report(research_report, wallet_status)
            
            print(f"\n🎯 Trading Decisions:")
            for decision in decisions:
                print(f"   {decision.action} {decision.symbol} - "
                      f"Quantity: {decision.quantity:.4f}, "
                      f"Confidence: {decision.confidence:.2f}")
            
            # Execute one sample trade
            if decisions:
                sample_decision = decisions[0]
                print(f"\n⚡ Executing Sample Trade: {sample_decision.action} {sample_decision.symbol}")
                
                await master._execute_trades([sample_decision], wallet_status)
                
                # Show updated status
                updated_status = await master.wallet_monitor.get_current_status()
                print(f"\n📈 Updated Portfolio Value: ${updated_status['portfolio_value']:,.2f}")
                print(f"💰 Updated Available Balance: ${updated_status['available_balance']:,.2f}")
    
    print("\n📊 Final System Statistics:")
    execution_stats = master.order_manager.get_execution_stats()
    print(f"   Total Trades: {execution_stats['total_trades']}")
    print(f"   Success Rate: {execution_stats['success_rate']:.1f}%")
    print(f"   Average Slippage: {execution_stats['average_slippage']:.3f}%")
    
    print("\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("="*60)


if __name__ == "__main__":
    # Run tests
    asyncio.run(run_all_tests())
    
    # Run demonstration
    asyncio.run(demo_master_slave_system())
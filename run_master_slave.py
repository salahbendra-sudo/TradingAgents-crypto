#!/usr/bin/env python3
"""
Master-Slave Trading System - Main Entry Point
Complete implementation with testing and execution
"""

import asyncio
import sys
import argparse
from datetime import datetime

from master_slave_architecture import MarketTradingAgent
from master_slave_architecture.test_master_slave import run_all_tests, demo_master_slave_system


async def run_live_trading():
    """Run the Master-Slave trading system live"""
    print("\n" + "="*70)
    print("🚀 MASTER-SLAVE TRADING SYSTEM - LIVE MODE")
    print("="*70)
    
    # Initialize the Master Agent
    master = MarketTradingAgent()
    
    print("\n✅ System Components Initialized:")
    print(f"   • Market Trading Agent (Master)")
    print(f"   • {len(master.slave_orchestrator.get_available_slaves())} Specialized Slave Agents")
    print(f"   • Wallet Status Monitor")
    print(f"   • Order Book Manager")
    
    print("\n📊 Starting Live Trading Cycle...")
    print("   (Press Ctrl+C to stop)")
    
    try:
        # Run the main trading cycle
        await master.run_trading_cycle()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Trading system stopped by user")
        
        # Show final statistics
        await show_final_statistics(master)


async def show_final_statistics(master):
    """Show final system statistics"""
    print("\n" + "="*70)
    print("📈 FINAL SYSTEM STATISTICS")
    print("="*70)
    
    # System status
    system_status = master.get_system_status()
    print(f"\n🔧 System Status:")
    print(f"   • Master Agent: {system_status['master_agent']}")
    print(f"   • Slave Agents Available: {system_status['slave_agents_available']}")
    print(f"   • Total Trades Executed: {system_status['total_trades_executed']}")
    
    # Wallet status
    wallet_status = await master.wallet_monitor.get_current_status()
    performance = master.wallet_monitor.get_performance_summary()
    
    print(f"\n💰 Portfolio Performance:")
    print(f"   • Portfolio Value: ${wallet_status['portfolio_value']:,.2f}")
    print(f"   • Available Balance: ${wallet_status['available_balance']:,.2f}")
    print(f"   • Total P&L: ${performance['total_pnl']:,.2f}")
    print(f"   • P&L %: {performance['total_pnl_percent']:.2f}%")
    print(f"   • Win Rate: {performance['win_rate']:.1f}%")
    
    # Execution statistics
    execution_stats = master.order_manager.get_execution_stats()
    print(f"\n⚡ Execution Statistics:")
    print(f"   • Total Trades: {execution_stats['total_trades']}")
    print(f"   • Success Rate: {execution_stats['success_rate']:.1f}%")
    print(f"   • Average Slippage: {execution_stats['average_slippage']:.3f}%")
    
    # Slave performance
    slave_performance = master.slave_orchestrator.get_slave_performance()
    print(f"\n🔬 Slave Agent Performance:")
    for agent_type, score in slave_performance.items():
        print(f"   • {agent_type}: {score:.2f}")
    
    # Recent trades
    if master.trade_history:
        print(f"\n📋 Recent Trades (Last 5):")
        recent_trades = master.trade_history[-5:]
        for trade in recent_trades:
            decision = trade['decision']
            execution = trade['execution']
            print(f"   • {decision.action} {decision.symbol} - "
                  f"Qty: {decision.quantity:.4f}, "
                  f"Conf: {decision.confidence:.2f}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Master-Slave Trading System')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--demo', action='store_true', help='Run demonstration')
    parser.add_argument('--live', action='store_true', help='Run live trading')
    
    args = parser.parse_args()
    
    if not any([args.test, args.demo, args.live]):
        # Default: run tests and demo
        print("Running default mode: Tests + Demo")
        asyncio.run(run_all_tests())
        asyncio.run(demo_master_slave_system())
    else:
        if args.test:
            asyncio.run(run_all_tests())
        
        if args.demo:
            asyncio.run(demo_master_slave_system())
        
        if args.live:
            asyncio.run(run_live_trading())


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🤖 TRADINGAGENTS-CRYPTO - MASTER-SLAVE ARCHITECTURE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    print(f"\n✅ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
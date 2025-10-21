"""
Performance Optimizer for Master-Slave Architecture
Monitors and optimizes system performance
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import statistics


@dataclass
class PerformanceMetrics:
    """Performance metrics for system components"""
    component: str
    execution_time: float
    success_rate: float
    error_count: int
    timestamp: datetime


@dataclass
class OptimizationRecommendation:
    """Optimization recommendations"""
    component: str
    issue: str
    recommendation: str
    priority: str  # low, medium, high, critical
    impact: str   # performance, reliability, accuracy


class PerformanceOptimizer:
    """
    Monitors and optimizes Master-Slave system performance
    """
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.optimization_thresholds = {
            'execution_time_warning': 2.0,  # seconds
            'execution_time_critical': 5.0,  # seconds
            'success_rate_warning': 0.85,   # 85%
            'success_rate_critical': 0.70,  # 70%
            'error_rate_warning': 0.05,     # 5%
            'error_rate_critical': 0.10     # 10%
        }
        
        # Performance baselines
        self.baselines = {
            'slave_research_time': 1.5,
            'decision_interpretation_time': 0.5,
            'trade_execution_time': 0.3
        }
        
        print("✅ Performance Optimizer initialized")
    
    def record_metric(self, component: str, execution_time: float, 
                     success: bool, error_count: int = 0):
        """Record performance metric"""
        success_rate = 1.0 if success else 0.0
        
        metric = PerformanceMetrics(
            component=component,
            execution_time=execution_time,
            success_rate=success_rate,
            error_count=error_count,
            timestamp=datetime.now()
        )
        
        self.metrics_history.append(metric)
    
    def get_component_metrics(self, component: str, 
                            time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get metrics for specific component"""
        now = datetime.now()
        
        if time_window:
            metrics = [m for m in self.metrics_history 
                      if m.component == component 
                      and now - m.timestamp <= time_window]
        else:
            metrics = [m for m in self.metrics_history 
                      if m.component == component]
        
        if not metrics:
            return {}
        
        execution_times = [m.execution_time for m in metrics]
        success_rates = [m.success_rate for m in metrics]
        error_counts = [m.error_count for m in metrics]
        
        return {
            'component': component,
            'total_executions': len(metrics),
            'avg_execution_time': statistics.mean(execution_times),
            'max_execution_time': max(execution_times),
            'min_execution_time': min(execution_times),
            'avg_success_rate': statistics.mean(success_rates),
            'total_errors': sum(error_counts),
            'error_rate': sum(error_counts) / len(metrics),
            'time_window': str(time_window) if time_window else 'all'
        }
    
    def analyze_performance(self) -> List[OptimizationRecommendation]:
        """Analyze system performance and generate recommendations"""
        recommendations = []
        
        # Get recent metrics (last hour)
        time_window = timedelta(hours=1)
        components = set(m.component for m in self.metrics_history)
        
        for component in components:
            metrics = self.get_component_metrics(component, time_window)
            
            if not metrics:
                continue
            
            # Check execution time
            avg_time = metrics['avg_execution_time']
            if avg_time > self.optimization_thresholds['execution_time_critical']:
                recommendations.append(
                    OptimizationRecommendation(
                        component=component,
                        issue=f"Critical execution time: {avg_time:.2f}s",
                        recommendation="Optimize algorithm or add caching",
                        priority="critical",
                        impact="performance"
                    )
                )
            elif avg_time > self.optimization_thresholds['execution_time_warning']:
                recommendations.append(
                    OptimizationRecommendation(
                        component=component,
                        issue=f"High execution time: {avg_time:.2f}s",
                        recommendation="Consider performance improvements",
                        priority="high",
                        impact="performance"
                    )
                )
            
            # Check success rate
            success_rate = metrics['avg_success_rate']
            if success_rate < self.optimization_thresholds['success_rate_critical']:
                recommendations.append(
                    OptimizationRecommendation(
                        component=component,
                        issue=f"Critical success rate: {success_rate:.1%}",
                        recommendation="Investigate and fix reliability issues",
                        priority="critical",
                        impact="reliability"
                    )
                )
            elif success_rate < self.optimization_thresholds['success_rate_warning']:
                recommendations.append(
                    OptimizationRecommendation(
                        component=component,
                        issue=f"Low success rate: {success_rate:.1%}",
                        recommendation="Monitor and improve reliability",
                        priority="medium",
                        impact="reliability"
                    )
                )
            
            # Check error rate
            error_rate = metrics['error_rate']
            if error_rate > self.optimization_thresholds['error_rate_critical']:
                recommendations.append(
                    OptimizationRecommendation(
                        component=component,
                        issue=f"Critical error rate: {error_rate:.1%}",
                        recommendation="Implement better error handling",
                        priority="critical",
                        impact="reliability"
                    )
                )
            elif error_rate > self.optimization_thresholds['error_rate_warning']:
                recommendations.append(
                    OptimizationRecommendation(
                        component=component,
                        issue=f"High error rate: {error_rate:.1%}",
                        recommendation="Improve error handling and logging",
                        priority="high",
                        impact="reliability"
                    )
                )
        
        return recommendations
    
    def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        if not self.metrics_history:
            return 100.0  # No data = assume healthy
        
        # Get recent metrics (last 30 minutes)
        time_window = timedelta(minutes=30)
        recent_metrics = [m for m in self.metrics_history 
                         if datetime.now() - m.timestamp <= time_window]
        
        if not recent_metrics:
            return 100.0
        
        # Calculate health factors
        execution_times = [m.execution_time for m in recent_metrics]
        success_rates = [m.success_rate for m in recent_metrics]
        error_counts = [m.error_count for m in recent_metrics]
        
        # Normalize factors (0-1, higher is better)
        avg_execution_time = statistics.mean(execution_times)
        execution_score = max(0, 1 - (avg_execution_time / 10))  # Cap at 10 seconds
        
        avg_success_rate = statistics.mean(success_rates)
        success_score = avg_success_rate
        
        total_errors = sum(error_counts)
        error_score = max(0, 1 - (total_errors / len(recent_metrics) / 0.1))  # Cap at 10% error rate
        
        # Weighted average
        health_score = (
            execution_score * 0.3 +
            success_score * 0.5 +
            error_score * 0.2
        ) * 100
        
        return min(100, max(0, health_score))
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now(),
            'system_health_score': self.get_system_health_score(),
            'total_metrics_recorded': len(self.metrics_history),
            'component_performance': {},
            'optimization_recommendations': [],
            'performance_trends': {}
        }
        
        # Component performance
        components = set(m.component for m in self.metrics_history)
        for component in components:
            metrics_1h = self.get_component_metrics(component, timedelta(hours=1))
            metrics_24h = self.get_component_metrics(component, timedelta(hours=24))
            
            report['component_performance'][component] = {
                'last_hour': metrics_1h,
                'last_24_hours': metrics_24h
            }
        
        # Optimization recommendations
        recommendations = self.analyze_performance()
        report['optimization_recommendations'] = [
            {
                'component': r.component,
                'issue': r.issue,
                'recommendation': r.recommendation,
                'priority': r.priority,
                'impact': r.impact
            }
            for r in recommendations
        ]
        
        # Performance trends
        report['performance_trends'] = self._calculate_performance_trends()
        
        return report
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.metrics_history) < 10:
            return {'insufficient_data': True}
        
        # Group metrics by hour
        hourly_metrics = {}
        for metric in self.metrics_history:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_metrics:
                hourly_metrics[hour_key] = []
            hourly_metrics[hour_key].append(metric)
        
        # Calculate trends
        execution_trend = []
        success_trend = []
        
        for hour, metrics in sorted(hourly_metrics.items()):
            avg_execution = statistics.mean([m.execution_time for m in metrics])
            avg_success = statistics.mean([m.success_rate for m in metrics])
            
            execution_trend.append({
                'hour': hour,
                'avg_execution_time': avg_execution
            })
            success_trend.append({
                'hour': hour,
                'avg_success_rate': avg_success
            })
        
        return {
            'execution_time_trend': execution_trend[-24:],  # Last 24 hours
            'success_rate_trend': success_trend[-24:],      # Last 24 hours
            'trend_analysis': self._analyze_trends(execution_trend, success_trend)
        }
    
    def _analyze_trends(self, execution_trend: List[Dict], 
                       success_trend: List[Dict]) -> Dict[str, str]:
        """Analyze performance trends"""
        if len(execution_trend) < 2:
            return {'status': 'insufficient_data'}
        
        # Simple trend analysis
        recent_execution = [t['avg_execution_time'] for t in execution_trend[-6:]]  # Last 6 hours
        recent_success = [t['avg_success_rate'] for t in success_trend[-6:]]
        
        execution_slope = (recent_execution[-1] - recent_execution[0]) / len(recent_execution)
        success_slope = (recent_success[-1] - recent_success[0]) / len(recent_success)
        
        analysis = {}
        
        if execution_slope > 0.1:
            analysis['execution_trend'] = 'deteriorating'
        elif execution_slope < -0.1:
            analysis['execution_trend'] = 'improving'
        else:
            analysis['execution_trend'] = 'stable'
        
        if success_slope > 0.05:
            analysis['success_trend'] = 'improving'
        elif success_slope < -0.05:
            analysis['success_trend'] = 'deteriorating'
        else:
            analysis['success_trend'] = 'stable'
        
        return analysis
    
    async def continuous_monitoring(self):
        """Continuous performance monitoring loop"""
        print("🔍 Starting continuous performance monitoring...")
        
        while True:
            try:
                # Generate periodic report
                report = self.generate_performance_report()
                
                # Log critical issues
                critical_recommendations = [
                    r for r in report['optimization_recommendations']
                    if r['priority'] == 'critical'
                ]
                
                if critical_recommendations:
                    print(f"🚨 CRITICAL PERFORMANCE ISSUES DETECTED:")
                    for rec in critical_recommendations:
                        print(f"   • {rec['component']}: {rec['issue']}")
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"❌ Performance monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
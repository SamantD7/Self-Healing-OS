"""
System Reporting Module

Generates various reports about system health, anomalies, and performance.
Provides summaries and trends for analysis and presentation.

Author: [Your Name]
Date: November 5, 2025
"""

from datetime import datetime, timedelta
from collections import Counter
import json


class SystemReporter:
    """
    Generates reports from detector and system statistics
    """
    
    def __init__(self, detector, stats):
        """
        Initialize reporter
        
        Args:
            detector: AnomalyDetector instance
            stats: Dictionary of system statistics
        """
        self.detector = detector
        self.stats = stats
    
    def generate_summary_report(self):
        """
        Generate comprehensive system summary report
        
        Returns:
            str: Formatted report text
        """
        
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("  SELF-HEALING SYSTEM - SUMMARY REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Runtime Information
        report_lines.append("\n" + "-" * 70)
        report_lines.append("RUNTIME INFORMATION")
        report_lines.append("-" * 70)
        
        if self.stats.get('start_time'):
            elapsed = datetime.now() - self.stats['start_time']
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            report_lines.append(f"Total Uptime: {hours:02d}h {minutes:02d}m")
        
        report_lines.append(f"Total Monitoring Cycles: {self.stats.get('cycles', 0)}")
        
        # Anomaly Statistics
        report_lines.append("\n" + "-" * 70)
        report_lines.append("ANOMALY STATISTICS")
        report_lines.append("-" * 70)
        report_lines.append(f"Total Anomalies Detected: {self.stats.get('total_anomalies_detected', 0)}")
        
        # Anomaly Breakdown by Type
        anomaly_types = Counter()
        for anomaly in self.detector.anomaly_history:
            anomaly_types[anomaly['type']] += 1
        
        if anomaly_types:
            report_lines.append("\nAnomalies by Type:")
            for atype, count in anomaly_types.most_common():
                report_lines.append(f"  {atype:<30} {count:>5}")
        
        # Severity Breakdown
        severity_breakdown = self.detector.get_severity_breakdown()
        report_lines.append("\nAnomalies by Severity:")
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_breakdown.get(severity, 0)
            if count > 0:
                report_lines.append(f"  {severity:<15} {count:>5}")
        
        # Healing Statistics
        report_lines.append("\n" + "-" * 70)
        report_lines.append("HEALING STATISTICS")
        report_lines.append("-" * 70)
        report_lines.append(f"Total Healing Attempts: {self.stats.get('total_healing_attempts', 0)}")
        report_lines.append(f"Successful Healings: {self.stats.get('successful_healings', 0)}")
        report_lines.append(f"Failed Healings: {self.stats.get('failed_healings', 0)}")
        
        if self.stats.get('total_healing_attempts', 0) > 0:
            success_rate = (self.stats['successful_healings'] / self.stats['total_healing_attempts']) * 100
            report_lines.append(f"Success Rate: {success_rate:.1f}%")
        
        # Health Score Analysis
        report_lines.append("\n" + "-" * 70)
        report_lines.append("HEALTH SCORE ANALYSIS")
        report_lines.append("-" * 70)
        
        current_health = self.detector.get_system_health_score()
        report_lines.append(f"Current Health Score: {current_health}/100")
        
        if current_health >= 80:
            status = "EXCELLENT - System operating optimally"
        elif current_health >= 60:
            status = "GOOD - Minor issues present"
        elif current_health >= 40:
            status = "FAIR - Multiple issues detected"
        elif current_health >= 20:
            status = "POOR - Significant problems"
        else:
            status = "CRITICAL - System in danger"
        
        report_lines.append(f"Status: {status}")
        
        # Most Common Anomalies
        report_lines.append("\n" + "-" * 70)
        report_lines.append("MOST COMMON ISSUES")
        report_lines.append("-" * 70)
        
        most_common = self.detector.get_most_common_anomalies(limit=5)
        if most_common:
            for idx, (atype, count) in enumerate(most_common, 1):
                report_lines.append(f"{idx}. {atype} - {count} occurrences")
        else:
            report_lines.append("No anomalies recorded")
        
        # Recent Trends
        report_lines.append("\n" + "-" * 70)
        report_lines.append("RECENT TRENDS (Last Hour)")
        report_lines.append("-" * 70)
        
        trend = self.detector.get_anomaly_trend(hours=1)
        if trend:
            for atype, count in trend.items():
                report_lines.append(f"  {atype:<30} {count:>5}")
        else:
            report_lines.append("  No anomalies in last hour")
        
        report_lines.append("\n" + "=" * 70)
        
        return "\n".join(report_lines)
    
    def generate_hourly_report(self, hours=1):
        """
        Generate report for specific time period
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            str: Formatted report
        """
        
        report_lines = []
        report_lines.append(f"\n{'=' * 70}")
        report_lines.append(f"  HOURLY REPORT - Last {hours} Hour(s)")
        report_lines.append(f"{'=' * 70}")
        
        # Get anomalies from time period
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_anomalies = [
            a for a in self.detector.anomaly_history
            if datetime.fromisoformat(a['timestamp']) > cutoff_time
        ]
        
        report_lines.append(f"\nTotal Anomalies: {len(recent_anomalies)}")
        
        if recent_anomalies:
            # Count by type
            type_counts = Counter(a['type'] for a in recent_anomalies)
            report_lines.append("\nBy Type:")
            for atype, count in type_counts.most_common():
                report_lines.append(f"  {atype}: {count}")
            
            # Count by severity
            severity_counts = Counter(a['severity'] for a in recent_anomalies)
            report_lines.append("\nBy Severity:")
            for severity, count in severity_counts.most_common():
                report_lines.append(f"  {severity}: {count}")
        else:
            report_lines.append("\nNo anomalies in this period - System healthy!")
        
        report_lines.append(f"\n{'=' * 70}\n")
        
        return "\n".join(report_lines)
    
    def generate_health_trend_data(self, hours=24):
        """
        Generate health score trend data for graphing
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            list: List of (timestamp, health_score) tuples
        """
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Get health scores from anomaly history
        # (Each anomaly affects health negatively)
        health_data = []
        
        for anomaly in self.detector.anomaly_history:
            timestamp = datetime.fromisoformat(anomaly['timestamp'])
            if timestamp > cutoff_time:
                # Calculate health at that point
                # This is simplified - you could track actual health over time
                health_data.append((timestamp.isoformat(), anomaly.get('health_score', 100)))
        
        return health_data

"""
Log File Analyzer

Analyzes healing_system.log to extract statistics and insights.
Useful for post-mortem analysis and understanding system behavior.

Usage:
    python analyze_logs.py

Author: [Your Name]
Date: November 5, 2025
"""

import re
from collections import Counter
from datetime import datetime


class LogAnalyzer:
    """
    Analyzes log files to extract insights
    """
    
    def __init__(self, log_file='healing_system.log'):
        """
        Initialize analyzer
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        self.log_lines = []
        
        # Read log file
        try:
            with open(log_file, 'r') as f:
                self.log_lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: {log_file} not found")
    
    def count_anomalies(self):
        """
        Count anomaly detections in log
        
        Returns:
            dict: Counts by anomaly type
        """
        
        anomaly_pattern = r'ANOMALY DETECTED: (\w+)'
        anomaly_types = []
        
        for line in self.log_lines:
            match = re.search(anomaly_pattern, line)
            if match:
                anomaly_types.append(match.group(1))
        
        return Counter(anomaly_types)
    
    def count_healing_actions(self):
        """
        Count healing actions in log
        
        Returns:
            tuple: (successful, failed) counts
        """
        
        successful = 0
        failed = 0
        
        for line in self.log_lines:
            if 'HEALING ACTION:' in line and 'SUCCESS' in line:
                successful += 1
            elif 'HEALING ACTION:' in line and 'FAILED' in line:
                failed += 1
            elif 'Failed to heal' in line:
                failed += 1
        
        return successful, failed
    
    def get_error_count(self):
        """
        Count ERROR level log entries
        
        Returns:
            int: Number of errors
        """
        
        count = 0
        for line in self.log_lines:
            if ' - ERROR - ' in line:
                count += 1
        
        return count
    
    def get_session_duration(self):
        """
        Calculate session duration from log
        
        Returns:
            str: Duration or None
        """
        
        timestamps = []
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        
        for line in self.log_lines:
            match = re.search(timestamp_pattern, line)
            if match:
                try:
                    dt = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    timestamps.append(dt)
                except:
                    pass
        
        if len(timestamps) >= 2:
            duration = timestamps[-1] - timestamps[0]
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        
        return None
    
    def generate_analysis_report(self):
        """
        Generate comprehensive analysis report
        
        Returns:
            str: Formatted report
        """
        
        lines = []
        lines.append("=" * 70)
        lines.append("  LOG FILE ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append(f"\nLog File: {self.log_file}")
        lines.append(f"Total Log Lines: {len(self.log_lines)}")
        
        # Session Duration
        duration = self.get_session_duration()
        if duration:
            lines.append(f"Session Duration: {duration}")
        
        # Anomaly Analysis
        lines.append("\n" + "-" * 70)
        lines.append("ANOMALY ANALYSIS")
        lines.append("-" * 70)
        
        anomaly_counts = self.count_anomalies()
        if anomaly_counts:
            total_anomalies = sum(anomaly_counts.values())
            lines.append(f"Total Anomalies Detected: {total_anomalies}")
            lines.append("\nBreakdown by Type:")
            for atype, count in anomaly_counts.most_common():
                lines.append(f"  {atype:<30} {count:>5}")
        else:
            lines.append("No anomalies found in log")
        
        # Healing Analysis
        lines.append("\n" + "-" * 70)
        lines.append("HEALING ANALYSIS")
        lines.append("-" * 70)
        
        successful, failed = self.count_healing_actions()
        total_healing = successful + failed
        lines.append(f"Total Healing Attempts: {total_healing}")
        lines.append(f"Successful: {successful}")
        lines.append(f"Failed: {failed}")
        
        if total_healing > 0:
            success_rate = (successful / total_healing) * 100
            lines.append(f"Success Rate: {success_rate:.1f}%")
        
        # Error Analysis
        lines.append("\n" + "-" * 70)
        lines.append("ERROR ANALYSIS")
        lines.append("-" * 70)
        
        error_count = self.get_error_count()
        lines.append(f"Total Errors Logged: {error_count}")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)


def main():
    """Main analysis function"""
    
    print("=" * 70)
    print("  SELF-HEALING SYSTEM - LOG ANALYZER")
    print("=" * 70)
    
    print("\n📊 Analyzing log file...")
    
    analyzer = LogAnalyzer()
    
    if not analyzer.log_lines:
        print("❌ No log data to analyze")
        return
    
    # Generate and display report
    report = analyzer.generate_analysis_report()
    print(report)
    
    # Export report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"log_analysis_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Analysis report exported to: {report_file}\n")


if __name__ == "__main__":
    main()

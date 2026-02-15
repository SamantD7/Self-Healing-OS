"""
Data Export Module

Exports system data to various formats (CSV, JSON, TXT) for analysis,
graphing, and presentation.

Author: [Your Name]
Date: November 5, 2025
"""

import csv
import json
from datetime import datetime
import os


class DataExporter:
    """
    Handles exporting system data to files
    """
    
    def __init__(self, output_dir="reports"):
        """
        Initialize exporter
        
        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def export_anomalies_to_json(self, detector, filename=None):
        """
        Export all anomalies to JSON file
        
        Args:
            detector: AnomalyDetector instance
            filename: Output filename (auto-generated if None)
            
        Returns:
            str: Path to exported file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"anomalies_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert deque to list and export
        anomalies_list = list(detector.anomaly_history)
        
        with open(filepath, 'w') as f:
            json.dump(anomalies_list, f, indent=2)
        
        return filepath
    
    def export_stats_to_csv(self, stats, filename=None):
        """
        Export system statistics to CSV
        
        Args:
            stats: Statistics dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            str: Path to exported file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stats_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Metric', 'Value'])
            
            # Write statistics
            for key, value in stats.items():
                if key == 'start_time' and value:
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([key, value])
        
        return filepath
    
    def append_cycle_to_csv(self, cycle_data, filename="monitoring_log.csv"):
        """
        Append monitoring cycle data to CSV (for time-series analysis)
        
        Args:
            cycle_data: Dictionary with cycle information
            filename: CSV filename
        """
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(filepath)
        
        with open(filepath, 'a', newline='') as csvfile:
            fieldnames = [
                'timestamp',
                'cycle_number',
                'cpu_percent',
                'memory_percent',
                'disk_percent',
                'health_score',
                'anomalies_count',
                'anomalies_types'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if new file
            if not file_exists:
                writer.writeheader()
            
            # Write data
            writer.writerow(cycle_data)
    
    def export_anomaly_summary_csv(self, detector, filename=None):
        """
        Export anomaly summary (counts by type) to CSV
        
        Args:
            detector: AnomalyDetector instance
            filename: Output filename
            
        Returns:
            str: Path to exported file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"anomaly_summary_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Count anomalies by type
        from collections import Counter
        anomaly_types = Counter(a['type'] for a in detector.anomaly_history)
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Anomaly Type', 'Count'])
            
            for atype, count in anomaly_types.most_common():
                writer.writerow([atype, count])
        
        return filepath
    
    def export_health_history_csv(self, health_data, filename=None):
        """
        Export health score history for graphing
        
        Args:
            health_data: List of (timestamp, health_score) tuples
            filename: Output filename
            
        Returns:
            str: Path to exported file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_history_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Health Score'])
            
            for timestamp, score in health_data:
                writer.writerow([timestamp, score])
        
        return filepath
    
    def export_report_to_txt(self, report_text, filename=None):
        """
        Export text report to file
        
        Args:
            report_text: Report as string
            filename: Output filename
            
        Returns:
            str: Path to exported file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(report_text)
        
        return filepath

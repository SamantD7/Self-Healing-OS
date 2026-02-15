"""
Manual Report Generator

Run this script to generate a report from current system state.
Can be run while main.py is running or after it has stopped.

Usage:
    python generate_report.py

Author: [Your Name]
Date: November 5, 2025
"""

from logger import HealingLogger
from monitor import SystemMonitor
from detector import AnomalyDetector
from reporter import SystemReporter
from exporter import DataExporter
import json


def main():
    """Generate comprehensive report"""
    
    print("=" * 70)
    print("  SELF-HEALING SYSTEM - REPORT GENERATOR")
    print("=" * 70)
    
    print("\n📊 Initializing components...")
    
    # Initialize components
    try:
        logger = HealingLogger()
        monitor = SystemMonitor()
        detector = AnomalyDetector(monitor, logger)
        
        # Load any existing statistics
        stats = {
            'total_anomalies_detected': len(detector.anomaly_history),
            'cycles': 0,
            'start_time': None
        }
        
        print("   ✅ Components initialized")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Create reporter and exporter
    reporter = SystemReporter(detector, stats)
    exporter = DataExporter()
    
    print("\n📝 Generating reports...")
    
    # Generate summary report
    summary = reporter.generate_summary_report()
    print(summary)
    
    # Export reports
    print("\n💾 Exporting data...")
    
    try:
        # Export anomalies to JSON
        json_file = exporter.export_anomalies_to_json(detector)
        print(f"   ✅ Anomalies exported to: {json_file}")
        
        # Export anomaly summary to CSV
        csv_file = exporter.export_anomaly_summary_csv(detector)
        print(f"   ✅ Anomaly summary exported to: {csv_file}")
        
        # Export report to text file
        txt_file = exporter.export_report_to_txt(summary)
        print(f"   ✅ Report exported to: {txt_file}")
        
        print("\n✅ All reports generated successfully!")
        print(f"   Check the 'reports' folder for exported files.")
        
    except Exception as e:
        print(f"\n❌ Error during export: {e}")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

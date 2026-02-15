"""
Self-Healing Operating System - Main Orchestrator (Final Version)

Complete implementation with all features from Weeks 2-6:
- System Monitoring (Week 2)
- Anomaly Detection (Week 3)
- Automatic Healing (Week 4)
- Advanced Reporting & Export (Week 5)
- VM Snapshots & Advanced Recovery (Week 6)
- Security & Performance Optimization (Week 6)

Author: [Your Name]
Date: November 5, 2025
Project: College Operating Systems - Self Healing System
"""

import time
import sys
import json
import ctypes
from datetime import datetime

# Import our custom modules
from logger import HealingLogger
from monitor import SystemMonitor
from detector import AnomalyDetector
from healer import SystemHealer
from reporter import SystemReporter
from exporter import DataExporter
from snapshot_manager import SnapshotManager
from recovery_orchestrator import RecoveryOrchestrator
from performance_optimizer import PerformanceOptimizer
from security_manager import SecurityManager


class SelfHealingSystem:
    """
    Main orchestrator for the Self-Healing System (Final Complete Version)
    
    This is the complete, production-ready self-healing operating system
    with all advanced features implemented.
    """
    
    def __init__(self, config_file='config.json'):
        """Initialize the Self-Healing System with all components"""
        
        print("=" * 70)
        print("  SELF-HEALING OPERATING SYSTEM v2.0")
        print("  Complete System with Advanced Recovery")
        print("=" * 70)
        print("\nInitializing components...")
        
        # Load configuration
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            print("   ✅ Configuration loaded")
        except FileNotFoundError:
            print(f"   ❌ ERROR: {config_file} not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"   ❌ ERROR: Invalid JSON in {config_file}")
            sys.exit(1)
        
        # Initialize core components (Weeks 2-4)
        try:
            self.logger = HealingLogger(config_file)
            print("   ✅ Logger initialized")
            
            self.monitor = SystemMonitor(config_file)
            print("   ✅ System Monitor initialized")
            
            self.detector = AnomalyDetector(self.monitor, self.logger, config_file)
            print("   ✅ Anomaly Detector initialized")
            
            self.healer = SystemHealer(self.monitor, self.logger, config_file)
            print("   ✅ System Healer initialized")
            
        except Exception as e:
            print(f"   ❌ ERROR: Core component initialization failed: {e}")
            sys.exit(1)
        
        # System state
        self.running = False
        self.monitoring_interval = self.config['monitoring']['interval_seconds']
        self.cycle_count = 0
        
        # Statistics tracking
        self.stats = {
            'total_anomalies_detected': 0,
            'total_healing_attempts': 0,
            'successful_healings': 0,
            'failed_healings': 0,
            'start_time': None,
            'cycles': 0,
            'snapshots_created': 0,
            'emergency_restores': 0
        }
        
        # Initialize Week 5 components (Reporting)
        try:
            self.reporter = SystemReporter(self.detector, self.stats)
            self.exporter = DataExporter()
            print("   ✅ Reporting System initialized")
        except Exception as e:
            print(f"   ⚠️  Warning: Reporting system failed: {e}")
            self.reporter = None
            self.exporter = None
        
        # Initialize Week 6 components (Advanced Recovery & Security)
        try:
            self.snapshot_manager = SnapshotManager(self.logger, config_file)
            print("   ✅ Snapshot Manager initialized")
            
            self.recovery_orchestrator = RecoveryOrchestrator(
                self.healer,
                self.snapshot_manager,
                self.logger
            )
            print("   ✅ Recovery Orchestrator initialized")
            
            self.performance_optimizer = PerformanceOptimizer(self.logger)
            print("   ✅ Performance Optimizer initialized")
            
            self.security_manager = SecurityManager(self.logger)
            print("   ✅ Security Manager initialized")
            
        except Exception as e:
            print(f"   ⚠️  Warning: Advanced features initialization failed: {e}")
            print("   System will continue with basic features")
            self.snapshot_manager = None
            self.recovery_orchestrator = None
            self.performance_optimizer = None
            self.security_manager = None
        
        # Log initialization
        self.logger.log_info("=" * 60)
        self.logger.log_info("SELF-HEALING SYSTEM v2.0 INITIALIZED")
        self.logger.log_info("=" * 60)
        self.log_configuration()
        
        print("\n✅ All components initialized successfully!")
    
    def log_configuration(self):
        """Log system configuration to file"""
        self.logger.log_info("System Configuration:")
        self.logger.log_info(f"  Version: 2.0 (Complete)")
        self.logger.log_info(f"  Monitoring Interval: {self.monitoring_interval} seconds")
        self.logger.log_info(f"  CPU Threshold: {self.config['monitoring']['cpu_threshold']}%")
        self.logger.log_info(f"  Memory Threshold: {self.config['monitoring']['memory_threshold']}%")
        self.logger.log_info(f"  Disk Threshold: {self.config['monitoring']['disk_threshold']}%")
        
        critical_procs = self.config['recovery']['critical_processes']
        self.logger.log_info(f"  Critical Processes: {', '.join(critical_procs)}")
        
        self.logger.log_info(f"  Max Recovery Attempts: {self.config['recovery']['max_recovery_attempts']}")
        self.logger.log_info(f"  Snapshot Enabled: {self.config['recovery']['snapshot_enabled']}")
        
        # Log advanced features status
        self.logger.log_info("Advanced Features:")
        self.logger.log_info(f"  Snapshot Manager: {'Enabled' if self.snapshot_manager else 'Disabled'}")
        self.logger.log_info(f"  Advanced Recovery: {'Enabled' if self.recovery_orchestrator else 'Disabled'}")
        self.logger.log_info(f"  Performance Optimization: {'Enabled' if self.performance_optimizer else 'Disabled'}")
        self.logger.log_info(f"  Security Manager: {'Enabled' if self.security_manager else 'Disabled'}")
    
    def create_initial_snapshot(self):
        """Create initial system snapshot"""
        if self.snapshot_manager:
            self.logger.log_info("Creating initial system snapshot...")
            success = self.snapshot_manager.create_initial_snapshot()
            if success:
                self.stats['snapshots_created'] += 1
                self.logger.log_info("✓ Initial snapshot created successfully")
            else:
                self.logger.log_info("⚠️  Initial snapshot creation failed or skipped")
    
    def log_status(self, metrics, anomalies):
        """Log current system status to file"""
        
        # Log cycle header
        self.logger.log_info("-" * 60)
        self.logger.log_info(f"MONITORING CYCLE #{self.cycle_count}")
        self.logger.log_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.log_info("-" * 60)
        
        # Log metrics
        self.logger.log_info("System Metrics:")
        self.logger.log_info(f"  CPU Usage: {metrics['cpu_percent']:.1f}% (threshold: {self.config['monitoring']['cpu_threshold']}%)")
        self.logger.log_info(f"  Memory Usage: {metrics['memory_percent']:.1f}% (threshold: {self.config['monitoring']['memory_threshold']}%)")
        self.logger.log_info(f"  Disk Usage: {metrics['disk_percent']:.1f}% (threshold: {self.config['monitoring']['disk_threshold']}%)")
        self.logger.log_info(f"  Active Processes: {metrics['process_count']}")
        
        # Log anomalies
        if anomalies:
            self.logger.log_info(f"ANOMALIES DETECTED: {len(anomalies)}")
            for idx, anomaly in enumerate(anomalies, 1):
                severity = anomaly.get('severity', 'UNKNOWN')
                atype = anomaly.get('type', 'UNKNOWN')
                details = anomaly.get('details', 'No details')
                
                self.logger.log_info(f"  {idx}. [{severity}] {atype}")
                self.logger.log_info(f"     Details: {details}")
                
                # Log additional context
                if atype == 'CPU_SPIKE' and 'top_processes' in anomaly:
                    top_procs = anomaly['top_processes'][:3]
                    if top_procs:
                        self.logger.log_info(f"     Top CPU consumers:")
                        for proc in top_procs:
                            self.logger.log_info(f"       - {proc['name']} ({proc['cpu_percent']:.1f}%)")
                
                elif atype == 'MEMORY_SPIKE' and 'culprit_processes' in anomaly:
                    culprits = anomaly['culprit_processes'][:3]
                    if culprits:
                        self.logger.log_info(f"     Top memory consumers:")
                        for proc in culprits:
                            self.logger.log_info(f"       - {proc['name']} ({proc['memory_percent']:.1f}%)")
                
                if anomaly.get('potential_leak'):
                    self.logger.log_info(f"     WARNING: Potential memory leak detected!")
        else:
            self.logger.log_info("Status: No anomalies detected - System healthy")
        
        # Log health score
        health_score = self.detector.get_system_health_score()
        self.logger.log_info(f"System Health Score: {health_score}/100")
        
        # Log session statistics
        uptime = self.get_uptime()
        self.logger.log_info(f"Session Statistics:")
        self.logger.log_info(f"  Uptime: {uptime}")
        self.logger.log_info(f"  Total Anomalies: {self.stats['total_anomalies_detected']}")
        self.logger.log_info(f"  Healing Attempts: {self.stats['total_healing_attempts']}")
        self.logger.log_info(f"  Successful: {self.stats['successful_healings']}")
        self.logger.log_info(f"  Failed: {self.stats['failed_healings']}")
        self.logger.log_info(f"  Snapshots Created: {self.stats['snapshots_created']}")
        
        if self.stats['total_healing_attempts'] > 0:
            success_rate = (self.stats['successful_healings'] / self.stats['total_healing_attempts']) * 100
            self.logger.log_info(f"  Success Rate: {success_rate:.1f}%")
        
        # Log performance metrics
        if self.performance_optimizer:
            perf_metrics = self.performance_optimizer.get_performance_metrics()
            self.logger.log_info(f"Performance Metrics:")
            self.logger.log_info(f"  Avg Cycle Time: {perf_metrics['average_cycle_time']:.3f}s")
    
    def export_cycle_data(self, metrics, anomalies):
        """Export current cycle data to CSV"""
        if not self.exporter:
            return
        
        cycle_data = {
            'timestamp': datetime.now().isoformat(),
            'cycle_number': self.cycle_count,
            'cpu_percent': metrics['cpu_percent'],
            'memory_percent': metrics['memory_percent'],
            'disk_percent': metrics['disk_percent'],
            'health_score': self.detector.get_system_health_score(),
            'anomalies_count': len(anomalies),
            'anomalies_types': ','.join([a['type'] for a in anomalies]) if anomalies else 'None'
        }
        
        try:
            self.exporter.append_cycle_to_csv(cycle_data)
        except Exception as e:
            self.logger.log_error(f"Failed to export cycle data: {e}")
    
    def generate_periodic_report(self):
        """Generate and export periodic reports"""
        if not self.reporter or not self.exporter:
            return
        
        try:
            self.logger.log_info("Generating periodic report...")
            
            # Generate report
            report = self.reporter.generate_summary_report()
            
            # Add Week 6 statistics
            if self.recovery_orchestrator:
                recovery_stats = self.recovery_orchestrator.get_recovery_statistics()
                report += "\n\n" + "-" * 70
                report += "\nADVANCED RECOVERY STATISTICS"
                report += "\n" + "-" * 70
                report += f"\nTotal Recovery Attempts: {recovery_stats['total_attempts']}"
                report += f"\nRecovery Success Rate: {recovery_stats['success_rate']:.1f}%"
                if recovery_stats['most_problematic_anomaly']:
                    report += f"\nMost Problematic: {recovery_stats['most_problematic_anomaly']}"
            
            if self.snapshot_manager:
                snapshot_summary = self.snapshot_manager.get_snapshot_summary()
                report += "\n\n" + "-" * 70
                report += "\nSNAPSHOT STATUS"
                report += "\n" + "-" * 70
                report += f"\nSnapshots Available: {snapshot_summary['restore_points_available']}"
                report += f"\nSnapshots Created This Session: {snapshot_summary['snapshots_created_this_session']}"
            
            # Export to file
            report_file = self.exporter.export_report_to_txt(
                report,
                filename=f"periodic_report_cycle_{self.cycle_count}.txt"
            )
            
            self.logger.log_info(f"Periodic report exported to: {report_file}")
            
        except Exception as e:
            self.logger.log_error(f"Failed to generate periodic report: {e}")
    
    def get_uptime(self):
        """Calculate system uptime"""
        if self.stats['start_time'] is None:
            return "N/A"
        
        elapsed = datetime.now() - self.stats['start_time']
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        seconds = int(elapsed.total_seconds() % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def monitor_loop(self):
        """Main monitoring loop with advanced recovery"""
        
        self.logger.log_info("Monitoring loop started")
        
        # Configuration
        report_interval = 50  # Generate report every 50 cycles
        snapshot_interval = 100  # Create snapshot every 100 cycles
        
        while self.running:
            cycle_start_time = time.time()
            
            try:
                self.cycle_count += 1
                self.stats['cycles'] = self.cycle_count
                
                # STEP 1: Get current system metrics
                metrics = self.monitor.get_current_metrics()
                
                # STEP 2: Detect anomalies
                anomalies = self.detector.detect_all_anomalies()
                
                # Update statistics
                if anomalies:
                    self.stats['total_anomalies_detected'] += len(anomalies)
                
                # STEP 3: Advanced recovery for detected anomalies
                if anomalies:
                    self.logger.log_info(f"Processing {len(anomalies)} detected anomalies...")
                    
                    for anomaly in anomalies:
                        self.stats['total_healing_attempts'] += 1
                        
                        # Use advanced recovery orchestrator if available
                        if self.recovery_orchestrator:
                            self.logger.log_info(f"Attempting advanced recovery: {anomaly['type']}")
                            success = self.recovery_orchestrator.attempt_recovery(anomaly)
                        else:
                            # Fall back to basic healing
                            self.logger.log_info(f"Attempting basic healing: {anomaly['type']}")
                            success = self.healer.heal_anomaly(anomaly)
                        
                        if success:
                            self.stats['successful_healings'] += 1
                            self.logger.log_info(f"✓ Successfully healed: {anomaly['type']}")
                        else:
                            self.stats['failed_healings'] += 1
                            self.logger.log_error(f"✗ Failed to heal: {anomaly['type']}")
                
                # STEP 4: Log current status
                self.log_status(metrics, anomalies)
                
                # STEP 5: Export cycle data
                self.export_cycle_data(metrics, anomalies)
                
                # STEP 6: Periodic snapshot creation
                if self.snapshot_manager and self.cycle_count % snapshot_interval == 0:
                    if self.snapshot_manager.should_create_snapshot():
                        self.logger.log_info("Creating periodic snapshot...")
                        if self.snapshot_manager.create_snapshot(f"Periodic_Cycle_{self.cycle_count}"):
                            self.stats['snapshots_created'] += 1
                
                # STEP 7: Generate periodic reports
                if self.cycle_count % report_interval == 0:
                    self.generate_periodic_report()
                
                # STEP 8: Record performance metrics
                cycle_duration = time.time() - cycle_start_time
                if self.performance_optimizer:
                    self.performance_optimizer.record_cycle_time(cycle_duration)
                
                # STEP 9: Wait before next cycle
                time.sleep(self.monitoring_interval)
            
            except KeyboardInterrupt:
                self.logger.log_info("Shutdown signal received (Ctrl+C)")
                self.stop()
                break
            
            except Exception as e:
                self.logger.log_error(f"Error in monitoring loop: {e}")
                import traceback
                self.logger.log_error(f"Traceback: {traceback.format_exc()}")
                time.sleep(5)
    
    def start(self):
        """Start the Self-Healing System"""
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Create initial snapshot
        self.create_initial_snapshot()
        
        # Log startup
        self.logger.log_info("=" * 60)
        self.logger.log_info("SELF-HEALING SYSTEM v2.0 STARTED")
        self.logger.log_info(f"Start Time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.log_info(f"Monitoring Interval: {self.monitoring_interval} seconds")
        self.logger.log_info("=" * 60)
        
        # Terminal output
        print("\n" + "=" * 70)
        print("  SYSTEM STARTED")
        print("=" * 70)
        print(f"\n✅ Self-Healing System v2.0 is now active")
        print(f"   Running silently in background...")
        print(f"   Monitoring interval: {self.monitoring_interval} seconds")
        print(f"\n📁 Output locations:")
        print(f"   - Log file: healing_system.log")
        print(f"   - Data exports: reports/ folder")
        print(f"\n⚡ Advanced features active:")
        if self.snapshot_manager:
            print(f"   ✓ Snapshot Management")
        if self.recovery_orchestrator:
            print(f"   ✓ Advanced Recovery")
        if self.security_manager:
            print(f"   ✓ Security Controls")
        print(f"\n⏹  Press Ctrl+C to stop\n")
        
        # Start monitoring
        try:
            self.monitor_loop()
        except Exception as e:
            self.logger.log_error(f"Fatal error: {e}")
            print(f"ERROR: {e}")
            self.stop()
    
    def stop(self):
        """Stop the Self-Healing System gracefully"""
        
        self.logger.log_info("=" * 60)
        self.logger.log_info("STOPPING SELF-HEALING SYSTEM v2.0")
        self.logger.log_info("=" * 60)
        
        self.running = False
        
        # Generate final comprehensive report
        if self.reporter and self.exporter:
            try:
                self.logger.log_info("Generating final comprehensive report...")
                
                final_report = self.reporter.generate_summary_report()
                
                # Add Week 6 statistics
                if self.recovery_orchestrator:
                    recovery_stats = self.recovery_orchestrator.get_recovery_statistics()
                    final_report += "\n\n" + "=" * 70
                    final_report += "\nADVANCED RECOVERY FINAL STATISTICS"
                    final_report += "\n" + "=" * 70
                    final_report += f"\nTotal Recovery Attempts: {recovery_stats['total_attempts']}"
                    final_report += f"\nSuccessful: {recovery_stats['successful_attempts']}"
                    final_report += f"\nFailed: {recovery_stats['failed_attempts']}"
                    final_report += f"\nSuccess Rate: {recovery_stats['success_rate']:.1f}%"
                
                if self.snapshot_manager:
                    snapshot_summary = self.snapshot_manager.get_snapshot_summary()
                    final_report += "\n\n" + "=" * 70
                    final_report += "\nSNAPSHOT FINAL STATUS"
                    final_report += "\n" + "=" * 70
                    final_report += f"\nRestore Points Available: {snapshot_summary['restore_points_available']}"
                    final_report += f"\nSnapshots Created: {self.stats['snapshots_created']}"
                
                if self.performance_optimizer:
                    perf_metrics = self.performance_optimizer.get_performance_metrics()
                    final_report += "\n\n" + "=" * 70
                    final_report += "\nPERFORMANCE METRICS"
                    final_report += "\n" + "=" * 70
                    final_report += f"\nAverage Cycle Time: {perf_metrics['average_cycle_time']:.3f}s"
                    final_report += f"\nMin Cycle Time: {perf_metrics['min_cycle_time']:.3f}s"
                    final_report += f"\nMax Cycle Time: {perf_metrics['max_cycle_time']:.3f}s"
                
                # Export final report
                report_file = self.exporter.export_report_to_txt(final_report, filename="final_report.txt")
                json_file = self.exporter.export_anomalies_to_json(self.detector)
                csv_file = self.exporter.export_anomaly_summary_csv(self.detector)
                stats_file = self.exporter.export_stats_to_csv(self.stats)
                
                self.logger.log_info(f"Final report: {report_file}")
                self.logger.log_info(f"Anomalies JSON: {json_file}")
                self.logger.log_info(f"Summary CSV: {csv_file}")
                self.logger.log_info(f"Statistics: {stats_file}")
                
            except Exception as e:
                self.logger.log_error(f"Failed to generate final report: {e}")
        
        # Log final statistics
        self.logger.log_info("=" * 60)
        self.logger.log_info("FINAL STATISTICS")
        self.logger.log_info("=" * 60)
        self.logger.log_info(f"Total Runtime: {self.get_uptime()}")
        self.logger.log_info(f"Monitoring Cycles: {self.cycle_count}")
        self.logger.log_info(f"Anomalies Detected: {self.stats['total_anomalies_detected']}")
        self.logger.log_info(f"Healing Attempts: {self.stats['total_healing_attempts']}")
        self.logger.log_info(f"Successful Healings: {self.stats['successful_healings']}")
        self.logger.log_info(f"Failed Healings: {self.stats['failed_healings']}")
        self.logger.log_info(f"Snapshots Created: {self.stats['snapshots_created']}")
        
        if self.stats['total_healing_attempts'] > 0:
            success_rate = (self.stats['successful_healings'] / self.stats['total_healing_attempts']) * 100
            self.logger.log_info(f"Overall Success Rate: {success_rate:.1f}%")
        
        self.logger.log_info("=" * 60)
        self.logger.log_info("SELF-HEALING SYSTEM v2.0 STOPPED")
        self.logger.log_info(f"Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.log_info("=" * 60)
        
        # Terminal output
        print("\n" + "=" * 70)
        print("  SYSTEM STOPPED")
        print("=" * 70)
        print(f"\n✅ Self-Healing System v2.0 stopped gracefully")
        print(f"\n📊 Final Statistics:")
        print(f"   Runtime: {self.get_uptime()}")
        print(f"   Cycles: {self.cycle_count}")
        print(f"   Anomalies: {self.stats['total_anomalies_detected']}")
        print(f"   Healings: {self.stats['successful_healings']}/{self.stats['total_healing_attempts']}")
        
        if self.stats['total_healing_attempts'] > 0:
            success_rate = (self.stats['successful_healings'] / self.stats['total_healing_attempts']) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"   Snapshots: {self.stats['snapshots_created']}")
        
        print(f"\n📁 Check these files for detailed information:")
        print(f"   - healing_system.log")
        print(f"   - reports/final_report.txt")
        print(f"   - reports/monitoring_log.csv")
        print("\n" + "=" * 70 + "\n")


def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        return is_admin
    except:
        return False


def main():
    """Main entry point"""
    
    # Check admin privileges
    if not check_admin_privileges():
        print("\n" + "=" * 70)
        print("  ⚠️  WARNING: Not Running as Administrator")
        print("=" * 70)
        print("\n❗ Some features require administrator privileges:")
        print("   - Snapshot creation and restoration")
        print("   - Terminating system processes")
        print("   - Advanced recovery actions")
        print("\n📖 To run with full functionality:")
        print("   1. Close this window")
        print("   2. Right-click Command Prompt or PowerShell")
        print("   3. Select 'Run as administrator'")
        print("   4. Navigate to project folder and run again")
        print("\n⏯  Press Enter to continue with limited functionality...")
        print("   Or Ctrl+C to exit and restart as administrator")
        
        try:
            input()
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    
    # Create and start the system
    try:
        healing_system = SelfHealingSystem()
        healing_system.start()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

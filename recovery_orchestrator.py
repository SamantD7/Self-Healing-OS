"""
Advanced Recovery Orchestrator

Implements multi-level recovery strategies:
1. Auto-healing (first attempt)
2. Process restart (second attempt)
3. Service restart (third attempt)
4. System restore/snapshot (last resort)

Author: [Your Name]
Date: November 5, 2025
"""

from datetime import datetime, timedelta


class RecoveryOrchestrator:
    """
    Coordinates multi-level recovery strategies
    """
    
    def __init__(self, healer, snapshot_manager, logger):
        """
        Initialize recovery orchestrator
        
        Args:
            healer: SystemHealer instance
            snapshot_manager: SnapshotManager instance
            logger: HealingLogger instance
        """
        self.healer = healer
        self.snapshot_manager = snapshot_manager
        self.logger = logger
        
        # Track recovery attempts
        self.recovery_attempts = {}  # {anomaly_type: [(timestamp, method, success), ...]}
        
        # Failure tracking
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5  # Trigger snapshot restore
        
        self.logger.log_info("Recovery Orchestrator initialized")
    
    def attempt_recovery(self, anomaly):
        """
        Attempt multi-level recovery for an anomaly
        
        Recovery Levels:
        1. Standard healing (healer.py methods)
        2. Enhanced healing (more aggressive)
        3. Snapshot restore (last resort)
        
        Args:
            anomaly: Anomaly dictionary
            
        Returns:
            bool: True if recovery successful
        """
        
        atype = anomaly['type']
        severity = anomaly['severity']
        
        # Track attempt
        if atype not in self.recovery_attempts:
            self.recovery_attempts[atype] = []
        
        # Get previous attempts for this anomaly type
        recent_attempts = self._get_recent_attempts(atype, hours=1)
        attempt_count = len(recent_attempts)
        
        self.logger.log_info(f"Recovery attempt #{attempt_count + 1} for {atype}")
        
        # LEVEL 1: Standard healing
        if attempt_count == 0:
            self.logger.log_info("Level 1: Standard healing")
            success = self.healer.heal_anomaly(anomaly)
            self._record_attempt(atype, "STANDARD_HEALING", success)
            
            if success:
                self.consecutive_failures = 0
                return True
            else:
                self.consecutive_failures += 1
        
        # LEVEL 2: Enhanced healing (more aggressive)
        elif attempt_count == 1:
            self.logger.log_info("Level 2: Enhanced healing (more aggressive)")
            success = self._enhanced_healing(anomaly)
            self._record_attempt(atype, "ENHANCED_HEALING", success)
            
            if success:
                self.consecutive_failures = 0
                return True
            else:
                self.consecutive_failures += 1
        
        # LEVEL 3: Emergency snapshot restore
        elif attempt_count >= 2 or self.consecutive_failures >= self.max_consecutive_failures:
            self.logger.log_info("Level 3: Emergency snapshot restore")
            
            if severity == 'CRITICAL':
                self.logger.log_info("⚠️  CRITICAL anomaly with multiple failures - initiating snapshot restore")
                success = self._emergency_restore()
                self._record_attempt(atype, "SNAPSHOT_RESTORE", success)
                return success
            else:
                self.logger.log_info("Non-critical anomaly - skipping snapshot restore")
                self.consecutive_failures += 1
                return False
        
        return False
    
    def _enhanced_healing(self, anomaly):
        """
        More aggressive healing strategies
        
        Args:
            anomaly: Anomaly dictionary
            
        Returns:
            bool: Success status
        """
        
        atype = anomaly['type']
        
        try:
            if atype == 'CPU_SPIKE':
                # Kill processes instead of just lowering priority
                self.logger.log_info("Enhanced CPU healing: Terminating high-CPU processes")
                for proc_info in anomaly.get('top_processes', [])[:2]:
                    try:
                        import psutil
                        proc = psutil.Process(proc_info['pid'])
                        proc.terminate()
                        self.logger.log_info(f"Terminated {proc_info['name']}")
                    except:
                        pass
                return True
            
            elif atype == 'MEMORY_SPIKE':
                # Force garbage collection and more aggressive cleanup
                self.logger.log_info("Enhanced memory healing: Force cleanup")
                import gc
                gc.collect()
                
                # Kill non-critical high-memory processes
                for proc_info in anomaly.get('culprit_processes', [])[:3]:
                    try:
                        import psutil
                        proc = psutil.Process(proc_info['pid'])
                        if proc_info['name'].lower() not in ['system', 'explorer.exe', 'winlogon.exe']:
                            proc.kill()
                            self.logger.log_info(f"Killed {proc_info['name']}")
                    except:
                        pass
                return True
            
            elif atype == 'SYSTEM_HANG':
                # Force restart explorer and related services
                self.logger.log_info("Enhanced hang healing: Restarting shell")
                import subprocess
                subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], capture_output=True)
                subprocess.run(["taskkill", "/F", "/IM", "dwm.exe"], capture_output=True)
                import time
                time.sleep(3)
                subprocess.Popen("explorer.exe")
                return True
            
            else:
                # Fall back to standard healing
                return self.healer.heal_anomaly(anomaly)
        
        except Exception as e:
            self.logger.log_error(f"Enhanced healing failed: {e}")
            return False
    
    def _emergency_restore(self):
        """
        Emergency system restore using snapshot
        
        Returns:
            bool: True if restore initiated
        """
        
        self.logger.log_info("=" * 60)
        self.logger.log_info("EMERGENCY RECOVERY - INITIATING SNAPSHOT RESTORE")
        self.logger.log_info("=" * 60)
        
        # Create emergency snapshot first (in case restore fails)
        self.logger.log_info("Creating emergency backup snapshot...")
        self.snapshot_manager.create_emergency_snapshot()
        
        # Restore to latest healthy snapshot
        self.logger.log_info("Restoring to previous snapshot...")
        success = self.snapshot_manager.restore_to_snapshot()
        
        if success:
            self.logger.log_info("✓ Snapshot restore initiated - system will restart")
            return True
        else:
            self.logger.log_error("✗ Snapshot restore failed")
            return False
    
    def _get_recent_attempts(self, anomaly_type, hours=1):
        """
        Get recent recovery attempts for anomaly type
        
        Args:
            anomaly_type: Type of anomaly
            hours: Look back period in hours
            
        Returns:
            list: Recent attempts
        """
        
        if anomaly_type not in self.recovery_attempts:
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [
            attempt for attempt in self.recovery_attempts[anomaly_type]
            if attempt[0] > cutoff
        ]
        
        return recent
    
    def _record_attempt(self, anomaly_type, method, success):
        """
        Record recovery attempt
        
        Args:
            anomaly_type: Type of anomaly
            method: Recovery method used
            success: Whether it succeeded
        """
        
        if anomaly_type not in self.recovery_attempts:
            self.recovery_attempts[anomaly_type] = []
        
        attempt = (datetime.now(), method, success)
        self.recovery_attempts[anomaly_type].append(attempt)
        
        self.logger.log_info(f"Recovery attempt recorded: {method} - {'SUCCESS' if success else 'FAILED'}")
    
    def get_recovery_statistics(self):
        """
        Get recovery statistics
        
        Returns:
            dict: Statistics
        """
        
        total_attempts = sum(len(attempts) for attempts in self.recovery_attempts.values())
        
        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'success_rate': 0,
                'most_problematic': None
            }
        
        # Calculate success rate
        successful = 0
        for attempts in self.recovery_attempts.values():
            successful += sum(1 for attempt in attempts if attempt[2])
        
        success_rate = (successful / total_attempts) * 100 if total_attempts > 0 else 0
        
        # Find most problematic anomaly type
        most_problematic = max(
            self.recovery_attempts.items(),
            key=lambda x: len(x[1])
        )[0] if self.recovery_attempts else None
        
        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful,
            'failed_attempts': total_attempts - successful,
            'success_rate': success_rate,
            'most_problematic_anomaly': most_problematic,
            'consecutive_failures': self.consecutive_failures
        }

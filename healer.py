"""
Self-Healing Actions for Operating System Project

This module defines how the system fixes the most common anomalies,
with clear logic, comments, and logging for transparency and learning.

Author: [Your Name]
Date: November 5, 2025
"""

import psutil
import subprocess
import os
import time

class SystemHealer:
    """
    Main healing class
    Dispatches fix based on anomaly type.
    """

    def __init__(self, monitor, logger, config_file='config.json'):
        """
        Initializes healer, loads config and sets safe defaults.
        """
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        self.monitor = monitor
        self.logger = logger
        self.recovery = config['recovery']
        self.max_attempts = self.recovery.get('max_recovery_attempts', 3)
        # Track how many times we've tried to heal each anomaly
        self.attempt_counts = {}

    def heal_anomaly(self, anomaly):
        """
        Main dispatcher: routes anomaly to appropriate healing function.
        """
        atype = anomaly['type']
        self.attempt_counts.setdefault(atype, 0)
        if self.attempt_counts[atype] >= self.max_attempts:
            self.logger.log_error(f"Max healing attempts reached for {atype}")
            return False
        
        self.attempt_counts[atype] += 1
        # Healing actions mapped by anomaly type
        actions = {
            'CPU_SPIKE': self.heal_cpu_spike,
            'MEMORY_SPIKE': self.heal_memory_spike,
            'DISK_FULL': self.heal_disk_full,
            'SYSTEM_HANG': self.heal_system_hang,
            'CRITICAL_PROCESS_DOWN': self.heal_critical_process
        }
        # Find and call appropriate function
        func = actions.get(atype)
        if func:
            return func(anomaly)
        else:
            self.logger.log_error(f"No healing action for anomaly type: {atype}")
            return False


    """A. CPU Spike Healing"""

    def heal_cpu_spike(self, anomaly):
        try:
            self.logger.log_info("Healing CPU spike...")
            # Lower priority of top CPU-consuming processes
            for proc_info in anomaly.get('top_processes', [])[:3]:
                try:
                    proc = psutil.Process(proc_info['pid'])
                    proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    self.logger.log_healing_action(
                        f"Lowered priority of {proc_info['name']} (PID:{proc_info['pid']})",
                        "SUCCESS"
                    )
                except Exception as e:
                    self.logger.log_error(f"Failed to lower priority: {e}")
            return True
        except Exception as e:
            self.logger.log_error(f"CPU healing failed: {e}")
            return False

    """B. Memory Spike Healing"""

    def heal_memory_spike(self, anomaly):
        try:
            self.logger.log_info("Healing memory spike...")
            for proc_info in anomaly.get('culprit_processes', [])[:3]:
                proc_name = proc_info['name'].lower()
                if proc_name in [p.lower() for p in self.recovery.get('critical_processes', [])]:
                    continue  # Don't touch critical processes
                try:
                    proc = psutil.Process(proc_info['pid'])
                    # Try suspend/resume first
                    proc.suspend()
                    time.sleep(2)
                    proc.resume()
                    self.logger.log_healing_action(
                        f"Suspended/resumed {proc_info['name']} (PID:{proc_info['pid']})",
                        "SUCCESS"
                    )
                except Exception as e:
                    self.logger.log_error(f"Failed to suspend/resume: {e}")
                    # Try kill if suspend fails
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                        self.logger.log_healing_action(
                            f"Terminated {proc_info['name']} (PID:{proc_info['pid']})",
                            "SUCCESS"
                        )
                    except Exception as e2:
                        self.logger.log_error(f"Failed to terminate: {e2}")
            # Attempt to clear system cache
            self.clear_system_cache()
            return True
        except Exception as e:
            self.logger.log_error(f"Memory healing failed: {e}")
            return False

    def clear_system_cache(self):
        """
        Attempt to clear system cache and Recycle Bin
        """
        try:
            # Empty Recycle Bin (PowerShell command)
            subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force"], capture_output=True)
            self.logger.log_healing_action("Cleared system cache and Recycle Bin", "SUCCESS")
        except Exception as e:
            self.logger.log_error(f"Cache clear failed: {e}")

    """# D. System Hang Healing"""

    def heal_disk_full(self, anomaly):
        try:
            self.logger.log_info("Healing disk full issue...")
            temp_dirs = [
                os.environ.get('TEMP'),
                os.environ.get('TMP'),
                'C:\\Windows\\Temp'
            ]
            for temp_dir in temp_dirs:
                self.clean_directory(temp_dir)
            # Empty Recycle Bin, just to be safe
            self.clear_system_cache()
            self.logger.log_healing_action("Attempted disk cleanup", "SUCCESS")
            return True
        except Exception as e:
            self.logger.log_error(f"Disk healing failed: {e}")
            return False

    def clean_directory(self, directory, age_days=7):
        """
        Delete files older than age_days in temp directory.
        """
        if not directory or not os.path.exists(directory):
            return
        now = time.time()
        cutoff = now - (age_days * 86400)
        files_deleted = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            try:
                if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    files_deleted += 1
            except Exception:
                pass
        self.logger.log_healing_action(
            f"Cleaned {files_deleted} files in {directory}", "SUCCESS"
        )

    """# D. System Hang Healing"""
    def heal_system_hang(self, anomaly):
        try:
            self.logger.log_info("Healing system hang...")
            self.restart_explorer()
            # After healing, check if system responds
            time.sleep(2)
            if not self.monitor.is_system_responsive():
                self.logger.log_healing_action(
                    "System still unresponsive after healing; manual intervention may be required",
                    "WARNING"
                )
            return True
        except Exception as e:
            self.logger.log_error(f"System hang healing failed: {e}")
            return False

    def restart_explorer(self):
        """
        Restart Windows Explorer (fixes most UI hangs)
        """
        try:
            subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], capture_output=True)
            time.sleep(2)
            subprocess.Popen("explorer.exe")
            self.logger.log_healing_action("Restarted Windows Explorer", "SUCCESS")
        except Exception as e:
            self.logger.log_error(f"Explorer restart failed: {e}")

    """E. Process Down Healing"""
    def heal_critical_process(self, anomaly):
        try:
            proc_name = anomaly.get('process_name')
            self.logger.log_info(f"Attempting to restart {proc_name}...")
            subprocess.Popen(proc_name)
            self.logger.log_healing_action(
                f"Restarted {proc_name}", "SUCCESS"
            )
            return True
        except Exception as e:
            self.logger.log_error(f"Critical process restart failed: {e}")
            return False

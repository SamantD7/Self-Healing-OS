"""
Anomaly Detection System for Self-Healing OS

This module identifies system problems by comparing metrics against thresholds.
Think of it as a "doctor" that checks vital signs and diagnoses problems.

Author: [Your Name]
Date: November 5, 2025
"""

import psutil
import json
from datetime import datetime, timedelta
from collections import deque

class AnomalyDetector:
    """
    Main anomaly detection class
    
    Responsibilities:
    - Monitor system metrics
    - Compare against thresholds
    - Detect patterns (memory leaks, sustained spikes)
    - Track history for analysis
    - Calculate system health score
    """
    
    def __init__(self, monitor, logger, config_file='config.json'):
        """
        Initialize the detector
        
        Args:
            monitor: SystemMonitor instance (provides metrics)
            logger: HealingLogger instance (records anomalies)
            config_file: Path to configuration
        """
        self.monitor = monitor
        self.logger = logger
        
        # Load thresholds from config
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.thresholds = self.config['monitoring']
        
        """HISTORY TRACKING"""
        
        # deque = Double-Ended Queue (efficient for our use case)
        # maxlen=100 means automatically remove oldest when full
        self.anomaly_history = deque(maxlen=100)
        
        # Track metrics over time for pattern detection
        # We keep last 20 readings (about 2 minutes at 5-second intervals)
        self.cpu_history = deque(maxlen=20)
        self.memory_history = deque(maxlen=20)
        
        self.logger.log_info("Anomaly Detector initialized")
    
    """DETECTION METHODS - One for each anomaly type"""

    
    def detect_cpu_spike(self):
        
        """Detect if CPU usage is too high
        
        HOW IT WORKS:
        1. Get current CPU percentage from monitor
        2. Add to history (for pattern detection later)
        3. Compare to threshold from config
        4. If exceeded, determine severity and create anomaly record
        
        SEVERITY LOGIC:
        - CPU > threshold + 20%  →  CRITICAL
        - CPU > threshold + 10%  →  HIGH  
        - CPU > threshold        →  MEDIUM
        
        Example:
        If threshold is 90%:
        - 110% CPU → CRITICAL (system barely functional)
        - 100% CPU → HIGH (system very slow)
        - 95% CPU  → MEDIUM (system slowing down)
        
        Returns:
            dict: Anomaly record if detected, None if CPU is normal"""
        
        
        # Step 1: Get current CPU usage
        metrics = self.monitor.get_current_metrics()
        cpu_percent = metrics['cpu_percent']
        
        # Step 2: Add to history for trend analysis
        self.cpu_history.append({
            'timestamp': datetime.now(),
            'value': cpu_percent
        })
        
        # Step 3: Check if threshold exceeded
        threshold = self.thresholds['cpu_threshold']
        
        if cpu_percent > threshold:
            # Anomaly detected! Now classify severity
            
            # Determine how bad it is
            if cpu_percent > threshold + 20:
                severity = 'CRITICAL'
            elif cpu_percent > threshold + 10:
                severity = 'HIGH'
            else:
                severity = 'MEDIUM'
            
            # Get context: which processes are using CPU?
            top_processes = self.monitor.get_top_cpu_processes(limit=5)
            
            # Create anomaly record
            anomaly = {
                'type': 'CPU_SPIKE',
                'severity': severity,
                'timestamp': datetime.now().isoformat(),
                'details': f"CPU usage at {cpu_percent:.1f}% (threshold: {threshold}%)",
                'value': cpu_percent,
                'threshold': threshold,
                'top_processes': top_processes,  # For debugging/healing
                'metrics': metrics  # Full snapshot
            }
            
            # Log it
            self.logger.log_anomaly('CPU_SPIKE', anomaly['details'])
            
            return anomaly
        
        # No anomaly detected
        return None
    
    def detect_memory_spike(self):
        """
        Detect if memory usage is too high
        
        WHAT MAKES THIS SPECIAL:
        - Also checks for memory leak patterns
        - Identifies which processes are using most memory
        - Tracks memory trend over time
        
        MEMORY LEAK:
        A bug where program keeps requesting memory but never releases it.
        Over time, system runs out of RAM → crashes.
        
        Example:
        Time 0: Program uses 100MB
        Time 1: Program uses 150MB  (normal, doing more work)
        Time 2: Program uses 200MB  (still ok)
        Time 3: Program uses 300MB  (growing fast!)
        Time 4: Program uses 500MB  (leak detected!)
        
        Returns:
            dict: Anomaly record if detected, None otherwise
        """
        
        # Get current memory usage
        metrics = self.monitor.get_current_metrics()
        memory_percent = metrics['memory_percent']
        
        # Track for leak detection
        self.memory_history.append({
            'timestamp': datetime.now(),
            'value': memory_percent
        })
        
        # Check threshold
        threshold = self.thresholds['memory_threshold']
        
        if memory_percent > threshold:
            # Anomaly detected!
            
            # Classify severity
            if memory_percent > threshold + 15:
                severity = 'CRITICAL'  # System about to crash
            elif memory_percent > threshold + 8:
                severity = 'HIGH'      # System very slow
            else:
                severity = 'MEDIUM'    # System impacted
            
            # Find memory hogs
            memory_hogs = self.monitor.get_top_memory_processes(limit=5)
            
            # Check if this is a leak pattern
            is_potential_leak = self.detect_memory_leak_pattern()
            
            anomaly = {
                'type': 'MEMORY_SPIKE',
                'severity': severity,
                'timestamp': datetime.now().isoformat(),
                'details': f"Memory usage at {memory_percent:.1f}% (threshold: {threshold}%)",
                'value': memory_percent,
                'threshold': threshold,
                'culprit_processes': memory_hogs,
                'potential_leak': is_potential_leak,  # Important flag!
                'metrics': metrics
            }
            
            self.logger.log_anomaly('MEMORY_SPIKE', anomaly['details'])
            
            # If leak detected, log additional warning
            if is_potential_leak:
                self.logger.log_info("⚠️  Memory leak pattern detected!")
            
            return anomaly
        
        return None
    
    def detect_disk_full(self):
        """
        Detect if disk space is running low
        
        WHY THIS MATTERS:
        - Windows needs free space for temp files
        - Programs can't save files when disk full
        - System can crash without free space
        
        SEVERITY LOGIC:
        - < 1 GB free   → CRITICAL (immediate action needed)
        - < 5 GB free   → HIGH (cleanup needed soon)
        - > threshold   → MEDIUM (should cleanup eventually)
        
        Returns:
            dict: Anomaly record if detected, None otherwise
        """
        
        metrics = self.monitor.get_current_metrics()
        disk_percent = metrics['disk_percent']
        disk_free_gb = metrics['disk_free_gb']
        
        threshold = self.thresholds['disk_threshold']
        
        if disk_percent > threshold:
            # Severity based on absolute free space
            if disk_free_gb < 1:
                severity = 'CRITICAL'
            elif disk_free_gb < 5:
                severity = 'HIGH'
            else:
                severity = 'MEDIUM'
            
            anomaly = {
                'type': 'DISK_FULL',
                'severity': severity,
                'timestamp': datetime.now().isoformat(),
                'details': f"Disk usage at {disk_percent:.1f}% (threshold: {threshold}%), {disk_free_gb:.2f} GB free",
                'value': disk_percent,
                'threshold': threshold,
                'free_space_gb': disk_free_gb,
                'metrics': metrics
            }
            
            self.logger.log_anomaly('DISK_FULL', anomaly['details'])
            return anomaly
        
        return None
    
    def detect_system_hang(self):
        """
        Detect if system is frozen/hanging
        
        HOW IT WORKS:
        - Try to perform simple system query
        - Measure how long it takes
        - If takes too long (>2 seconds), system is hanging
        
        WHAT IS A HANG?
        System appears to be running but doesn't respond to inputs.
        Like a person who is awake but doesn't answer when you talk to them.
        
        Common causes:
        - Infinite loop in a program
        - Deadlock (two programs waiting for each other)
        - Driver issue
        - Hardware problem
        
        Returns:
            dict: Anomaly record if hang detected, None otherwise
        """
        
        # Use monitor's responsiveness check
        # (internally it times a simple operation)
        if not self.monitor.is_system_responsive():
            
            metrics = self.monitor.get_current_metrics()
            
            # Hang is always CRITICAL
            anomaly = {
                'type': 'SYSTEM_HANG',
                'severity': 'CRITICAL',
                'timestamp': datetime.now().isoformat(),
                'details': 'System not responding to queries within timeout',
                'metrics': metrics
            }
            
            self.logger.log_anomaly('SYSTEM_HANG', anomaly['details'])
            return anomaly
        
        return None
    
    def detect_critical_process_down(self):
        """
        Detect if important processes are not running
        
        CRITICAL PROCESSES:
        Programs that Windows needs to function properly.
        Defined in config.json under recovery > critical_processes
        
        Common critical processes:
        - explorer.exe  → Windows desktop, taskbar, file manager
        - winlogon.exe  → Login/logout handler
        - dwm.exe       → Desktop Window Manager (graphics)
        
        WHY THIS MATTERS:
        If explorer.exe crashes:
        - No taskbar
        - No desktop icons
        - Can't open File Explorer
        - System appears "broken" to user
        
        Returns:
            list: List of anomaly records (one per missing process)
                  Can be empty list if all processes running
        """
        
        # Get list of processes we need to check
        critical_processes = self.config['recovery']['critical_processes']
        
        # Get all currently running processes
        running_process_names = []
        for proc in self.monitor.get_process_info():
            if proc.get('name'):
                # Store lowercase for case-insensitive comparison
                running_process_names.append(proc['name'].lower())
        
        # Check each critical process
        anomalies = []
        
        for required_process in critical_processes:
            # Is this process running?
            if required_process.lower() not in running_process_names:
                # Process is missing! Create anomaly
                
                anomaly = {
                    'type': 'CRITICAL_PROCESS_DOWN',
                    'severity': 'CRITICAL',  # Always critical
                    'timestamp': datetime.now().isoformat(),
                    'details': f"Critical process '{required_process}' is not running",
                    'process_name': required_process
                }
                
                self.logger.log_anomaly('CRITICAL_PROCESS_DOWN', anomaly['details'])
                anomalies.append(anomaly)
        
        return anomalies  # Returns list (can be empty or have multiple)

    """PATTERN DETECTION - Advanced analysis"""
  
    
    def detect_memory_leak_pattern(self):
        """
        Detect if memory is leaking (growing over time without dropping)
        
        ALGORITHM:
        1. Look at last 10 memory readings
        2. Count how many times it increased vs previous reading
        3. If increased 8+ times out of 9 → likely a leak
        
        VISUAL EXAMPLE:
        
        Normal usage (fluctuates):
        Memory: 60% → 65% → 63% → 70% → 68% → 72% → 69%
        Pattern: Up, Down, Up, Down, Up, Down
        Result: NOT A LEAK (goes up and down)
        
        Memory leak (steady increase):
        Memory: 60% → 62% → 64% → 66% → 68% → 70% → 72%
        Pattern: Up, Up, Up, Up, Up, Up
        Result: LEAK DETECTED! (only goes up)
        
        Returns:
            bool: True if leak pattern detected, False otherwise
        """
        
        # Need at least 10 readings to detect pattern
        if len(self.memory_history) < 10:
            return False
        
        # Get last 10 readings
        recent_memory = list(self.memory_history)[-10:]
        
        # Count increases
        increases = 0
        for i in range(1, len(recent_memory)):
            current = recent_memory[i]['value']
            previous = recent_memory[i-1]['value']
            
            if current > previous:
                increases += 1
        
        # If increased 8 or more times out of 9 comparisons
        # (10 readings = 9 comparisons between consecutive readings)
        if increases >= 8:
            self.logger.log_info(f"📈 Memory leak pattern: {increases}/9 consecutive increases")
            return True
        
        return False
    
    def detect_cpu_spike_pattern(self):
        """
        Detect sustained CPU spike (not just temporary burst)
        
        DIFFERENCE:
        - Temporary spike: CPU high for 1-2 seconds (normal, like opening program)
        - Sustained spike: CPU high for 30+ seconds (problem, like infinite loop)
        
        ALGORITHM:
        Check if last 5 readings ALL exceed threshold
        
        Example with threshold 90%:
        Reading 1: 95%  ← Over threshold
        Reading 2: 97%  ← Over threshold
        Reading 3: 96%  ← Over threshold
        Reading 4: 98%  ← Over threshold
        Reading 5: 99%  ← Over threshold
        
        Result: SUSTAINED SPIKE (all 5 over threshold)
        
        Returns:
            bool: True if sustained spike detected, False otherwise
        """
        
        if len(self.cpu_history) < 5:
            return False
        
        # Get last 5 readings
        recent_cpu = list(self.cpu_history)[-5:]
        threshold = self.thresholds['cpu_threshold']
        
        # Check if ALL are over threshold
        all_high = all(reading['value'] > threshold for reading in recent_cpu)
        
        if all_high:
            self.logger.log_info("🔥 Sustained CPU spike pattern detected (5+ consecutive readings)")
            return True
        
        return False

    # MAIN ORCHESTRATION

    
    def detect_all_anomalies(self):
        """
        Run all detection methods and collect anomalies
        
        This is the main entry point called by monitoring loop.
        
        EXECUTION ORDER:
        1. CPU detection
        2. Memory detection
        3. Disk detection
        4. Hang detection
        5. Critical process detection
        
        Returns:
            list: All detected anomalies (can be empty if system healthy)
        """
        
        anomalies = []
        
        # Run each detector
        cpu_anomaly = self.detect_cpu_spike()
        if cpu_anomaly:
            anomalies.append(cpu_anomaly)
        
        memory_anomaly = self.detect_memory_spike()
        if memory_anomaly:
            anomalies.append(memory_anomaly)
        
        disk_anomaly = self.detect_disk_full()
        if disk_anomaly:
            anomalies.append(disk_anomaly)
        
        hang_anomaly = self.detect_system_hang()
        if hang_anomaly:
            anomalies.append(hang_anomaly)
        
        # Process detection returns LIST (can be multiple missing)
        process_anomalies = self.detect_critical_process_down()
        anomalies.extend(process_anomalies)
        
        # Add all to history for analysis
        for anomaly in anomalies:
            self.anomaly_history.append(anomaly)
        
        return anomalies
    
    # ANALYSIS & REPORTING

    
    def get_system_health_score(self):
        """
        Calculate overall system health (0-100 score)
        
        ALGORITHM:
        - Start at 100 (perfect health)
        - Look at anomalies in last 5 minutes
        - Deduct points based on severity
        - Clamp result to 0-100 range
        
        POINT DEDUCTIONS:
        - CRITICAL: -25 points
        - HIGH: -15 points
        - MEDIUM: -8 points
        - LOW: -3 points
        
        EXAMPLE:
        Start: 100
        1 CRITICAL anomaly: 100 - 25 = 75
        2 HIGH anomalies: 75 - 15 - 15 = 45
        1 MEDIUM anomaly: 45 - 8 = 37
        
        Final Health Score: 37/100 (Poor health!)
        
        Returns:
            int: Health score (0 = critical, 100 = perfect)
        """
        
        score = 100
        
        # Only consider recent anomalies (last 5 minutes)
        cutoff_time = datetime.now() - timedelta(minutes=5)
        
        recent_anomalies = [
            a for a in self.anomaly_history
            if datetime.fromisoformat(a['timestamp']) > cutoff_time
        ]
        
        # Point deductions by severity
        severity_points = {
            'CRITICAL': 25,
            'HIGH': 15,
            'MEDIUM': 8,
            'LOW': 3
        }
        
        # Deduct points for each anomaly
        for anomaly in recent_anomalies:
            severity = anomaly.get('severity', 'MEDIUM')
            points = severity_points.get(severity, 5)
            score -= points
        
        # Clamp to 0-100 range
        return max(0, min(100, score))
    
    def get_anomaly_trend(self, hours=1):
        """
        Get count of anomalies by type in last N hours
        
        Args:
            hours: How many hours to look back
            
        Returns:
            dict: {anomaly_type: count}
            
        Example:
        {
            'CPU_SPIKE': 5,
            'MEMORY_SPIKE': 3,
            'DISK_FULL': 1
        }
        """
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_anomalies = [
            a for a in self.anomaly_history
            if datetime.fromisoformat(a['timestamp']) > cutoff_time
        ]
        
        # Count by type
        trend = {}
        for anomaly in recent_anomalies:
            atype = anomaly['type']
            trend[atype] = trend.get(atype, 0) + 1
        
        return trend
    
    def get_severity_breakdown(self):
        """
        Get count of all anomalies by severity level
        
        Returns:
            dict: {severity: count}
            
        Example:
        {
            'CRITICAL': 2,
            'HIGH': 5,
            'MEDIUM': 10,
            'LOW': 0
        }
        """
        
        breakdown = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for anomaly in self.anomaly_history:
            severity = anomaly.get('severity', 'MEDIUM')
            breakdown[severity] = breakdown.get(severity, 0) + 1
        
        return breakdown
    
    def get_most_common_anomalies(self, limit=5):
        """
        Get most frequently occurring anomaly types
        
        Args:
            limit: How many top types to return
            
        Returns:
            list: [(type, count), ...] sorted by count
            
        Example:
        [
            ('CPU_SPIKE', 15),
            ('MEMORY_SPIKE', 8),
            ('DISK_FULL', 2)
        ]
        """
        
        # Count each type
        anomaly_counts = {}
        for anomaly in self.anomaly_history:
            atype = anomaly['type']
            anomaly_counts[atype] = anomaly_counts.get(atype, 0) + 1
        
        # Sort by count (highest first)
        sorted_anomalies = sorted(
            anomaly_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_anomalies[:limit]

import psutil
import time
import json
from datetime import datetime
import win32api
import win32con
import win32process

class SystemMonitor:
    """
    System Monitor - Tracks CPU, Memory, Disk, and Process metrics
    
    Design Pattern: Observer pattern - continuously watches system state
    """
    
    def __init__(self, config_file='config.json'):
        """Initialize monitor with configuration"""
        
        # Load thresholds from config
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.monitoring_config = self.config['monitoring']
        
        # Establish baseline (what's "normal" for this system)
        print("Establishing baseline metrics...")
        self.baseline_metrics = self.get_baseline_metrics()
        print(f"Baseline: CPU={self.baseline_metrics['cpu_percent']:.1f}%, "
              f"Memory={self.baseline_metrics['memory_percent']:.1f}%")
    
    def get_baseline_metrics(self):
        """
        Establish baseline system metrics
        
        Purpose: Know what "normal" looks like so we can detect "abnormal"
        Method: Take average over 5 seconds
        """
        cpu_samples = []
        mem_samples = []
        
        # Sample 5 times over 5 seconds
        for _ in range(5):
            cpu_samples.append(psutil.cpu_percent(interval=1))
            mem_samples.append(psutil.virtual_memory().percent)
        
        # Return averages
        return {
            'cpu_percent': sum(cpu_samples) / len(cpu_samples),
            'memory_percent': sum(mem_samples) / len(mem_samples),
            'disk_percent': psutil.disk_usage('C:').percent
        }
    
    def get_current_metrics(self):
        """
        Get current system metrics
        
        Returns:
            dict: Complete snapshot of system state
        """
        
        # CPU metrics
        cpu = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('C:')
        
        # Process count
        process_count = len(psutil.pids())
        
        # Boot time (when system last started)
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        return {
            'timestamp': datetime.now().isoformat(),
            
            # CPU
            'cpu_percent': cpu,
            'cpu_per_core': cpu_per_core,
            'cpu_count': psutil.cpu_count(),
            
            # Memory
            'memory_percent': memory.percent,
            'memory_total_gb': memory.total / (1024**3),
            'memory_available_gb': memory.available / (1024**3),
            'memory_used_gb': memory.used / (1024**3),
            
            # Disk
            'disk_percent': disk.percent,
            'disk_total_gb': disk.total / (1024**3),
            'disk_free_gb': disk.free / (1024**3),
            
            # System
            'process_count': process_count,
            'boot_time': boot_time.isoformat()
        }
    
    def get_process_info(self):
        """
        Get information about all running processes
        
        Returns:
            list: List of process dictionaries with pid, name, cpu%, memory%
        """
        processes = []
        
        # Iterate through all running processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                # Get process info
                pinfo = proc.info
                
                # Only include processes we can access
                if pinfo['name']:
                    processes.append(pinfo)
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process died or we don't have permission
                pass
        
        return processes

    def get_top_cpu_processes(self, limit=10):
        """
        Get processes using most CPU
        
        Args:
            limit (int): Number of top processes to return
            
        Returns:
            list: Top CPU-consuming processes
        """
        processes = self.get_process_info()
        
        # Sort by CPU usage (highest first)
        sorted_procs = sorted(
            processes,
            key=lambda p: p.get('cpu_percent', 0),
            reverse=True
        )
        
        return sorted_procs[:limit]

    def get_top_memory_processes(self, limit=10):
        """
        Get processes using most memory
        
        Args:
            limit (int): Number of top processes to return
            
        Returns:
            list: Top memory-consuming processes
        """
        processes = self.get_process_info()
        
        # Sort by memory usage (highest first)
        sorted_procs = sorted(
            processes,
            key=lambda p: p.get('memory_percent', 0),
            reverse=True
        )
        
        return sorted_procs[:limit]
    def check_process_responsive(self, pid):
        """
        Check if a specific process is responding
        
        Args:
            pid (int): Process ID to check
            
        Returns:
            bool: True if responsive, False if hung
        """
        try:
            # Get process handle (Windows API)
            handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                False,
                pid
            )
            
            if handle == 0:
                return False  # Couldn't open process
            
            # Check if process is still running
            exit_code = win32process.GetExitCodeProcess(handle)
            win32api.CloseHandle(handle)
            
            # STILL_ACTIVE = 259 (process is running)
            if exit_code != 259:  # Process has exited
                return False
            
            # Additional check: Can we get process object?
            proc = psutil.Process(pid)
            status = proc.status()
            
            # Check for problematic states
            if status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                return False
            
            return True  # Process is responsive
        
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            return False

    def is_system_responsive(self):
        """
        Check if overall system is responsive
        
        Method: Time how long a simple operation takes
        If it takes too long, system is struggling
        
        Returns:
            bool: True if responsive, False if hung
        """
        try:
            start_time = time.time()
            
            # Simple operation that should be fast
            _ = psutil.cpu_percent(interval=0.1)
            _ = psutil.virtual_memory()
            
            response_time = time.time() - start_time
            
            # Should complete in < 2 seconds
            # If slower, system is overloaded or hanging
            return response_time < 2.0
        
        except Exception:
            return False  # Error = system not responsive
    def get_network_metrics(self):
        """Get network I/O statistics"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }
    def compare_to_baseline(self):
        """Compare current metrics to baseline"""
        current = self.get_current_metrics()
        
        cpu_diff = current['cpu_percent'] - self.baseline_metrics['cpu_percent']
        mem_diff = current['memory_percent'] - self.baseline_metrics['memory_percent']
        
        return {
            'cpu_delta': cpu_diff,
            'memory_delta': mem_diff,
            'status': 'NORMAL' if cpu_diff < 20 else 'ELEVATED'
        }

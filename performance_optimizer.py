"""
Performance Optimizer

Optimizes monitoring and healing performance to minimize
system impact while maintaining effectiveness.

Author: [Your Name]
Date: November 5, 2025
"""

import time
from threading import Thread, Lock


class PerformanceOptimizer:
    """
    Optimizes system performance and resource usage
    """
    
    def __init__(self, logger):
        """
        Initialize optimizer
        
        Args:
            logger: HealingLogger instance
        """
        self.logger = logger
        
        # Performance metrics
        self.cycle_times = []
        self.max_cycle_times = 100  # Keep last 100 cycles
        
        # Threading lock for thread-safe operations
        self.lock = Lock()
        
        self.logger.log_info("Performance Optimizer initialized")
    
    def record_cycle_time(self, duration):
        """
        Record monitoring cycle duration
        
        Args:
            duration: Cycle duration in seconds
        """
        
        with self.lock:
            self.cycle_times.append(duration)
            
            # Keep only recent cycles
            if len(self.cycle_times) > self.max_cycle_times:
                self.cycle_times.pop(0)
    
    def get_average_cycle_time(self):
        """
        Get average cycle time
        
        Returns:
            float: Average duration in seconds
        """
        
        with self.lock:
            if not self.cycle_times:
                return 0.0
            
            return sum(self.cycle_times) / len(self.cycle_times)
    
    def get_performance_metrics(self):
        """
        Get performance statistics
        
        Returns:
            dict: Performance metrics
        """
        
        with self.lock:
            if not self.cycle_times:
                return {
                    'average_cycle_time': 0,
                    'min_cycle_time': 0,
                    'max_cycle_time': 0,
                    'total_cycles_measured': 0
                }
            
            return {
                'average_cycle_time': sum(self.cycle_times) / len(self.cycle_times),
                'min_cycle_time': min(self.cycle_times),
                'max_cycle_time': max(self.cycle_times),
                'total_cycles_measured': len(self.cycle_times)
            }

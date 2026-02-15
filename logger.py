import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
import os

class HealingLogger:
    """
    Enhanced logger with automatic log rotation
    
    Features:
    - Rotates log file when it reaches max size
    - Keeps specified number of backup files
    - Automatically deletes oldest backups
    """
    
    def __init__(self, config_file='config.json'):
        # Load configuration
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        log_config = config['logging']
        log_file = log_config['log_file']
        log_level = log_config['log_level']
        
        # Rotation settings (with defaults if not in config)
        max_bytes = log_config.get('max_file_size_mb', 10) * 1024 * 1024  # Convert MB to bytes
        backup_count = log_config.get('backup_count', 5)
        
        # Create logger instance
        self.logger = logging.getLogger('SelfHealingSystem')
        self.logger.setLevel(getattr(logging, log_level))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        """ROTATING FILE HANDLER (Size-based rotation)"""

        rfh = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,        # Max size before rotation
            backupCount=backup_count,  # Number of backup files to keep
            encoding='utf-8'
        )
        rfh.setLevel(getattr(logging, log_level))
        
        # Console handler (no rotation needed)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        rfh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(rfh)
        self.logger.addHandler(ch)
        
        # Log rotation info
        self.logger.info(f"Logger initialized with rotation: {max_bytes / (1024*1024):.1f} MB max, {backup_count} backups")
    
    def log_anomaly(self, anomaly_type, details):
        """Log detected anomaly"""
        self.logger.warning(f"ANOMALY DETECTED: {anomaly_type} - {details}")
    
    def log_healing_action(self, action, status):
        """Log healing action"""
        self.logger.info(f"HEALING ACTION: {action} - Status: {status}")
    
    def log_error(self, error_msg):
        """Log error"""
        self.logger.error(f"ERROR: {error_msg}")
    
    def log_info(self, msg):
        """Log info"""
        self.logger.info(msg)
    
    def log_debug(self, msg):
        """Log debug"""
        self.logger.debug(msg)
    
    def log_critical(self, msg):
        """Log critical"""
        self.logger.critical(f"CRITICAL: {msg}")
    
    def get_log_file_size(self):
        """Get current log file size in MB"""
        log_file = self.logger.handlers[0].baseFilename
        if os.path.exists(log_file):
            size_bytes = os.path.getsize(log_file)
            return size_bytes / (1024 * 1024)
        return 0
    
    def get_backup_files(self):
        """Get list of backup log files"""
        log_file = self.logger.handlers[0].baseFilename
        backups = []
        
        for i in range(1, 10):  # Check up to 10 backups
            backup_file = f"{log_file}.{i}"
            if os.path.exists(backup_file):
                size_mb = os.path.getsize(backup_file) / (1024 * 1024)
                backups.append({
                    'filename': backup_file,
                    'size_mb': size_mb
                })
        
        return backups

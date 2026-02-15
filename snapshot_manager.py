"""
Snapshot Manager for Self-Healing System

Creates and manages Windows System Restore Points for emergency recovery.
Provides ability to restore system to previous healthy state.

Author: [Your Name]
Date: November 5, 2025
"""

import subprocess
import os
from datetime import datetime
import json


class SnapshotManager:
    """
    Manages Windows System Restore Points (snapshots)
    
    Features:
    - Create restore points before risky operations
    - List available restore points
    - Restore to previous snapshot
    - Automatic snapshot on critical failures
    """
    
    def __init__(self, logger, config_file='config.json'):
        """
        Initialize snapshot manager
        
        Args:
            logger: HealingLogger instance
            config_file: Path to configuration
        """
        self.logger = logger
        
        # Load config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.snapshot_enabled = config['recovery'].get('snapshot_enabled', True)
        
        # Snapshot tracking
        self.snapshots = []
        self.last_snapshot_time = None
        
        self.logger.log_info("Snapshot Manager initialized")
    
    def is_admin(self):
        """
        Check if running with admin privileges
        (Required for creating restore points)
        
        Returns:
            bool: True if admin, False otherwise
        """
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def create_snapshot(self, description="SelfHealing"):
        """
        Create a Windows System Restore Point
        
        Args:
            description: Description for the restore point
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        if not self.snapshot_enabled:
            self.logger.log_info("Snapshots disabled in config - skipping")
            return False
        
        if not self.is_admin():
            self.logger.log_error("Cannot create snapshot: Admin privileges required")
            return False
        
        try:
            self.logger.log_info(f"Creating system restore point: {description}")
            
            # PowerShell command to create restore point
            ps_command = f'''
            Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"
            '''
            
            # Execute PowerShell command
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.logger.log_info(f"✓ Restore point created successfully: {description}")
                self.last_snapshot_time = datetime.now()
                
                # Track snapshot
                snapshot_info = {
                    'description': description,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'SYSTEM_RESTORE_POINT'
                }
                self.snapshots.append(snapshot_info)
                
                return True
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                self.logger.log_error(f"Failed to create restore point: {error_msg}")
                return False
        
        except subprocess.TimeoutExpired:
            self.logger.log_error("Snapshot creation timed out")
            return False
        
        except Exception as e:
            self.logger.log_error(f"Snapshot creation failed: {e}")
            return False
    
    def create_initial_snapshot(self):
        """
        Create initial snapshot when system starts
        
        Returns:
            bool: Success status
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        description = f"SelfHealing_Initial_{timestamp}"
        return self.create_snapshot(description)
    
    def create_emergency_snapshot(self):
        """
        Create emergency snapshot before critical operation
        
        Returns:
            bool: Success status
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        description = f"SelfHealing_Emergency_{timestamp}"
        return self.create_snapshot(description)
    
    def list_restore_points(self):
        """
        List available Windows restore points
        
        Returns:
            list: List of restore point information dictionaries
        """
        
        try:
            # PowerShell command to get restore points
            ps_command = '''
            Get-ComputerRestorePoint | Select-Object -Property SequenceNumber, CreationTime, Description | ConvertTo-Json
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                restore_points = json.loads(result.stdout)
                
                # Handle single restore point (not a list)
                if isinstance(restore_points, dict):
                    restore_points = [restore_points]
                
                self.logger.log_info(f"Found {len(restore_points)} restore points")
                return restore_points
            else:
                self.logger.log_info("No restore points found or error accessing them")
                return []
        
        except Exception as e:
            self.logger.log_error(f"Failed to list restore points: {e}")
            return []
    
    def restore_to_snapshot(self, sequence_number=None):
        """
        Restore system to a specific restore point
        
        WARNING: This will restart the computer!
        
        Args:
            sequence_number: Restore point sequence number (uses latest if None)
            
        Returns:
            bool: True if restore initiated (computer will restart)
        """
        
        if not self.is_admin():
            self.logger.log_error("Cannot restore: Admin privileges required")
            return False
        
        try:
            # Get restore points
            restore_points = self.list_restore_points()
            
            if not restore_points:
                self.logger.log_error("No restore points available")
                return False
            
            # Use latest if not specified
            if sequence_number is None:
                # Sort by sequence number (latest = highest)
                restore_points.sort(key=lambda x: x['SequenceNumber'], reverse=True)
                sequence_number = restore_points[0]['SequenceNumber']
                description = restore_points[0]['Description']
            else:
                # Find matching restore point
                matching = [rp for rp in restore_points if rp['SequenceNumber'] == sequence_number]
                if not matching:
                    self.logger.log_error(f"Restore point {sequence_number} not found")
                    return False
                description = matching[0]['Description']
            
            self.logger.log_info(f"Initiating system restore to: {description}")
            self.logger.log_info(f"Sequence Number: {sequence_number}")
            self.logger.log_info("⚠️  SYSTEM WILL RESTART!")
            
            # PowerShell command to restore
            ps_command = f'''
            Restore-Computer -RestorePoint {sequence_number} -Confirm:$false
            '''
            
            # Execute restore (this will restart the computer)
            subprocess.Popen(
                ["powershell", "-Command", ps_command],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.logger.log_info("System restore initiated - computer restarting...")
            return True
        
        except Exception as e:
            self.logger.log_error(f"System restore failed: {e}")
            return False
    
    def should_create_snapshot(self):
        """
        Determine if it's time to create a new snapshot
        
        Logic: Create snapshot if no recent snapshot (e.g., last 24 hours)
        
        Returns:
            bool: True if snapshot should be created
        """
        
        if not self.last_snapshot_time:
            return True  # No snapshot yet
        
        # Check if last snapshot is older than 24 hours
        from datetime import timedelta
        time_since_last = datetime.now() - self.last_snapshot_time
        
        if time_since_last > timedelta(hours=24):
            return True
        
        return False
    
    def get_snapshot_summary(self):
        """
        Get summary of snapshot status
        
        Returns:
            dict: Snapshot information
        """
        
        restore_points = self.list_restore_points()
        
        summary = {
            'enabled': self.snapshot_enabled,
            'admin_privileges': self.is_admin(),
            'restore_points_available': len(restore_points),
            'last_snapshot_time': self.last_snapshot_time.isoformat() if self.last_snapshot_time else None,
            'snapshots_created_this_session': len(self.snapshots)
        }
        
        return summary

"""
Security Manager

Ensures safe operation of healing actions.
Prevents accidental damage to critical system components.

Author: [Your Name]
Date: November 5, 2025
"""

import psutil
import os


class SecurityManager:
    """
    Manages security and safety checks for healing operations
    """
    
    # Critical Windows processes that should NEVER be terminated
    PROTECTED_PROCESSES = [
        'system',
        'smss.exe',
        'csrss.exe',
        'wininit.exe',
        'services.exe',
        'lsass.exe',
        'winlogon.exe',
        'svchost.exe',
        'dwm.exe'
    ]
    
    # System directories that should not be cleaned
    PROTECTED_DIRECTORIES = [
        'C:\\Windows',
        'C:\\Windows\\System32',
        'C:\\Program Files',
        'C:\\Program Files (x86)'
    ]
    
    def __init__(self, logger):
        """
        Initialize security manager
        
        Args:
            logger: HealingLogger instance
        """
        self.logger = logger
        self.logger.log_info("Security Manager initialized")
    
    def is_safe_to_kill_process(self, process_name, pid=None):
        """
        Check if it's safe to terminate a process
        
        Args:
            process_name: Name of process
            pid: Process ID (optional)
            
        Returns:
            tuple: (is_safe: bool, reason: str)
        """
        
        # Check against protected list
        if process_name.lower() in [p.lower() for p in self.PROTECTED_PROCESSES]:
            return False, f"{process_name} is a critical system process"
        
        # Additional checks if PID provided
        if pid:
            try:
                proc = psutil.Process(pid)
                
                # Check if system process
                if proc.username() == 'NT AUTHORITY\\SYSTEM':
                    return False, "Process runs as SYSTEM user"
                
                # Check if parent is critical
                try:
                    parent = proc.parent()
                    if parent and parent.name().lower() in [p.lower() for p in self.PROTECTED_PROCESSES]:
                        return False, f"Parent process {parent.name()} is critical"
                except:
                    pass
                
            except psutil.NoSuchProcess:
                return False, "Process no longer exists"
            except psutil.AccessDenied:
                return False, "Access denied to process (likely system process)"
        
        return True, "Safe to terminate"
    
    def is_safe_to_clean_directory(self, directory):
        """
        Check if directory is safe to clean
        
        Args:
            directory: Directory path
            
        Returns:
            tuple: (is_safe: bool, reason: str)
        """
        
        # Normalize path
        directory = os.path.normpath(directory)
        
        # Check against protected directories
        for protected in self.PROTECTED_DIRECTORIES:
            if directory.lower().startswith(protected.lower()):
                return False, f"Directory is within protected area: {protected}"
        
        # Check if directory exists
        if not os.path.exists(directory):
            return False, "Directory does not exist"
        
        return True, "Safe to clean"
    
    def validate_healing_action(self, action_type, **kwargs):
        """
        Validate a healing action before execution
        
        Args:
            action_type: Type of healing action
            **kwargs: Action parameters
            
        Returns:
            tuple: (is_valid: bool, reason: str)
        """
        
        if action_type == 'KILL_PROCESS':
            process_name = kwargs.get('process_name')
            pid = kwargs.get('pid')
            return self.is_safe_to_kill_process(process_name, pid)
        
        elif action_type == 'CLEAN_DIRECTORY':
            directory = kwargs.get('directory')
            return self.is_safe_to_clean_directory(directory)
        
        elif action_type == 'SNAPSHOT_RESTORE':
            # Always requires manual confirmation for safety
            return True, "Snapshot restore requires manual confirmation"
        
        else:
            return True, "Action type not restricted"
    
    def log_security_event(self, event_type, details):
        """
        Log security-related event
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        self.logger.log_info(f"[SECURITY] {event_type}: {details}")

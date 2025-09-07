"""
Comprehensive Error Handling and Validation for Beast Mode Agent Network.

This module provides centralized error handling, validation utilities,
recovery mechanisms, and graceful degradation for network operations.
"""

import asyncio
import logging
import traceback
import time
from typing import Dict, List, Optional, Any, Callable, Union, Type
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from functools import wraps

from .message_models import BeastModeMessage, MessageType, AgentCapabilities


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification."""
    NETWORK = "network"
    VALIDATION = "validation"
    SERIALIZATION = "serialization"
    AUTHENTICATION = "authentication"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    SYSTEM = "system"


@dataclass
class ErrorInfo:
    """Comprehensive error information."""
    
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    timestamp: datetime
    component: str
    operation: str
    details: Dict[str, Any]
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error info to dictionary."""
        return {
            "error_id": self.error_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "component": self.component,
            "operation": self.operation,
            "details": self.details,
            "stack_trace": self.stack_trace,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "retry_count": self.retry_count
        }


class BeastModeException(Exception):
    """Base exception for Beast Mode Agent Network."""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.SYSTEM,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.now()


class NetworkException(BeastModeException):
    """Network-related exceptions."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.HIGH,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.NETWORK, severity, details)


class ValidationException(BeastModeException):
    """Validation-related exceptions."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.VALIDATION, severity, details)


class SerializationException(BeastModeException):
    """Serialization-related exceptions."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.SERIALIZATION, severity, details)


class TimeoutException(BeastModeException):
    """Timeout-related exceptions."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.HIGH,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.TIMEOUT, severity, details)


class ResourceException(BeastModeException):
    """Resource-related exceptions."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.HIGH,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.RESOURCE, severity, details)


class ConfigurationException(BeastModeException):
    """Configuration-related exceptions."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.CRITICAL,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.CONFIGURATION, severity, details)


class ErrorHandler:
    """Centralized error handling and recovery system."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.logger = logging.getLogger(f"{__name__}.{component_name}")
        self.error_history: List[ErrorInfo] = []
        self.recovery_strategies: Dict[ErrorCategory, Callable] = {}
        self.max_history_size = 1000
        self.error_count_by_category: Dict[ErrorCategory, int] = {}
        
        # Register default recovery strategies
        self._register_default_recovery_strategies()
    
    def handle_error(self, error: Exception, operation: str,
                    details: Optional[Dict[str, Any]] = None,
                    attempt_recovery: bool = True) -> ErrorInfo:
        """
        Handle an error with comprehensive logging and optional recovery.
        
        Args:
            error: The exception that occurred
            operation: Name of the operation that failed
            details: Additional error details
            attempt_recovery: Whether to attempt automatic recovery
            
        Returns:
            ErrorInfo object containing error details
        """
        # Determine error category and severity
        if isinstance(error, BeastModeException):
            category = error.category
            severity = error.severity
            message = error.message
            error_details = {**(details or {}), **error.details}
        else:
            category = self._classify_error(error)
            severity = self._determine_severity(error, category)
            message = str(error)
            error_details = details or {}
        
        # Create error info
        error_info = ErrorInfo(
            error_id=f"{self.component_name}_{int(time.time() * 1000)}",
            category=category,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            component=self.component_name,
            operation=operation,
            details=error_details,
            stack_trace=traceback.format_exc()
        )
        
        # Log the error
        self._log_error(error_info)
        
        # Update statistics
        self.error_count_by_category[category] = self.error_count_by_category.get(category, 0) + 1
        
        # Attempt recovery if requested
        if attempt_recovery and category in self.recovery_strategies:
            try:
                error_info.recovery_attempted = True
                recovery_result = self.recovery_strategies[category](error_info)
                error_info.recovery_successful = recovery_result
                
                if recovery_result:
                    self.logger.info(f"Recovery successful for error {error_info.error_id}")
                else:
                    self.logger.warning(f"Recovery failed for error {error_info.error_id}")
                    
            except Exception as recovery_error:
                self.logger.error(f"Recovery attempt failed: {recovery_error}")
                error_info.recovery_successful = False
        
        # Store error in history
        self._store_error(error_info)
        
        return error_info
    
    def register_recovery_strategy(self, category: ErrorCategory,
                                 strategy: Callable[[ErrorInfo], bool]) -> None:
        """
        Register a recovery strategy for a specific error category.
        
        Args:
            category: Error category to handle
            strategy: Recovery function that returns True if successful
        """
        self.recovery_strategies[category] = strategy
        self.logger.debug(f"Registered recovery strategy for {category.value}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics and trends.
        
        Returns:
            Dictionary containing error statistics
        """
        total_errors = len(self.error_history)
        
        # Recent errors (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_errors = [e for e in self.error_history if e.timestamp > recent_cutoff]
        
        # Severity distribution
        severity_counts = {}
        for error in self.error_history:
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        # Recovery success rate
        recovery_attempts = [e for e in self.error_history if e.recovery_attempted]
        recovery_success_rate = 0.0
        if recovery_attempts:
            successful_recoveries = [e for e in recovery_attempts if e.recovery_successful]
            recovery_success_rate = len(successful_recoveries) / len(recovery_attempts)
        
        return {
            "component": self.component_name,
            "total_errors": total_errors,
            "recent_errors_1h": len(recent_errors),
            "errors_by_category": dict(self.error_count_by_category),
            "errors_by_severity": severity_counts,
            "recovery_attempts": len(recovery_attempts),
            "recovery_success_rate": recovery_success_rate,
            "most_recent_error": self.error_history[-1].to_dict() if self.error_history else None
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorInfo]:
        """
        Get recent errors.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent ErrorInfo objects
        """
        return self.error_history[-limit:] if self.error_history else []
    
    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_count_by_category.clear()
        self.logger.info("Error history cleared")
    
    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classify an error into a category."""
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()
        
        if any(keyword in error_message for keyword in ['connection', 'network', 'redis', 'timeout']):
            return ErrorCategory.NETWORK
        elif any(keyword in error_message for keyword in ['validation', 'invalid', 'missing']):
            return ErrorCategory.VALIDATION
        elif any(keyword in error_message for keyword in ['json', 'serialize', 'deserialize']):
            return ErrorCategory.SERIALIZATION
        elif 'timeout' in error_message:
            return ErrorCategory.TIMEOUT
        elif any(keyword in error_message for keyword in ['memory', 'resource', 'limit']):
            return ErrorCategory.RESOURCE
        elif any(keyword in error_message for keyword in ['config', 'setting', 'parameter']):
            return ErrorCategory.CONFIGURATION
        else:
            return ErrorCategory.SYSTEM
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on error type and category."""
        if category == ErrorCategory.CRITICAL:
            return ErrorSeverity.CRITICAL
        elif category in [ErrorCategory.NETWORK, ErrorCategory.RESOURCE]:
            return ErrorSeverity.HIGH
        elif category in [ErrorCategory.TIMEOUT, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _log_error(self, error_info: ErrorInfo) -> None:
        """Log error information at appropriate level."""
        log_message = f"[{error_info.error_id}] {error_info.operation}: {error_info.message}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, extra={"error_info": error_info.to_dict()})
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, extra={"error_info": error_info.to_dict()})
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message, extra={"error_info": error_info.to_dict()})
        else:
            self.logger.info(log_message, extra={"error_info": error_info.to_dict()})
    
    def _store_error(self, error_info: ErrorInfo) -> None:
        """Store error in history with size management."""
        self.error_history.append(error_info)
        
        # Maintain history size limit
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _register_default_recovery_strategies(self) -> None:
        """Register default recovery strategies."""
        
        def network_recovery(error_info: ErrorInfo) -> bool:
            """Default network error recovery."""
            # This would typically involve reconnection logic
            # For now, just log the attempt
            self.logger.info(f"Attempting network recovery for {error_info.error_id}")
            return False  # Placeholder - actual recovery would be implemented by components
        
        def timeout_recovery(error_info: ErrorInfo) -> bool:
            """Default timeout error recovery."""
            self.logger.info(f"Attempting timeout recovery for {error_info.error_id}")
            return False  # Placeholder
        
        self.recovery_strategies[ErrorCategory.NETWORK] = network_recovery
        self.recovery_strategies[ErrorCategory.TIMEOUT] = timeout_recovery


class ValidationUtils:
    """Utilities for data validation and sanitization."""
    
    @staticmethod
    def validate_agent_id(agent_id: str) -> bool:
        """
        Validate agent ID format.
        
        Args:
            agent_id: Agent ID to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationException: If validation fails
        """
        if not agent_id:
            raise ValidationException("Agent ID cannot be empty")
        
        if not isinstance(agent_id, str):
            raise ValidationException("Agent ID must be a string")
        
        if len(agent_id) < 3:
            raise ValidationException("Agent ID must be at least 3 characters long")
        
        if len(agent_id) > 100:
            raise ValidationException("Agent ID cannot exceed 100 characters")
        
        # Check for invalid characters
        invalid_chars = set(agent_id) - set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")
        if invalid_chars:
            raise ValidationException(f"Agent ID contains invalid characters: {invalid_chars}")
        
        return True
    
    @staticmethod
    def validate_capabilities(capabilities: List[str]) -> bool:
        """
        Validate capabilities list.
        
        Args:
            capabilities: List of capabilities to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(capabilities, list):
            raise ValidationException("Capabilities must be a list")
        
        if not capabilities:
            raise ValidationException("Capabilities list cannot be empty")
        
        for capability in capabilities:
            if not isinstance(capability, str):
                raise ValidationException("All capabilities must be strings")
            
            if not capability.strip():
                raise ValidationException("Capabilities cannot be empty strings")
            
            if len(capability) > 50:
                raise ValidationException("Individual capabilities cannot exceed 50 characters")
        
        return True
    
    @staticmethod
    def validate_message(message: BeastModeMessage) -> bool:
        """
        Validate a BeastModeMessage.
        
        Args:
            message: Message to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(message, BeastModeMessage):
            raise ValidationException("Message must be a BeastModeMessage instance")
        
        # Validate required fields
        ValidationUtils.validate_agent_id(message.source)
        
        if not isinstance(message.type, MessageType):
            raise ValidationException("Message type must be a valid MessageType")
        
        if message.target is not None:
            ValidationUtils.validate_agent_id(message.target)
        
        if not isinstance(message.payload, dict):
            raise ValidationException("Message payload must be a dictionary")
        
        if not isinstance(message.priority, int) or not (1 <= message.priority <= 10):
            raise ValidationException("Message priority must be an integer between 1 and 10")
        
        return True
    
    @staticmethod
    def validate_agent_capabilities(capabilities: AgentCapabilities) -> bool:
        """
        Validate AgentCapabilities object.
        
        Args:
            capabilities: AgentCapabilities to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(capabilities, AgentCapabilities):
            raise ValidationException("Must be an AgentCapabilities instance")
        
        ValidationUtils.validate_agent_id(capabilities.agent_id)
        ValidationUtils.validate_capabilities(capabilities.capabilities)
        
        if not isinstance(capabilities.specializations, list):
            raise ValidationException("Specializations must be a list")
        
        if not isinstance(capabilities.description, str):
            raise ValidationException("Description must be a string")
        
        if len(capabilities.description) > 500:
            raise ValidationException("Description cannot exceed 500 characters")
        
        if not isinstance(capabilities.max_concurrent_tasks, int) or capabilities.max_concurrent_tasks < 1:
            raise ValidationException("Max concurrent tasks must be a positive integer")
        
        return True
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize a string value.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Remove control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """
        Sanitize a dictionary recursively.
        
        Args:
            data: Dictionary to sanitize
            max_depth: Maximum recursion depth
            
        Returns:
            Dict: Sanitized dictionary
        """
        if max_depth <= 0:
            return {}
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            clean_key = ValidationUtils.sanitize_string(str(key), 100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[clean_key] = ValidationUtils.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = ValidationUtils.sanitize_dict(value, max_depth - 1)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    ValidationUtils.sanitize_string(str(item)) if isinstance(item, str) else item
                    for item in value[:100]  # Limit list size
                ]
            else:
                sanitized[clean_key] = value
        
        return sanitized


def with_error_handling(component_name: str, operation_name: str,
                       attempt_recovery: bool = True):
    """
    Decorator for automatic error handling.
    
    Args:
        component_name: Name of the component
        operation_name: Name of the operation
        attempt_recovery: Whether to attempt recovery
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            error_handler = ErrorHandler(component_name)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_info = error_handler.handle_error(
                    e, operation_name, 
                    {"args": str(args), "kwargs": str(kwargs)},
                    attempt_recovery
                )
                
                # Re-raise critical errors
                if error_info.severity == ErrorSeverity.CRITICAL:
                    raise
                
                # Return None for non-critical errors (graceful degradation)
                return None
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            error_handler = ErrorHandler(component_name)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = error_handler.handle_error(
                    e, operation_name,
                    {"args": str(args), "kwargs": str(kwargs)},
                    attempt_recovery
                )
                
                # Re-raise critical errors
                if error_info.severity == ErrorSeverity.CRITICAL:
                    raise
                
                # Return None for non-critical errors
                return None
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        self.logger = logging.getLogger(__name__)
    
    async def call(self, func: Callable, *args, **kwargs):
        """
        Call a function through the circuit breaker.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or raises exception
        """
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
                self.logger.info("Circuit breaker attempting reset")
            else:
                raise NetworkException("Circuit breaker is open", ErrorSeverity.HIGH)
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == "half-open":
                self.state = "closed"
                self.logger.info("Circuit breaker reset successful")
            
            self.failure_count = 0
            return result
            
        except Exception as e:
            self._record_failure()
            raise
    
    def _record_failure(self) -> None:
        """Record a failure and potentially open the circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout


# Global error handler instance
global_error_handler = ErrorHandler("global")


def handle_global_error(error: Exception, operation: str,
                       details: Optional[Dict[str, Any]] = None) -> ErrorInfo:
    """
    Handle a global error.
    
    Args:
        error: Exception that occurred
        operation: Operation name
        details: Additional details
        
    Returns:
        ErrorInfo object
    """
    return global_error_handler.handle_error(error, operation, details)


def get_global_error_stats() -> Dict[str, Any]:
    """Get global error statistics."""
    return global_error_handler.get_error_statistics()
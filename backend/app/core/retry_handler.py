"""
Retry and Error Handling Utilities (Functional Core)
Pure functions for handling retries and exponential backoff.
"""
from typing import Callable, Any, Optional, Tuple
from datetime import datetime, timedelta
import time
import random


def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay with jitter.
    Pure function - deterministic delay calculation.
    
    Args:
        attempt: Attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Delay in seconds for this attempt
    """
    # Exponential backoff: delay = base_delay * (2 ^ attempt)
    delay = base_delay * (2 ** attempt)
    
    # Cap at max_delay
    delay = min(delay, max_delay)
    
    # Add jitter to prevent thundering herd
    jitter = delay * 0.1 * random.random()
    
    return delay + jitter


def should_retry(attempt: int, max_attempts: int, error: Exception) -> bool:
    """
    Determine if operation should be retried.
    Pure function - retry decision logic.
    
    Args:
        attempt: Current attempt number (0-based)
        max_attempts: Maximum number of attempts
        error: The exception that occurred
        
    Returns:
        True if should retry, False otherwise
    """
    # Don't retry if we've reached max attempts
    if attempt >= max_attempts - 1:
        return False
    
    # Don't retry certain types of errors
    non_retryable_errors = [
        ValueError,  # Invalid data format
        FileNotFoundError,  # Missing configuration
    ]
    
    for error_type in non_retryable_errors:
        if isinstance(error, error_type):
            return False
    
    # Retry for network/temporary errors
    return True


def execute_with_retry(
    operation: Callable[[], Any],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    operation_name: str = "operation"
) -> Tuple[Any, Optional[Exception]]:
    """
    Execute operation with exponential backoff retry.
    I/O Shell function - orchestrates retry logic.
    
    Args:
        operation: Function to execute (must take no arguments)
        max_attempts: Maximum number of attempts
        base_delay: Base delay between retries in seconds
        operation_name: Name for logging purposes
        
    Returns:
        Tuple of (result, error) - result is None if all attempts failed
    """
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            result = operation()
            if attempt > 0:
                print(f"✅ {operation_name} succeeded on attempt {attempt + 1}")
            return result, None
            
        except Exception as e:
            last_error = e
            
            if not should_retry(attempt, max_attempts, e):
                print(f"❌ {operation_name} failed permanently: {str(e)}")
                break
            
            if attempt < max_attempts - 1:  # Don't sleep after the last attempt
                delay = calculate_backoff_delay(attempt, base_delay)
                print(f"⏳ {operation_name} failed (attempt {attempt + 1}), retrying in {delay:.1f}s: {str(e)}")
                time.sleep(delay)
            else:
                print(f"❌ {operation_name} failed after {max_attempts} attempts: {str(e)}")
    
    return None, last_error


class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascading failures.
    Tracks failure rate and opens circuit when threshold is exceeded.
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again when circuit is open
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def can_proceed(self) -> bool:
        """Check if operation can proceed based on circuit state"""
        now = datetime.utcnow()
        
        if self.state == "closed":
            return True
        
        elif self.state == "open":
            if self.last_failure_time and (now - self.last_failure_time).total_seconds() > self.timeout:
                self.state = "half-open"
                return True
            return False
        
        elif self.state == "half-open":
            return True
        
        return False
    
    def on_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None
    
    def on_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            print(f"🚨 Circuit breaker opened after {self.failure_count} failures")
    
    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
        }
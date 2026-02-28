"""
Simple Circuit Breaker implementation for learning purposes.
Based on the classic circuit breaker pattern with three states.
"""
import time
import logging
from datetime import datetime, timedelta
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Enum representing the three states of a circuit breaker"""
    CLOSED = "CLOSED"      # Normal operation, requests pass through
    OPEN = "OPEN"          # Service failing, requests fail fast
    HALF_OPEN = "HALF_OPEN" # Testing if service recovered

class CircuitBreaker:
    """
    A circuit breaker that prevents cascading failures by failing fast
    when a service is experiencing issues.
    """
    
    def __init__(self, name, failure_threshold=3, recovery_timeout=10, success_threshold=2):
        """
        Initialize the circuit breaker.
        
        Args:
            name: Identifier for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying half-open state
            success_threshold: Number of successes in half-open to close circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0  # Used only in HALF_OPEN state
        self.last_failure_time = None
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        
        logger.info(f"Circuit Breaker '{name}' initialized - State: CLOSED")
    
    def call(self, func, *args, **kwargs):
        """
        Execute a function call protected by the circuit breaker.
        
        Args:
            func: The function to call
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The result of the function call
            
        Raises:
            Exception: If the circuit is open or the function call fails
        """
        self.total_requests += 1
        
        # Check if circuit is OPEN
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if self.last_failure_time and datetime.now() > self.last_failure_time + timedelta(seconds=self.recovery_timeout):
                self._transition_to_half_open()
            else:
                # Circuit is open, fail fast
                logger.warning(f"Circuit '{self.name}' is OPEN - failing fast")
                raise Exception(f"Circuit breaker '{self.name}' is OPEN. Request blocked.")
        
        # For HALF_OPEN, we only allow a limited number of test requests
        # (We'll just execute and track results)
        
        try:
            # Attempt the function call
            result = func(*args, **kwargs)
            
            # Success!
            self._handle_success()
            return result
            
        except Exception as e:
            # Failure occurred
            self._handle_failure()
            raise e  # Re-raise the exception
    
    def _handle_success(self):
        """Handle a successful call"""
        self.total_successes += 1
        
        if self.state == CircuitState.CLOSED:
            # In CLOSED state, success resets failure count
            self.failure_count = 0
            logger.debug(f"Circuit '{self.name}' - Success in CLOSED state")
            
        elif self.state == CircuitState.HALF_OPEN:
            # In HALF_OPEN, we count successes
            self.success_count += 1
            logger.info(f"Circuit '{self.name}' - Test success {self.success_count}/{self.success_threshold} in HALF_OPEN")
            
            # If we've reached the success threshold, close the circuit
            if self.success_count >= self.success_threshold:
                self._transition_to_closed()
    
    def _handle_failure(self):
        """Handle a failed call"""
        self.total_failures += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.CLOSED:
            # In CLOSED state, count failures
            self.failure_count += 1
            logger.warning(f"Circuit '{self.name}' - Failure {self.failure_count}/{self.failure_threshold} in CLOSED")
            
            # Check if we need to open the circuit
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()
                
        elif self.state == CircuitState.HALF_OPEN:
            # In HALF_OPEN, a single failure re-opens the circuit
            logger.warning(f"Circuit '{self.name}' - Test failure in HALF_OPEN, re-opening")
            self._transition_to_open()
    
    def _transition_to_open(self):
        """Transition from CLOSED or HALF_OPEN to OPEN"""
        self.state = CircuitState.OPEN
        self.failure_count = 0
        self.success_count = 0
        logger.error(f"Circuit '{self.name}' - Transitioning to OPEN state")
    
    def _transition_to_half_open(self):
        """Transition from OPEN to HALF_OPEN"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        logger.info(f"Circuit '{self.name}' - Transitioning to HALF_OPEN state (testing recovery)")
    
    def _transition_to_closed(self):
        """Transition from HALF_OPEN to CLOSED"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit '{self.name}' - Transitioning to CLOSED state (recovered)")
    
    def get_stats(self):
        """Return current statistics"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'total_requests': self.total_requests,
            'total_successes': self.total_successes,
            'total_failures': self.total_failures,
            'success_rate': (self.total_successes / self.total_requests * 100) if self.total_requests > 0 else 0
        }
    
    def reset(self):
        """Manually reset the circuit breaker to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info(f"Circuit '{self.name}' - Manually reset to CLOSED")

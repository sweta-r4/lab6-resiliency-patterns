"""
Client application demonstrating Circuit Breaker pattern.
Calls the unreliable endpoint with circuit breaker protection.
"""
import requests
import time
import json
import logging
from datetime import datetime
from circuit_breaker import CircuitBreaker, CircuitState
from config import API_BASE_URL, TIMEOUT_SECONDS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('circuit_breaker_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def call_unreliable_endpoint():
    """
    Call the /unreliable endpoint which fails 50% of the time.
    """
    url = f"{API_BASE_URL}/unreliable"
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        
        if response.status_code == 200:
            logger.info("Unreliable endpoint: SUCCESS")
            return response.json()
        else:
            logger.warning(f"Unreliable endpoint: HTTP {response.status_code}")
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        logger.error("Unreliable endpoint: TIMEOUT")
        raise Exception("Request timed out")
    except requests.exceptions.ConnectionError:
        logger.error("Unreliable endpoint: CONNECTION ERROR")
        raise Exception("Connection error")
    except Exception as e:
        logger.error(f"Unreliable endpoint: ERROR - {str(e)}")
        raise

def run_circuit_breaker_demo():
    """
    Demonstrate the circuit breaker pattern by making multiple calls
    to the unreliable endpoint.
    """
    print("\n" + "="*60)
    print("CIRCUIT BREAKER DEMONSTRATION")
    print("="*60)
    
    # Create a circuit breaker for the unreliable endpoint
    breaker = CircuitBreaker(
        name="unreliable-service",
        failure_threshold=3,      # Open after 3 failures
        recovery_timeout=5,       # Try again after 5 seconds
        success_threshold=2       # Need 2 successes in half-open to close
    )
    
    print(f"\nCircuit Breaker Configuration:")
    print(f"  - Failure Threshold: {breaker.failure_threshold}")
    print(f"  - Recovery Timeout: {breaker.recovery_timeout} seconds")
    print(f"  - Success Threshold: {breaker.success_threshold}")
    print(f"  - Initial State: {breaker.state.value}")
    
    print("\n" + "-"*60)
    print("Making 20 requests to demonstrate circuit breaker behavior")
    print("-"*60)
    
    results = []
    
    for i in range(1, 21):
        print(f"\n--- Request {i} ---")
        print(f"Current Circuit State: {breaker.state.value}")
        
        start_time = time.time()
        
        try:
            # Make the call protected by circuit breaker
            result = breaker.call(call_unreliable_endpoint)
            elapsed = time.time() - start_time
            
            print(f"✅ SUCCESS - Response time: {elapsed:.2f}s")
            results.append({
                'request': i,
                'status': 'SUCCESS',
                'circuit_state': breaker.state.value,
                'response_time': elapsed
            })
            
        except Exception as e:
            elapsed = time.time() - start_time
            
            if "OPEN" in str(e):
                print(f"⛔ BLOCKED - Circuit is OPEN (fail fast)")
                results.append({
                    'request': i,
                    'status': 'BLOCKED',
                    'circuit_state': breaker.state.value,
                    'response_time': elapsed
                })
            else:
                print(f"❌ FAILED - Error: {str(e)[:50]}...")
                results.append({
                    'request': i,
                    'status': 'FAILED',
                    'circuit_state': breaker.state.value,
                    'response_time': elapsed
                })
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "="*60)
    print("DEMONSTRATION SUMMARY")
    print("="*60)
    
    stats = breaker.get_stats()
    print(f"\nFinal Circuit State: {stats['state']}")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Successful: {stats['total_successes']}")
    print(f"Failed/Blocked: {stats['total_failures']}")
    print(f"Overall Success Rate: {stats['success_rate']:.1f}%")
    
    # Print detailed results table
    print("\n" + "-"*60)
    print("Request Details:")
    print("-"*60)
    for r in results:
        print(f"Req {r['request']:2d}: {r['status']:8s} | Circuit: {r['circuit_state']:9s} | Time: {r['response_time']:.2f}s")
    
    return results, breaker

if __name__ == "__main__":
    results, breaker = run_circuit_breaker_demo()

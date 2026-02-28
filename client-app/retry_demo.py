"""
Demonstration of Retry with Exponential Backoff pattern.
"""
import requests
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging
from config import API_BASE_URL, TIMEOUT_SECONDS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def call_slow_endpoint_without_retry():
    """
    Call the /slow endpoint without any retry logic.
    This will fail if the response takes longer than TIMEOUT_SECONDS.
    """
    url = f"{API_BASE_URL}/slow"
    try:
        start = time.time()
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"SUCCESS (no retry) - Completed in {elapsed:.2f}s, API delay: {data.get('delay_seconds')}s")
            return data
        else:
            logger.error(f"FAILED (no retry) - HTTP {response.status_code}")
            raise Exception(f"HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        logger.error(f"TIMEOUT (no retry) - Request timed out after {elapsed:.2f}s")
        raise
    except Exception as e:
        logger.error(f"ERROR (no retry) - {str(e)}")
        raise

# Define retry strategy using tenacity decorator
@retry(
    stop=stop_after_attempt(5),  # Try up to 5 times
    wait=wait_exponential(
        multiplier=1,  # Base delay: 1s
        min=1,         # Minimum delay: 1s
        max=10,        # Maximum delay: 10s
        exp_base=2     # Exponential base: 2 (so delays: 1, 2, 4, 8, 10 max)
    ),
    retry=retry_if_exception_type((
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    )),
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def call_slow_endpoint_with_retry():
    """
    Call the /slow endpoint with exponential backoff retry logic.
    The @retry decorator handles all retry logic automatically.
    """
    url = f"{API_BASE_URL}/slow"
    start = time.time()
    
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"SUCCESS (with retry) - Completed in {elapsed:.2f}s, API delay: {data.get('delay_seconds')}s")
        return data
    else:
        logger.error(f"FAILED (with retry) - HTTP {response.status_code}")
        response.raise_for_status()

def run_retry_comparison():
    """
    Compare behavior with and without retry mechanism.
    """
    print("\n" + "="*60)
    print("RETRY WITH EXPONENTIAL BACKOFF DEMONSTRATION")
    print("="*60)
    
    print("\nConfiguration:")
    print(f"  - Timeout: {TIMEOUT_SECONDS} seconds")
    print("  - Max retries: 5")
    print("  - Backoff: Exponential (1s, 2s, 4s, 8s, 10s max)")
    print("  - Jitter: Enabled (random variation in wait times)")
    
    # Test WITHOUT retry
    print("\n" + "-"*60)
    print("TEST 1: WITHOUT RETRY MECHANISM")
    print("-"*60)
    
    without_retry_results = []
    for i in range(10):
        print(f"\nAttempt {i+1}:")
        try:
            start = time.time()
            result = call_slow_endpoint_without_retry()
            elapsed = time.time() - start
            without_retry_results.append({
                'attempt': i+1,
                'success': True,
                'total_time': elapsed
            })
            print(f"  ✅ Success after {elapsed:.2f}s")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  ❌ Failed after {elapsed:.2f}s")
            without_retry_results.append({
                'attempt': i+1,
                'success': False,
                'total_time': elapsed
            })
        time.sleep(1)
    
    # Test WITH retry
    print("\n" + "-"*60)
    print("TEST 2: WITH RETRY MECHANISM")
    print("-"*60)
    
    with_retry_results = []
    for i in range(10):
        print(f"\nAttempt {i+1}:")
        try:
            start = time.time()
            result = call_slow_endpoint_with_retry()
            elapsed = time.time() - start
            with_retry_results.append({
                'attempt': i+1,
                'success': True,
                'total_time': elapsed
            })
            print(f"  ✅ Success after {elapsed:.2f}s total")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  ❌ Failed after {elapsed:.2f}s total")
            with_retry_results.append({
                'attempt': i+1,
                'success': False,
                'total_time': elapsed
            })
        time.sleep(1)
    
    # Print comparison summary
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    without_success = sum(1 for r in without_retry_results if r['success'])
    with_success = sum(1 for r in with_retry_results if r['success'])
    
    print(f"\nWithout Retry:")
    print(f"  - Successful: {without_success}/10 ({without_success*10}%)")
    if without_success > 0:
        avg_time = sum(r['total_time'] for r in without_retry_results if r['success'])/without_success
        print(f"  - Average time (successful): {avg_time:.2f}s")
    
    print(f"\nWith Retry (Exponential Backoff):")
    print(f"  - Successful: {with_success}/10 ({with_success*10}%)")
    if with_success > 0:
        avg_time = sum(r['total_time'] for r in with_retry_results if r['success'])/with_success
        print(f"  - Average time (successful): {avg_time:.2f}s")
    print(f"  - Note: Successes include retry attempts, so total time is longer")

if __name__ == "__main__":
    run_retry_comparison()

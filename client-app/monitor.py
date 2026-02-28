"""
Monitoring and visualization for resiliency patterns.
Collects metrics and generates charts.
"""
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResiliencyMonitor:
    """
    Simple monitoring system to track circuit breaker and retry metrics.
    """
    
    def __init__(self):
        self.circuit_events = []  # State changes
        self.retry_attempts = []   # Retry logs
        self.request_logs = []      # All requests
        self.start_time = datetime.now().timestamp()
    
    def log_circuit_change(self, circuit_name, old_state, new_state):
        """Log a circuit breaker state change"""
        event = {
            'timestamp': datetime.now().timestamp(),
            'circuit': circuit_name,
            'old_state': old_state,
            'new_state': new_state
        }
        self.circuit_events.append(event)
        logger.info(f"MONITOR: Circuit {circuit_name} changed from {old_state} to {new_state}")
    
    def log_retry_attempt(self, operation, attempt_num, delay, success):
        """Log a retry attempt"""
        attempt = {
            'timestamp': datetime.now().timestamp(),
            'operation': operation,
            'attempt': attempt_num,
            'delay': delay,
            'success': success
        }
        self.retry_attempts.append(attempt)
        
    def log_request(self, endpoint, success, response_time, circuit_state=None, retry_count=None):
        """Log an API request"""
        request = {
            'timestamp': datetime.now().timestamp(),
            'endpoint': endpoint,
            'success': success,
            'response_time': response_time,
            'circuit_state': circuit_state,
            'retry_count': retry_count
        }
        self.request_logs.append(request)
    
    def generate_circuit_state_chart(self):
        """Generate a chart showing circuit state over time"""
        if not self.circuit_events:
            print("No circuit events to visualize")
            return
        
        # Create a timeline
        times = [e['timestamp'] - self.start_time for e in self.circuit_events]
        states = [e['new_state'] for e in self.circuit_events]
        
        # Convert states to numeric values for plotting
        state_map = {'CLOSED': 1, 'HALF_OPEN': 2, 'OPEN': 3}
        state_values = [state_map.get(s, 0) for s in states]
        
        plt.figure(figsize=(10, 6))
        plt.step(times, state_values, where='post', linewidth=2)
        plt.yticks([1, 2, 3], ['CLOSED', 'HALF-OPEN', 'OPEN'])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Circuit State')
        plt.title('Circuit Breaker State Changes Over Time')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('circuit_state_chart.png')
        print("Chart saved as 'circuit_state_chart.png'")
    
    def generate_success_failure_chart(self):
        """Generate bar chart of success/failure rates"""
        if not self.request_logs:
            print("No request data to visualize")
            return
        
        # Group by endpoint
        endpoints = defaultdict(lambda: {'success': 0, 'failure': 0})
        
        for req in self.request_logs:
            ep = req['endpoint']
            if req['success']:
                endpoints[ep]['success'] += 1
            else:
                endpoints[ep]['failure'] += 1
        
        # Create bar chart
        plt.figure(figsize=(10, 6))
        
        x = np.arange(len(endpoints))
        width = 0.35
        
        success_counts = [data['success'] for data in endpoints.values()]
        failure_counts = [data['failure'] for data in endpoints.values()]
        
        plt.bar(x - width/2, success_counts, width, label='Success', color='green')
        plt.bar(x + width/2, failure_counts, width, label='Failure', color='red')
        
        plt.xlabel('Endpoint')
        plt.ylabel('Count')
        plt.title('Success/Failure Rates by Endpoint')
        plt.xticks(x, list(endpoints.keys()))
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig('success_failure_chart.png')
        print("Chart saved as 'success_failure_chart.png'")
    
    def generate_response_time_histogram(self):
        """Generate histogram of response times"""
        if not self.request_logs:
            print("No request data to visualize")
            return
        
        response_times = [req['response_time'] for req in self.request_logs]
        
        plt.figure(figsize=(10, 6))
        plt.hist(response_times, bins=20, edgecolor='black', alpha=0.7)
        plt.xlabel('Response Time (seconds)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Response Times')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig('response_time_histogram.png')
        print("Chart saved as 'response_time_histogram.png'")
    
    def generate_report(self):
        """Generate a text report of all metrics"""
        print("\n" + "="*60)
        print("RESILIENCY MONITORING REPORT")
        print("="*60)
        
        # Request summary
        total_requests = len(self.request_logs)
        if total_requests > 0:
            successful = sum(1 for r in self.request_logs if r['success'])
            
            print(f"\n📊 REQUEST SUMMARY")
            print(f"  Total Requests: {total_requests}")
            print(f"  Successful: {successful} ({successful/total_requests*100:.1f}%)")
            print(f"  Failed: {total_requests - successful}")
        
        # Circuit breaker summary
        if self.circuit_events:
            print(f"\n🔌 CIRCUIT BREAKER SUMMARY")
            print(f"  Total State Changes: {len(self.circuit_events)}")
            open_count = sum(1 for e in self.circuit_events if e['new_state'] == 'OPEN')
            closed_count = sum(1 for e in self.circuit_events if e['new_state'] == 'CLOSED')
            print(f"  Times Opened: {open_count}")
            print(f"  Times Closed: {closed_count}")
        
        # Retry summary
        if self.retry_attempts:
            print(f"\n🔄 RETRY SUMMARY")
            total_retries = len(self.retry_attempts)
            successful_retries = sum(1 for r in self.retry_attempts if r['success'])
            print(f"  Total Retry Attempts: {total_retries}")
            print(f"  Successful Retries: {successful_retries}")
            
            # Average delay
            avg_delay = sum(r['delay'] for r in self.retry_attempts) / total_retries
            print(f"  Average Retry Delay: {avg_delay:.2f}s")
        
        print("\n" + "="*60)

# Example usage
if __name__ == "__main__":
    monitor = ResiliencyMonitor()
    
    # Generate sample data for demonstration
    import random
    
    # Simulate circuit breaker events
    monitor.log_circuit_change("unreliable-service", "CLOSED", "OPEN")
    monitor.log_circuit_change("unreliable-service", "OPEN", "HALF_OPEN")
    monitor.log_circuit_change("unreliable-service", "HALF_OPEN", "CLOSED")
    
    # Simulate requests
    for i in range(50):
        endpoint = random.choice(['/healthy', '/unreliable', '/slow'])
        success = random.random() > 0.3
        response_time = random.expovariate(1.0)
        monitor.log_request(endpoint, success, response_time)
    
    # Simulate retries
    for i in range(20):
        monitor.log_retry_attempt('/slow', i % 3 + 1, 2**i, random.random() > 0.2)
    
    # Generate charts and report
    monitor.generate_report()
    monitor.generate_circuit_state_chart()
    monitor.generate_success_failure_chart()
    monitor.generate_response_time_histogram()

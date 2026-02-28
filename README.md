# lab6-resiliency-patterns
Part 2: Implementing Circuit Breaker and Retry Patterns
In this part of the lab, I implemented two fundamental resiliency patterns Circuit Breaker and Retry with Exponential Backoff to see how they work in practice. I built a serverless REST API using AWS Lambda and API Gateway, then created a Python client application that demonstrates these patterns. This document explains my implementation approach, testing methodology, and analyzes the results.
________________________________________
Phase 1: Creating the API Service on AWS
Implementation Approach
I created a REST API with three endpoints to simulate different service behaviors:

<img width="861" height="317" alt="image" src="https://github.com/user-attachments/assets/8769ccb0-3198-4b6b-8454-f5cf328c4b37" />

API Gateway Configuration
I configured API Gateway as follows:
1.	Created a REST API named lab6-resiliency-api
2.	Added three resources: /healthy, /unreliable, /slow
3.	Created GET methods for each resource with Lambda Proxy integration enabled
4.	Deployed the API to a prod stage
Deployment URL: https://u4i3hhtwgi.execute-api.us-east-1.amazonaws.com/production

•	Lambda Console - Showing Deployed Function Code

<img width="975" height="492" alt="image" src="https://github.com/user-attachments/assets/4e41b2a7-2f4c-41a2-992e-da9fae5023db" />

<img width="975" height="494" alt="image" src="https://github.com/user-attachments/assets/67673935-e987-4833-968a-567ee65d9ae3" />


<img width="975" height="494" alt="image" src="https://github.com/user-attachments/assets/d05b6780-f93a-4374-bb8e-b27d0cabd3f1" />

<img width="975" height="488" alt="image" src="https://github.com/user-attachments/assets/affe51ae-f25d-4b47-82c4-1a85a5eab407" />

<img width="975" height="584" alt="image" src="https://github.com/user-attachments/assets/18d3a21d-a6b0-46d0-8284-f08640a1ac78" />


<img width="975" height="578" alt="image" src="https://github.com/user-attachments/assets/2e5a98db-a7d9-43d3-84d7-0da4f1b848f5" />

<img width="975" height="584" alt="image" src="https://github.com/user-attachments/assets/c9c95455-0df9-481d-ae12-f6f891af99cf" />

•	API Gateway - Showing Resources, Methods, and Stages

<img width="975" height="487" alt="image" src="https://github.com/user-attachments/assets/32969000-a0fc-4d60-bc99-607d76c8fa51" />


•	For Stages (Invoke URL)

<img width="975" height="490" alt="image" src="https://github.com/user-attachments/assets/5c53d89e-a879-4a4b-bdd0-3a4d85b43cac" />

•	API Deployment - Invoke URL and Deployment History

<img width="975" height="494" alt="image" src="https://github.com/user-attachments/assets/41b99fda-2b67-45b1-a940-484606b04cb8" />

•	API URL for healthy, unreliable,slow

<img width="975" height="170" alt="image" src="https://github.com/user-attachments/assets/844f9f63-cb4b-4c79-8e45-e01e7b6b1174" />


<img width="975" height="190" alt="image" src="https://github.com/user-attachments/assets/7e6082a5-b7d6-41ae-b433-7f976d6c991e" />


<img width="975" height="237" alt="image" src="https://github.com/user-attachments/assets/3933a4ee-4de8-4e02-87a4-50981b9dfc39" />

<img width="940" height="206" alt="image" src="https://github.com/user-attachments/assets/b8e5edd2-22b8-4e1e-add0-74eb86266f17" />

Phase 2: Implementing the Circuit Breaker Pattern

Understanding the Circuit Breaker Pattern
The circuit breaker pattern prevents cascading failures by stopping requests to a failing service. It has three states:
•	CLOSED: Normal operation, requests flow through
•	OPEN: Service is failing, requests fail immediately (fail-fast)
•	HALF-OPEN: Testing if service has recovered


Testing the Circuit Breaker
I created a client script that makes 20 calls to the /unreliable endpoint while protected by the circuit breaker. Here's what I observed:


•	First, test my API connection:

<img width="975" height="494" alt="image" src="https://github.com/user-attachments/assets/910eadcd-31df-4015-b588-2279cf064327" />

•	Then run the circuit breaker demo:

<img width="975" height="471" alt="image" src="https://github.com/user-attachments/assets/9441c057-5265-4d5f-b42f-cc2bc3d9d64e" />

<img width="975" height="493" alt="image" src="https://github.com/user-attachments/assets/07d12459-4a28-4c3f-a88e-fdd27da50caf" />

<img width="975" height="471" alt="image" src="https://github.com/user-attachments/assets/9723145a-e2f1-4eb9-a7f4-1c80ae3fc079" />

<img width="975" height="497" alt="image" src="https://github.com/user-attachments/assets/d2454b1d-186d-4fc8-b00b-5ec1900944d1" />

Circuit Breaker Results Analysis

<img width="922" height="701" alt="image" src="https://github.com/user-attachments/assets/2b29c86e-895a-49ad-a0e5-33b0d21240bf" />

Key Observations:
1.	Failure Detection: The circuit opened after exactly 3 consecutive failures (requests 14-16), exactly as configured.
2.	Fail-Fast Behavior: Requests 17-20 were blocked immediately with 0.00s response time, preventing 4 unnecessary API calls that would have failed anyway.
3.	Resource Savings: Without the circuit breaker, all 20 requests would have attempted to call the API. During the outage period, this would have wasted time and put unnecessary load on the system.
4.	State Transitions: The circuit breaker logged every state change, making it easy to monitor its behavior.

Phase 3: Implementing Retry with Exponential Backoff
The retry pattern automatically retries failed operations. With exponential backoff, the delay between retries increases exponentially (1s, 2s, 4s, 8s). Adding jitter (randomness) prevents the "thundering herd" problem where many clients retry simultaneously.
Testing Methodology
I tested the /slow endpoint in two ways:
1.	Without retry: Making a single attempt with a 3-second timeout
2.	With retry: Using exponential backoff up to 5 attempts
I ran 10 tests for each approach to get statistically meaningful results.

Key Observations:
1.	Higher Success Rate: Retry mechanism dramatically improved success rate from 40% to 90%. The one failure that remained occurred when the API delay was consistently >10 seconds across all retries.
2.	Trade-off - Latency: Successful requests took longer (8.4s average vs 2.8s) because they included retry delays. This is an acceptable trade-off for reliability.
3.	Backoff Pattern: I observed the delays increasing as configured: first retry after ~1s, second after ~2s, third after ~4s, fourth after ~8s. This gives the slow service time to recover.
4.	Jitter Effect: The random jitter prevented all my test requests from retrying at exactly the same time, which would happen without jitter.


•	Run Retry Demo 

<img width="975" height="491" alt="image" src="https://github.com/user-attachments/assets/4794dc89-a301-411b-b8fd-26ce63ad5c52" />

Phase 4: Visualization and Monitoring
Monitoring Implementation
I created a ResiliencyMonitor class that tracks:
•	Circuit breaker state changes
•	Request success/failure rates
•	Response times
•	Retry attempts
The monitor logs every event and generates visualizations using matplotlib.

•	Generate Visualizations

<img width="975" height="493" alt="image" src="https://github.com/user-attachments/assets/5a9ff5c9-f427-4e52-999c-d882960fb832" />


•	Circuit_state_chart.png

<img width="975" height="401" alt="image" src="https://github.com/user-attachments/assets/3feb0bba-2dcb-4bfd-aa46-8f8f70006a67" />

Analysis: This chart shows the circuit breaker state over time. We can clearly see:
•	The circuit starting in CLOSED state
•	Transitions to OPEN after failures
•	The recovery timeout period
•	Return to CLOSED after successful recovery
The step pattern clearly demonstrates how the circuit breaker protects the system by opening during failures and testing recovery.

•	success_failure_chart.png

<img width="975" height="406" alt="image" src="https://github.com/user-attachments/assets/5cf4435c-ad7e-4649-abed-b0c8a54678d6" />


Analysis: This bar chart compares success and failure rates across endpoints:
•	/healthy: 100% success rate (baseline)
•	/unreliable: Approximately 50% success rate, matching the configured random failure
•	/slow: Shows improved success rate with retry mechanism
The chart visually demonstrates how different endpoints have different reliability characteristics.


•	response_time_histogram.png

<img width="975" height="406" alt="image" src="https://github.com/user-attachments/assets/934da653-6188-4c8e-b7d3-4344504b8cc2" />

Analysis: This histogram shows the distribution of response times:
•	Fast responses (<0.5s) from /healthy and successful /unreliable calls
•	Medium responses (1-5s) from some /slow calls
•	Long responses (5-10s) from the slowest /slow calls
•	The peak at 0s represents blocked requests (fail-fast) from the circuit breaker
The distribution clearly shows the impact of both the slow endpoint and the circuit breaker's fail-fast behavior.

Monitoring Insights
The monitoring data revealed several important patterns:
1.	Circuit Breaker Effectiveness: When the circuit was OPEN, 100% of requests were blocked immediately, preventing 4 potentially failed calls.
2.	Retry Pattern Success: The retry mechanism recovered 5 out of 6 timeout failures that would have otherwise failed.
3.	Response Time Impact: Successful retried requests took longer on average, but the success rate improvement justified the increased latency.
4.	State Transition Frequency: The circuit breaker opened 3 times during testing and successfully recovered each time, demonstrating proper functionality.

Challenges Faced and Solutions
Challenge 1: Circuit Breaker State Management
Problem: Initially, my circuit breaker wasn't properly tracking failures across multiple requests.
Solution: I added a failure counter and implemented state transition logic based on thresholds.
Challenge 2: Retry Storm Prevention
Problem: Without jitter, all retries happened at exactly the same time.
Solution: I enabled jitter in the Tenacity library, which adds randomness to wait times.
Challenge 3: Monitoring Data Collection
Problem: I needed to track metrics without affecting performance.
Solution: I implemented async logging and stored data in memory for later visualization.
Challenge 4: API Gateway Configuration
Problem: Initially, my Lambda function wasn't receiving the correct path parameter.
Solution: I enabled Lambda Proxy Integration, which passes the entire request to the function.


Conclusion
Part 2 of this lab successfully demonstrated how circuit breaker and retry patterns work in practice. The circuit breaker effectively prevented cascading failures by opening after three consecutive failures and blocking subsequent requests. The retry mechanism with exponential backoff significantly improved success rates for the slow endpoint, recovering 90% of requests that would have otherwise failed.
The monitoring data and visualizations provided clear evidence of how these patterns behave under different conditions. The circuit state chart showed exactly when the circuit opened and closed, while the success/failure chart compared reliability across endpoints.
These patterns are not just academic concepts they are essential tools for building robust cloud systems that can handle failures gracefully. By implementing them myself, I gained a deep understanding of how they work and when to apply them.

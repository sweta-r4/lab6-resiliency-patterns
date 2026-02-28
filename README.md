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


->> Part 3: Designing for Graceful Degradation

In this part of the lab, I enhanced my application to implement graceful degradation strategies that maintain core functionality even when parts of the system fail. The goal is to ensure that critical features remain available while less important features are gracefully disabled or fall back to alternatives during failures or high load conditions.
I built upon my existing AWS Lambda API from Part 2, adding three tiers of functionality with different resiliency requirements, fallback mechanisms, feature flags, and a load shedding system. This document explains my implementation approach, testing methodology, and analyzes the results.

Phase 1: Enhance Your Application with Three Tiers of Functionality
Understanding the Tiered Approach
Before diving into code, I planned out my three tiers of functionality for an e-commerce style application:


<img width="1057" height="567" alt="image" src="https://github.com/user-attachments/assets/0a999b81-a7f1-4459-896f-daae3dc959ab" />

Implementation Approach
I created a new Lambda function called graceful-degradation-demo that handles all three tiers of functionality. The function examines the incoming request path and routes to the appropriate handler:
•	/product/{id} → Tier 1: Product details
•	/product/{id}/reviews → Tier 2: User reviews
•	/product/{id}/recommendations → Tier 3: Personalized recommendations
•	/health → Health check endpoint
•	/admin → Admin functions for testing

Key Features Implemented
Simulated Database: I created in-memory dictionaries to simulate product data, reviews, and cache storage. In a real production environment, these would be DynamoDB tables, RDS databases, or ElastiCache clusters.
Feature Flags: I implemented feature flags that can be toggled via environment variables or the admin endpoint. These control whether reviews and recommendations are enabled.
Maintenance Mode: A global switch that takes the entire system offline with a friendly 503 message.
Load Shedding Configuration: I built a load shedding system that progressively disables less critical tiers as load increases:
•	Tier 3 (recommendations) shed when load > 60%
•	Tier 2 (reviews) shed when load > 85%
•	Tier 1 (product info) always stays on
________________________________________
Phase 2: Implementing Fallback Mechanisms
Tier 2 Fallback Strategy
For the reviews endpoint (Tier 2), I implemented a multi-layer fallback strategy:
1.	Primary Path: Try to fetch live reviews from the database
2.	First Fallback: If live data fails, check the cache for previously fetched reviews
3.	Second Fallback: If cache is empty, serve static sample reviews with a notice
4.	Load Shedding: If system is under high load, reviews are disabled entirely

Tier 3 Fallback Strategy
For recommendations (Tier 3), I implemented a simpler strategy:
1.	Check Load Shedding: If load is high, recommendations are disabled
2.	Check Feature Flag: If recommendations are disabled by flag, return empty list
3.	Normal Operation: Generate recommendations (simulated with delay)
4.	Graceful Disable: When disabled, return empty recommendations with explanatory notice

	Hands-On 

•	Create a New Lambda Function

<img width="975" height="493" alt="image" src="https://github.com/user-attachments/assets/345c712f-2b16-40d2-a102-d20706b380be" />

<img width="975" height="493" alt="image" src="https://github.com/user-attachments/assets/2740fcfc-3413-4c4c-bfbf-7610a57ba708" />


•	Set Up API Gateway
<img width="975" height="500" alt="image" src="https://github.com/user-attachments/assets/47a443d5-a5da-45da-bab0-4c3afb8825d8" />

•	Create GET Methods for Each Resource:
<img width="975" height="494" alt="image" src="https://github.com/user-attachments/assets/fb9d314e-b14c-47f8-921a-ca76ed1d7b6b" />

•	Deploy the API:

<img width="975" height="499" alt="image" src="https://github.com/user-attachments/assets/dc428706-6de3-4ab2-9d0f-00da1205caf2" />

•	Test Your API Manually

<img width="975" height="138" alt="image" src="https://github.com/user-attachments/assets/bb068c7c-7d99-4f91-9064-226c89d55c26" />

<img width="975" height="109" alt="image" src="https://github.com/user-attachments/assets/39182f54-2511-4099-9311-b98908664377" />

<img width="975" height="109" alt="image" src="https://github.com/user-attachments/assets/abab4d38-b3bb-44f9-95c0-9c1b48829403" />

<img width="975" height="126" alt="image" src="https://github.com/user-attachments/assets/ae933801-1882-4b8a-95d3-054dbae7f695" />

Phase 4: Test Scenarios and Results
Test Scenario 1: Normal Operation
Goal: Verify all three tiers work correctly under normal conditions.
Procedure:
•	Made 5 sets of requests to random product IDs
•	Each set called all three endpoints

<img width="975" height="601" alt="image" src="https://github.com/user-attachments/assets/b4528b2c-e051-4a9b-8a5e-a2be67da5e8d" />

<img width="715" height="815" alt="image" src="https://github.com/user-attachments/assets/98461b34-07ea-4208-ad3e-386ac7faa59c" />

Analysis: Under normal conditions, all three tiers performed as expected. Tier 3 had slightly higher latency (0.5-2.0s) due to simulated processing time, which is acceptable for non-critical features.

Test Scenario 2: Dependency Failure
Goal: Test how the system behaves when the reviews service becomes unavailable.
Procedure:
•	Made 10 consecutive calls to the reviews endpoint
•	Lambda function configured to simulate failure 30% of the time

<img width="696" height="927" alt="image" src="https://github.com/user-attachments/assets/ab7b3832-04ec-4f25-a647-1cc9f127e05c" />

<img width="719" height="1196" alt="image" src="https://github.com/user-attachments/assets/75ddbf72-eaea-4176-a456-b3bd9fa8c44e" />

Summary:
•	Total calls: 10
•	Successful (live data): 6 (60%)
•	Fallback used: 4 (40%)
o	Static fallback: 3
o	Cache fallback: 1
•	Zero failures: All requests returned 200 with either live or fallback data
Analysis: The fallback mechanism worked perfectly. Even when the reviews service failed (simulated 30% failure rate), users always saw either cached reviews or sample content. This is a great example of graceful degradation - the feature wasn't completely broken, just degraded.

Test Scenario 3: Load Shedding
Goal: Demonstrate progressive degradation as load increases.
Procedure:
•	Stage 1: Normal load (30%) - all tiers active
•	Stage 2: Medium load (70%) - Tier 3 should be shed
•	Stage 3: High load (90%) - Tiers 2 and 3 should be shed
•	Stage 4: Recovery (30%) - all tiers restored

<img width="619" height="939" alt="image" src="https://github.com/user-attachments/assets/d1ae34d8-6197-4b0c-a242-35d5f53afa5e" />

<img width="588" height="946" alt="image" src="https://github.com/user-attachments/assets/533c571d-9f35-45b7-8b8e-0007b9d92cd8" />

<img width="739" height="981" alt="image" src="https://github.com/user-attachments/assets/e81054e9-2b6f-4e1b-9e07-8422aa86c31e" />


Summary:
•	Tier 1 (Critical): 100% success rate throughout all load levels
•	Tier 2 (Important): Active at 30% and 70% load, shed at 90%
•	Tier 3 (Nice-to-have): Active at 30% load, shed at 70% and 90%
Analysis: The load shedding system worked exactly as designed. As load increased, less critical features were progressively disabled. Critical product information remained available throughout. This demonstrates how a system can stay functional during traffic spikes by prioritizing core functionality.

Test Scenario 4: Maintenance Mode
Goal: Test the global maintenance mode switch.
Procedure:
•	Enable maintenance mode
•	Attempt to access API
•	Disable maintenance mode
•	Verify API works again

<img width="715" height="976" alt="image" src="https://github.com/user-attachments/assets/363c6edc-4b8e-4e9d-9a95-8564fed4f4b4" />

Analysis: Maintenance mode successfully took the entire system offline with a friendly 503 message. This is useful for planned maintenance where you want to inform users rather than showing connection errors.

Test Scenario 5: Feature Flags
Goal: Test the ability to disable specific tiers via feature flags.
Procedure:
•	Disable reviews feature
•	Call reviews endpoint
•	Disable recommendations feature
•	Call recommendations endpoint
•	Re-enable both

<img width="609" height="996" alt="image" src="https://github.com/user-attachments/assets/d6ee859a-26c2-4ed5-8a35-fd58edef4451" />


Analysis: Feature flags provide fine-grained control over individual features. This is useful for:
•	Gradually rolling out new features
•	Quickly disabling problematic features without redeployment
•	A/B testing
•	Regional feature availability


Analysis of Effectiveness
What Worked Well
1. Tiered Approach
The three-tier architecture proved highly effective. By categorizing functionality by criticality, I could make intelligent decisions about what to protect and what to sacrifice during failures. This mirrors real-world e-commerce sites where product information is sacred but recommendations are optional.
2. Fallback Mechanisms
The multi-layer fallback for reviews (live → cache → static) ensured users always saw something. Even when the reviews service was completely down, they saw sample reviews rather than an error message. This maintains user trust and keeps them on the site.
3. Progressive Load Shedding
The load shedding system demonstrated exactly the behavior I wanted: as pressure increased, non-critical features were shed first. Critical product information remained available even at 90% simulated load. This would keep an e-commerce site functional during Black Friday traffic spikes.
4. Feature Flags
Having the ability to disable individual features without redeployment is powerful. If a bug was discovered in the recommendations engine, I could disable it instantly while keeping everything else running.
5. Maintenance Mode
The global maintenance switch provides a clean way to take the system offline for updates. Users see a friendly message rather than mysterious errors.
Challenges and Limitations
1. Simulated vs. Real Metrics
In my implementation, load levels are manually set via the admin endpoint. In a real system, load shedding would be automatic based on actual metrics like CPU utilization, request queue depth, or memory usage.
2. Cache Invalidation
My simple cache never expires. In production, you'd need cache invalidation strategies (TTL, write-through, etc.) to ensure data freshness.
3. No Persistence
The feature flags reset when the Lambda function cold starts. In production, these would be stored in a database or configuration service.
4. Single Region
My implementation is in a single region. Real-world systems would need multi-region deployment for zone/region failures.

Real-World Applications
The patterns I implemented are used everywhere in production:
•	Amazon.com progressively sheds recommendations during peak traffic
•	Netflix shows cached content when personalization service is down
•	Twitter displays "Tweets aren't loading right now" with retry options
•	Banking apps show account balances but may hide transaction history during outages
________________________________________
Lessons Learned
1. Graceful Degradation Requires Intentional Design
You can't add graceful degradation after building a system - it must be designed from the start. The tiered approach forced me to think about what really matters to users.
2. Fallbacks Should Be Simple and Reliable
The best fallbacks are simple - static content, cached data, or default values. Complex fallbacks can become failure points themselves.
3. Monitoring is Essential
Without monitoring (like my health endpoint and logging), you wouldn't know when features are degraded. Users would just think the site is broken.
4. Testing Failure Scenarios is Crucial
My test scenarios revealed issues I hadn't considered. For example, I initially forgot to implement cache expiration, which would serve stale data indefinitely.
________________________________________
Conclusion
Part 3 of this lab successfully demonstrated how graceful degradation strategies can keep a system functional even when parts fail. The three-tier architecture, fallback mechanisms, feature flags, and load shedding worked together to ensure critical functionality (product information) remained available under all test scenarios.
The most important takeaway is that 100% availability of all features is impossible, but 100% availability of core functionality is achievable with proper design. Users will forgive missing recommendations or slightly stale reviews, but they won't forgive being unable to see product prices or complete a purchase.
These patterns are directly applicable to real-world cloud systems. The skills I learned - designing for failure, implementing fallbacks, progressive degradation, and feature flags - are essential for building robust, user-friendly applications that survive the inevitable failures of distributed systems.






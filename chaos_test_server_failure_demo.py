#!/usr/bin/env python3
"""
Chaos Engineering Test: Random Server Failure (DEMO VERSION)
This version uses MOCK responses to demonstrate the logic without network delays.

Tests if Tawakkalna system can handle sudden server failures:
1. Load balancer detects failed server
2. Traffic routes to healthy servers
3. Users experience minimal disruption
"""

import time
import random
from datetime import datetime

# Configuration
SERVERS = [
    "tawakkalna-riyadh-1.sa",
    "tawakkalna-riyadh-2.sa",
    "tawakkalna-jeddah-1.sa",
    "tawakkalna-jeddah-2.sa",
    "tawakkalna-dammam-1.sa"
]

LOAD_BALANCER = "https://tawakkalna.sa"
NUM_HEALTH_CHECKS = 10

class ChaosTest:
    def __init__(self):
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "server_failures": []
        }
        self.active_servers = SERVERS.copy()
    
    def log(self, message):
        """Print log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def kill_random_server(self):
        """Simulate killing a random server"""
        if len(self.active_servers) > 1:
            server = random.choice(self.active_servers)
            self.active_servers.remove(server)
            self.log(f" CHAOS: Killing server {server}")
            self.log(f"   Remaining active servers: {len(self.active_servers)}")
            self.results["server_failures"].append({
                "time": datetime.now(),
                "server": server
            })
            return server
        else:
            self.log(" Cannot kill more servers - only 1 remaining!")
            return None
    
    def mock_health_check(self):
        """
        Simulate load balancer health check.
        Success depends on having active servers available.
        """
        # Simulate response time (faster with more servers)
        base_time = 100  # 100ms base
        load_factor = 5 / len(self.active_servers)  # More load with fewer servers
        response_time = base_time * load_factor + random.uniform(0, 50)
        
        # Success rate depends on server availability
        # With all 5 servers: 99.9% success
        # With 1 server: 95% success (overloaded)
        success_probability = 0.95 + (len(self.active_servers) - 1) * 0.01
        
        return random.random() < success_probability, response_time
    
    def check_system_health(self):
        """Check if system is still responding"""
        self.results["total_requests"] += 1
        
        success, response_time = self.mock_health_check()
        
        if success:
            self.results["successful_requests"] += 1
            self.results["response_times"].append(response_time)
            self.log(f" System healthy - Response time: {response_time:.2f}ms")
            return True
        else:
            self.results["failed_requests"] += 1
            self.log(f" System unhealthy - Request failed")
            return False
    
    def run_test(self):
        """Run the chaos test"""
        self.log(" Starting Chaos Engineering Test: Server Failure (DEMO)")
        self.log(f"Target: {LOAD_BALANCER}")
        self.log(f"Initial active servers: {len(self.active_servers)}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Initial health check
        self.log(" Initial health check...")
        self.check_system_health()
        
        # Run multiple rounds of chaos
        for i in range(NUM_HEALTH_CHECKS):
            time.sleep(0.3)  # Small delay for readability
            
            # 40% chance to kill a server each round
            if random.random() < 0.4:
                self.kill_random_server()
            
            # Always do health check
            self.check_system_health()
        
        self.results["test_duration"] = time.time() - start_time
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        self.log(" CHAOS TEST RESULTS")
        print("=" * 60)
        
        total = self.results["total_requests"]
        success = self.results["successful_requests"]
        failed = self.results["failed_requests"]
        
        success_rate = (success / total * 100) if total > 0 else 0
        avg_response_time = sum(self.results["response_times"]) / len(self.results["response_times"]) if self.results["response_times"] else 0
        
        print(f"\n Request Statistics:")
        print(f"   Total Requests: {total}")
        print(f"   Successful: {success} ({success_rate:.2f}%)")
        print(f"   Failed: {failed} ({100-success_rate:.2f}%)")
        print(f"   Average Response Time: {avg_response_time:.2f}ms")
        
        print(f"\n Chaos Events:")
        print(f"   Servers Killed: {len(self.results['server_failures'])}")
        print(f"   Servers Still Active: {len(self.active_servers)}")
        
        for i, failure in enumerate(self.results['server_failures'], 1):
            print(f"   {i}. {failure['server']}")
        
        print("\n Pass/Fail Criteria:")
        
        # Check resilience requirements
        if success_rate >= 99.9:
            print("    SUCCESS RATE: PASS (>99.9%)")
        elif success_rate >= 95:
            print(f"    SUCCESS RATE: ACCEPTABLE ({success_rate:.2f}% >= 95%)")
        else:
            print(f"    SUCCESS RATE: FAIL ({success_rate:.2f}% < 95%)")
        
        if avg_response_time < 3000:
            print(f"    RESPONSE TIME: PASS ({avg_response_time:.2f}ms < 3000ms)")
        else:
            print(f"    RESPONSE TIME: FAIL ({avg_response_time:.2f}ms > 3000ms)")
        
        # Overall
        print("\n" + "=" * 60)
        if success_rate >= 95 and avg_response_time < 3000:
            print(" OVERALL RESULT: SYSTEM IS RESILIENT!")
            print("   The load balancer successfully routed traffic around failed servers.")
        else:
            print(" OVERALL RESULT: RESILIENCE NEEDS IMPROVEMENT")
            print("   Consider adding more servers or improving failover speed.")
        
        print(f"\n Test Duration: {self.results['test_duration']:.2f} seconds")
        print("=" * 60)

def main():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║     TAWAKKALNA CHAOS ENGINEERING TEST                 ║
    ║     Test: Random Server Failure (DEMO)                ║
    ║     Purpose: Verify load balancer resilience          ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    print(" This demo uses MOCK responses to show how the test works.")
    print("   In production, it would actually SSH to servers and stop services.\n")
    
    test = ChaosTest()
    test.run_test()

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Chaos Engineering Test: Random Server Failure
Tests if Tawakkalna system can handle sudden server failures

This script simulates random server failures to test:
1. Load balancer detects failed server
2. Traffic routes to healthy servers
3. Users experience minimal disruption
"""

import time
import random
import requests
from datetime import datetime

# Configuration
SERVERS = [
    "https://tawakkalna-riyadh-1.sa",
    "https://tawakkalna-riyadh-2.sa",
    "https://tawakkalna-jeddah-1.sa",
    "https://tawakkalna-jeddah-2.sa",
    "https://tawakkalna-dammam-1.sa"
]

LOAD_BALANCER = "https://tawakkalna.sa"
TEST_DURATION = 300  # 5 minutes
CHECK_INTERVAL = 5   # Check every 5 seconds

class ChaosTest:
    def __init__(self):
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "server_failures": []
        }
    
    def log(self, message):
        """Print log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def kill_random_server(self):
        """Simulate killing a random server (in real test, would SSH and stop service)"""
        server = random.choice(SERVERS)
        self.log(f"🔥 CHAOS: Killing server {server}")
        self.results["server_failures"].append({
            "time": datetime.now(),
            "server": server
        })
        # In real implementation:
        # ssh_command = f"ssh {server} 'sudo systemctl stop tawakkalna'"
        # os.system(ssh_command)
        return server
    
    def check_system_health(self):
        """Check if system is still responding"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{LOAD_BALANCER}/health",
                timeout=10
            )
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            self.results["response_times"].append(response_time)
            self.results["total_requests"] += 1
            
            if response.status_code == 200:
                self.results["successful_requests"] += 1
                self.log(f"✅ System healthy - Response time: {response_time:.2f}ms")
                return True
            else:
                self.results["failed_requests"] += 1
                self.log(f"❌ System unhealthy - Status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.results["failed_requests"] += 1
            self.results["total_requests"] += 1
            self.log(f"❌ Request failed: {str(e)}")
            return False
    
    def run_test(self):
        """Run the chaos test"""
        self.log("🚀 Starting Chaos Engineering Test: Server Failure")
        self.log(f"Duration: {TEST_DURATION} seconds")
        self.log(f"Target: {LOAD_BALANCER}")
        self.log("=" * 60)
        
        start_time = time.time()
        
        # Initial health check
        self.log("Initial health check...")
        self.check_system_health()
        
        # Kill first server
        time.sleep(10)
        self.kill_random_server()
        
        # Monitor system
        while time.time() - start_time < TEST_DURATION:
            time.sleep(CHECK_INTERVAL)
            self.check_system_health()
            
            # Randomly kill another server (20% chance)
            if random.random() < 0.2:
                self.kill_random_server()
        
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        self.log("=" * 60)
        self.log("📊 CHAOS TEST RESULTS")
        self.log("=" * 60)
        
        total = self.results["total_requests"]
        success = self.results["successful_requests"]
        failed = self.results["failed_requests"]
        
        success_rate = (success / total * 100) if total > 0 else 0
        avg_response_time = sum(self.results["response_times"]) / len(self.results["response_times"]) if self.results["response_times"] else 0
        
        self.log(f"Total Requests: {total}")
        self.log(f"Successful: {success} ({success_rate:.2f}%)")
        self.log(f"Failed: {failed} ({100-success_rate:.2f}%)")
        self.log(f"Average Response Time: {avg_response_time:.2f}ms")
        self.log(f"Servers Killed: {len(self.results['server_failures'])}")
        
        self.log("\n📋 Pass/Fail Criteria:")
        
        # Check if system meets resilience requirements
        if success_rate >= 99.9:
            self.log("✅ SUCCESS RATE: PASS (>99.9%)")
        else:
            self.log(f"❌ SUCCESS RATE: FAIL ({success_rate:.2f}% < 99.9%)")
        
        if avg_response_time < 3000:  # 3 seconds
            self.log(f"✅ RESPONSE TIME: PASS (<3000ms)")
        else:
            self.log(f"❌ RESPONSE TIME: FAIL ({avg_response_time:.2f}ms > 3000ms)")
        
        if success_rate >= 99.9 and avg_response_time < 3000:
            self.log("\n🎉 OVERALL RESULT: SYSTEM IS RESILIENT!")
            self.log("The load balancer successfully routed traffic around failed servers.")
        else:
            self.log("\n⚠️ OVERALL RESULT: RESILIENCE NEEDS IMPROVEMENT")
            self.log("Consider adding more servers or improving failover speed.")

def main():
    """Main function"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║     TAWAKKALNA CHAOS ENGINEERING TEST                 ║
    ║     Test: Random Server Failure                       ║
    ║     Purpose: Verify load balancer resilience         ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    print("⚠️  WARNING: This test will deliberately cause server failures!")
    print("Only run in test environment, never in production.\n")
    
    # In real implementation, would ask for confirmation
    # response = input("Continue? (yes/no): ")
    # if response.lower() != "yes":
    #     print("Test cancelled.")
    #     return
    
    print("NOTE: This is a simulation for educational purposes.")
    print("In real implementation, this would SSH to servers and stop services.\n")
    
    test = ChaosTest()
    test.run_test()

if __name__ == "__main__":
    main()


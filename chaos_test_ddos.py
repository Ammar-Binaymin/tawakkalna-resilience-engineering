#!/usr/bin/env python3
"""
Chaos Engineering Test: DDoS Attack Simulation
Tests if Tawakkalna system can handle massive traffic spike

This script simulates a DDoS attack to test:
1. DDoS protection activates
2. Rate limiting blocks excessive requests
3. Legitimate users still get service
"""

import time
import requests
import threading
from datetime import datetime
from collections import defaultdict

# Configuration
TARGET_URL = "https://tawakkalna.sa/api/vaccination-certificate"
NORMAL_USERS = 100      # Simulate 100 normal users
ATTACK_BOTS = 1000      # Simulate 1000 malicious bots
TEST_DURATION = 60      # 1 minute test
REQUESTS_PER_USER = 10  # Normal users: 10 requests per minute
REQUESTS_PER_BOT = 100  # Bots: 100 requests per minute

class DDoSSimulation:
    def __init__(self):
        self.results = {
            "normal_user_success": 0,
            "normal_user_fail": 0,
            "bot_requests_sent": 0,
            "bot_requests_blocked": 0,
            "start_time": None,
            "end_time": None
        }
        self.lock = threading.Lock()
    
    def log(self, message):
        """Print log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def simulate_normal_user(self, user_id):
        """Simulate a normal user making legitimate requests"""
        for i in range(REQUESTS_PER_USER):
            try:
                # Normal user behavior: reasonable request rate
                time.sleep(6)  # Wait 6 seconds between requests
                
                response = requests.get(
                    TARGET_URL,
                    headers={
                        "User-Agent": "TawakkalnaApp/2.0",
                        "X-User-ID": f"normal-{user_id}"
                    },
                    timeout=10
                )
                
                with self.lock:
                    if response.status_code == 200:
                        self.results["normal_user_success"] += 1
                    else:
                        self.results["normal_user_fail"] += 1
                        
            except requests.exceptions.RequestException:
                with self.lock:
                    self.results["normal_user_fail"] += 1
    
    def simulate_attack_bot(self, bot_id):
        """Simulate a malicious bot making excessive requests"""
        for i in range(REQUESTS_PER_BOT):
            try:
                # Bot behavior: rapid fire requests
                time.sleep(0.6)  # Only 0.6 seconds between requests (very aggressive)
                
                response = requests.get(
                    TARGET_URL,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Bot)",
                        "X-Bot-ID": f"bot-{bot_id}"
                    },
                    timeout=5
                )
                
                with self.lock:
                    self.results["bot_requests_sent"] += 1
                    
                    # If we get rate limited (429) or blocked, count it
                    if response.status_code in [429, 403]:
                        self.results["bot_requests_blocked"] += 1
                        
            except requests.exceptions.RequestException:
                with self.lock:
                    self.results["bot_requests_sent"] += 1
                    self.results["bot_requests_blocked"] += 1
    
    def run_simulation(self):
        """Run the DDoS simulation"""
        self.log("🚀 Starting DDoS Simulation")
        self.log(f"Normal Users: {NORMAL_USERS}")
        self.log(f"Attack Bots: {ATTACK_BOTS}")
        self.log(f"Duration: {TEST_DURATION} seconds")
        self.log("=" * 60)
        
        self.results["start_time"] = time.time()
        
        # Create threads
        threads = []
        
        # Launch normal user threads
        self.log("👥 Launching normal user threads...")
        for i in range(NORMAL_USERS):
            thread = threading.Thread(
                target=self.simulate_normal_user,
                args=(i,)
            )
            threads.append(thread)
            thread.start()
        
        time.sleep(5)  # Let normal users start first
        
        # Launch attack bot threads
        self.log("🤖 Launching attack bot threads...")
        self.log("⚠️  ATTACK PHASE STARTING")
        for i in range(ATTACK_BOTS):
            thread = threading.Thread(
                target=self.simulate_attack_bot,
                args=(i,)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for test duration
        time.sleep(TEST_DURATION)
        
        # Wait for all threads to complete
        self.log("⏳ Waiting for all threads to complete...")
        for thread in threads:
            thread.join(timeout=10)
        
        self.results["end_time"] = time.time()
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        self.log("=" * 60)
        self.log("📊 DDOS SIMULATION RESULTS")
        self.log("=" * 60)
        
        # Normal users metrics
        total_normal = self.results["normal_user_success"] + self.results["normal_user_fail"]
        normal_success_rate = (self.results["normal_user_success"] / total_normal * 100) if total_normal > 0 else 0
        
        self.log("\n👥 Normal Users (Legitimate Traffic):")
        self.log(f"  Total Requests: {total_normal}")
        self.log(f"  Successful: {self.results['normal_user_success']}")
        self.log(f"  Failed: {self.results['normal_user_fail']}")
        self.log(f"  Success Rate: {normal_success_rate:.2f}%")
        
        # Attack bots metrics
        bot_block_rate = (self.results["bot_requests_blocked"] / self.results["bot_requests_sent"] * 100) if self.results["bot_requests_sent"] > 0 else 0
        
        self.log("\n🤖 Attack Bots (Malicious Traffic):")
        self.log(f"  Total Requests: {self.results['bot_requests_sent']}")
        self.log(f"  Blocked/Rate Limited: {self.results['bot_requests_blocked']}")
        self.log(f"  Block Rate: {bot_block_rate:.2f}%")
        
        # Overall assessment
        self.log("\n📋 Pass/Fail Criteria:")
        
        # Criterion 1: Normal users should still get service (>95% success)
        if normal_success_rate >= 95:
            self.log("✅ NORMAL USER ACCESS: PASS (>95% success)")
        else:
            self.log(f"❌ NORMAL USER ACCESS: FAIL ({normal_success_rate:.2f}% < 95%)")
        
        # Criterion 2: Bots should be blocked (>80% blocked)
        if bot_block_rate >= 80:
            self.log("✅ BOT BLOCKING: PASS (>80% blocked)")
        else:
            self.log(f"❌ BOT BLOCKING: FAIL ({bot_block_rate:.2f}% < 80%)")
        
        # Overall result
        if normal_success_rate >= 95 and bot_block_rate >= 80:
            self.log("\n🎉 OVERALL RESULT: SYSTEM RESILIENT TO DDOS!")
            self.log("DDoS protection successfully blocked attack while serving legitimate users.")
        else:
            self.log("\n⚠️ OVERALL RESULT: DDOS PROTECTION NEEDS IMPROVEMENT")
            if normal_success_rate < 95:
                self.log("- Normal users affected: Increase capacity or better traffic filtering")
            if bot_block_rate < 80:
                self.log("- Too many bot requests getting through: Improve rate limiting")
        
        # Duration
        duration = self.results["end_time"] - self.results["start_time"]
        self.log(f"\nTest Duration: {duration:.2f} seconds")

def main():
    """Main function"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║     TAWAKKALNA CHAOS ENGINEERING TEST                 ║
    ║     Test: DDoS Attack Simulation                      ║
    ║     Purpose: Verify DDoS protection                   ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    print("⚠️  WARNING: This test will generate massive traffic!")
    print("Only run in test environment with permission.\n")
    
    print("NOTE: This is a simplified simulation for educational purposes.")
    print("Real DDoS attacks are illegal. This is for testing your own system.\n")
    
    simulation = DDoSSimulation()
    simulation.run_simulation()

if __name__ == "__main__":
    main()


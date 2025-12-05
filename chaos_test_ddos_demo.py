#!/usr/bin/env python3
"""
Chaos Engineering Test: DDoS Attack Simulation (DEMO VERSION)
This version uses MOCK responses to demonstrate the logic without network delays.

Tests if Tawakkalna system can handle massive traffic spike:
1. DDoS protection activates
2. Rate limiting blocks excessive requests
3. Legitimate users still get service
"""

import time
import random
import threading
from datetime import datetime

# Configuration - Demo values
TARGET_URL = "https://tawakkalna.sa/api/vaccination-certificate"
NORMAL_USERS = 5
ATTACK_BOTS = 10
REQUESTS_PER_USER = 3
REQUESTS_PER_BOT = 5

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
        self.ddos_protection_active = False
    
    def log(self, message):
        """Print log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def mock_server_response(self, is_bot=False):
        """
        Simulate server response with DDoS protection logic.
        In a real system, this would be the actual server behavior.
        """
        # Simulate DDoS protection activating after detecting bot traffic
        if self.results["bot_requests_sent"] > 5:
            self.ddos_protection_active = True
        
        if is_bot and self.ddos_protection_active:
            # 85% chance bot gets blocked when protection is active
            if random.random() < 0.85:
                return 429  # Rate limited
            return 200
        elif is_bot:
            # Before protection activates, 30% blocked
            if random.random() < 0.30:
                return 429
            return 200
        else:
            # Normal users: 95% success rate even during attack
            if random.random() < 0.95:
                return 200
            return 503  # Service unavailable
    
    def simulate_normal_user(self, user_id):
        """Simulate a normal user making legitimate requests"""
        for i in range(REQUESTS_PER_USER):
            time.sleep(0.1)  # Small delay for demo
            
            status_code = self.mock_server_response(is_bot=False)
            
            with self.lock:
                if status_code == 200:
                    self.results["normal_user_success"] += 1
                else:
                    self.results["normal_user_fail"] += 1
    
    def simulate_attack_bot(self, bot_id):
        """Simulate a malicious bot making excessive requests"""
        for i in range(REQUESTS_PER_BOT):
            time.sleep(0.05)  # Bots are faster
            
            status_code = self.mock_server_response(is_bot=True)
            
            with self.lock:
                self.results["bot_requests_sent"] += 1
                if status_code in [429, 403]:
                    self.results["bot_requests_blocked"] += 1
    
    def run_simulation(self):
        """Run the DDoS simulation"""
        self.log(" Starting DDoS Simulation (DEMO VERSION)")
        self.log(f"Normal Users: {NORMAL_USERS}")
        self.log(f"Attack Bots: {ATTACK_BOTS}")
        self.log("=" * 60)
        
        self.results["start_time"] = time.time()
        
        threads = []
        
        # Launch normal user threads
        self.log("👥 Launching normal user threads...")
        for i in range(NORMAL_USERS):
            thread = threading.Thread(target=self.simulate_normal_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        time.sleep(0.5)
        
        # Launch attack bot threads
        self.log(" Launching attack bot threads...")
        self.log(" ATTACK PHASE STARTING")
        for i in range(ATTACK_BOTS):
            thread = threading.Thread(target=self.simulate_attack_bot, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        self.log(" Processing requests...")
        for thread in threads:
            thread.join()
        
        self.results["end_time"] = time.time()
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        self.log(" DDOS SIMULATION RESULTS")
        print("=" * 60)
        
        # Normal users metrics
        total_normal = self.results["normal_user_success"] + self.results["normal_user_fail"]
        normal_success_rate = (self.results["normal_user_success"] / total_normal * 100) if total_normal > 0 else 0
        
        print("\n Normal Users (Legitimate Traffic):")
        print(f"   Total Requests: {total_normal}")
        print(f"   Successful: {self.results['normal_user_success']}")
        print(f"   Failed: {self.results['normal_user_fail']}")
        print(f"   Success Rate: {normal_success_rate:.2f}%")
        
        # Attack bots metrics
        bot_block_rate = (self.results["bot_requests_blocked"] / self.results["bot_requests_sent"] * 100) if self.results["bot_requests_sent"] > 0 else 0
        
        print("\n Attack Bots (Malicious Traffic):")
        print(f"   Total Requests: {self.results['bot_requests_sent']}")
        print(f"   Blocked/Rate Limited: {self.results['bot_requests_blocked']}")
        print(f"   Block Rate: {bot_block_rate:.2f}%")
        
        # Pass/Fail
        print("\n Pass/Fail Criteria:")
        
        if normal_success_rate >= 95:
            print("    NORMAL USER ACCESS: PASS (>95% success)")
        else:
            print(f"    NORMAL USER ACCESS: FAIL ({normal_success_rate:.2f}% < 95%)")
        
        if bot_block_rate >= 80:
            print("    BOT BLOCKING: PASS (>80% blocked)")
        else:
            print(f"    BOT BLOCKING: FAIL ({bot_block_rate:.2f}% < 80%)")
        
        # Overall
        print("\n" + "=" * 60)
        if normal_success_rate >= 95 and bot_block_rate >= 80:
            print(" OVERALL RESULT: SYSTEM RESILIENT TO DDOS!")
            print("   DDoS protection blocked attack while serving legitimate users.")
        else:
            print(" OVERALL RESULT: DDOS PROTECTION NEEDS IMPROVEMENT")
        
        duration = self.results["end_time"] - self.results["start_time"]
        print(f"\n Test Duration: {duration:.2f} seconds")
        print("=" * 60)

def main():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║     TAWAKKALNA CHAOS ENGINEERING TEST                 ║
    ║     Test: DDoS Attack Simulation (DEMO)               ║
    ║     Purpose: Verify DDoS protection logic             ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    print(" This demo uses MOCK responses to show how the test works.")
    print("   In production, it would make real HTTP requests.\n")
    
    simulation = DDoSSimulation()
    simulation.run_simulation()

if __name__ == "__main__":
    main()


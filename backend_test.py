import requests
import sys
import json
from datetime import datetime

class FraudDetectionAPITester:
    def __init__(self, base_url="https://safeguard-ai-28.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        self.test_data = {
            'transactions': [],
            'cases': [],
            'alerts': []
        }
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, description=""):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        if description:
            print(f"   Description: {description}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {json.dumps(response_data, indent=2)}")
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration for all roles"""
        print("\n" + "="*50)
        print("TESTING USER REGISTRATION")
        print("="*50)
        
        test_users = [
            {"email": "user@test.com", "password": "password123", "name": "Test User", "role": "user"},
            {"email": "analyst@test.com", "password": "password123", "name": "Test Analyst", "role": "analyst"},
            {"email": "admin@test.com", "password": "password123", "name": "Test Admin", "role": "admin"}
        ]
        
        for user_data in test_users:
            success, response = self.run_test(
                f"Register {user_data['role']}",
                "POST",
                "auth/register",
                200,
                data=user_data,
                description=f"Register user with {user_data['role']} role"
            )
            if success:
                self.users[user_data['role']] = response

    def test_user_login(self):
        """Test user login for all roles"""
        print("\n" + "="*50)
        print("TESTING USER LOGIN")
        print("="*50)
        
        login_credentials = [
            {"email": "user@test.com", "password": "password123", "role": "user"},
            {"email": "analyst@test.com", "password": "password123", "role": "analyst"},
            {"email": "admin@test.com", "password": "password123", "role": "admin"}
        ]
        
        for creds in login_credentials:
            success, response = self.run_test(
                f"Login {creds['role']}",
                "POST",
                "auth/login",
                200,
                data={"email": creds['email'], "password": creds['password']},
                description=f"Login with {creds['role']} credentials"
            )
            if success and 'token' in response:
                self.tokens[creds['role']] = response['token']
                print(f"   Token stored for {creds['role']}")

    def test_transaction_submission(self):
        """Test transaction submission with different amounts and types"""
        print("\n" + "="*50)
        print("TESTING TRANSACTION SUBMISSION")
        print("="*50)
        
        if 'user' not in self.tokens:
            print("❌ No user token available for transaction testing")
            return
        
        test_transactions = [
            {"amount": 50.0, "transaction_type": "payment", "merchant": "Coffee Shop", "location": "New York"},
            {"amount": 500.0, "transaction_type": "transfer", "merchant": "Bank Transfer", "location": "Online"},
            {"amount": 5000.0, "transaction_type": "withdrawal", "merchant": "ATM Withdrawal", "location": "Los Angeles"},
            {"amount": 50000.0, "transaction_type": "purchase", "merchant": "Unknown Merchant", "location": "Suspicious Location"}
        ]
        
        for i, tx_data in enumerate(test_transactions):
            success, response = self.run_test(
                f"Submit Transaction ${tx_data['amount']}",
                "POST",
                "transactions",
                200,
                data=tx_data,
                token=self.tokens['user'],
                description=f"Submit {tx_data['transaction_type']} for ${tx_data['amount']}"
            )
            if success:
                self.test_data['transactions'].append(response)
                print(f"   Risk Score: {response.get('risk_score', 'N/A')}")
                print(f"   Risk Level: {response.get('risk_level', 'N/A')}")
                print(f"   Status: {response.get('status', 'N/A')}")
                if response.get('fraud_types'):
                    print(f"   Fraud Types: {response.get('fraud_types')}")

    def test_transaction_retrieval(self):
        """Test transaction retrieval for different roles"""
        print("\n" + "="*50)
        print("TESTING TRANSACTION RETRIEVAL")
        print("="*50)
        
        roles_to_test = ['user', 'analyst', 'admin']
        
        for role in roles_to_test:
            if role in self.tokens:
                success, response = self.run_test(
                    f"Get Transactions ({role})",
                    "GET",
                    "transactions",
                    200,
                    token=self.tokens[role],
                    description=f"Retrieve transactions as {role}"
                )
                if success:
                    print(f"   Retrieved {len(response)} transactions for {role}")

    def test_fraud_alerts(self):
        """Test fraud alerts endpoint (admin/analyst only)"""
        print("\n" + "="*50)
        print("TESTING FRAUD ALERTS")
        print("="*50)
        
        # Test unauthorized access (user role)
        if 'user' in self.tokens:
            success, response = self.run_test(
                "Get Fraud Alerts (User - Should Fail)",
                "GET",
                "fraud-alerts",
                403,
                token=self.tokens['user'],
                description="User should not have access to fraud alerts"
            )
        
        # Test authorized access (analyst and admin)
        for role in ['analyst', 'admin']:
            if role in self.tokens:
                success, response = self.run_test(
                    f"Get Fraud Alerts ({role})",
                    "GET",
                    "fraud-alerts",
                    200,
                    token=self.tokens[role],
                    description=f"Retrieve fraud alerts as {role}"
                )
                if success:
                    self.test_data['alerts'] = response
                    print(f"   Retrieved {len(response)} fraud alerts for {role}")

    def test_investigation_cases(self):
        """Test investigation case creation and retrieval"""
        print("\n" + "="*50)
        print("TESTING INVESTIGATION CASES")
        print("="*50)
        
        # Test case creation (analyst only)
        if 'analyst' in self.tokens and self.test_data['transactions']:
            transaction_ids = [tx['id'] for tx in self.test_data['transactions'][:2]]
            case_data = {
                "transaction_ids": transaction_ids,
                "notes": "Investigating suspicious transaction pattern"
            }
            
            success, response = self.run_test(
                "Create Investigation Case",
                "POST",
                "cases",
                200,
                data=case_data,
                token=self.tokens['analyst'],
                description="Create new investigation case as analyst"
            )
            if success:
                self.test_data['cases'].append(response)
                print(f"   Case ID: {response.get('id', 'N/A')}")
        
        # Test unauthorized case creation (user role)
        if 'user' in self.tokens:
            success, response = self.run_test(
                "Create Case (User - Should Fail)",
                "POST",
                "cases",
                403,
                data={"transaction_ids": ["test"], "notes": "test"},
                token=self.tokens['user'],
                description="User should not be able to create cases"
            )
        
        # Test case retrieval
        for role in ['analyst', 'admin']:
            if role in self.tokens:
                success, response = self.run_test(
                    f"Get Cases ({role})",
                    "GET",
                    "cases",
                    200,
                    token=self.tokens[role],
                    description=f"Retrieve cases as {role}"
                )
                if success:
                    print(f"   Retrieved {len(response)} cases for {role}")

    def test_case_updates(self):
        """Test case status updates"""
        print("\n" + "="*50)
        print("TESTING CASE UPDATES")
        print("="*50)
        
        if self.test_data['cases'] and 'analyst' in self.tokens:
            case_id = self.test_data['cases'][0]['id']
            update_data = {
                "status": "closed",
                "notes": "Investigation completed - no fraud detected"
            }
            
            success, response = self.run_test(
                "Update Case Status",
                "PATCH",
                f"cases/{case_id}",
                200,
                data=update_data,
                token=self.tokens['analyst'],
                description="Update case status and notes"
            )
            if success:
                print(f"   Updated case status to: {response.get('status', 'N/A')}")

    def test_analytics_stats(self):
        """Test analytics dashboard stats"""
        print("\n" + "="*50)
        print("TESTING ANALYTICS STATS")
        print("="*50)
        
        # Test unauthorized access (user role)
        if 'user' in self.tokens:
            success, response = self.run_test(
                "Get Analytics (User - Should Fail)",
                "GET",
                "analytics/stats",
                403,
                token=self.tokens['user'],
                description="User should not have access to analytics"
            )
        
        # Test authorized access (analyst and admin)
        for role in ['analyst', 'admin']:
            if role in self.tokens:
                success, response = self.run_test(
                    f"Get Analytics Stats ({role})",
                    "GET",
                    "analytics/stats",
                    200,
                    token=self.tokens[role],
                    description=f"Retrieve analytics stats as {role}"
                )
                if success:
                    print(f"   Total Transactions: {response.get('total_transactions', 'N/A')}")
                    print(f"   Flagged Transactions: {response.get('flagged_transactions', 'N/A')}")
                    print(f"   Total Alerts: {response.get('total_alerts', 'N/A')}")
                    print(f"   Active Cases: {response.get('active_cases', 'N/A')}")
                    if 'risk_distribution' in response:
                        risk_dist = response['risk_distribution']
                        print(f"   Risk Distribution - High: {risk_dist.get('high', 0)}, Medium: {risk_dist.get('medium', 0)}, Low: {risk_dist.get('low', 0)}")

    def test_ai_integration(self):
        """Test AI fraud detection integration"""
        print("\n" + "="*50)
        print("TESTING AI INTEGRATION")
        print("="*50)
        
        if not self.test_data['transactions']:
            print("❌ No transactions available to test AI integration")
            return
        
        ai_analysis_found = False
        high_risk_detected = False
        
        for tx in self.test_data['transactions']:
            if tx.get('ai_analysis'):
                ai_analysis_found = True
                print(f"✅ AI Analysis found for transaction ${tx['amount']}")
                print(f"   Analysis: {tx['ai_analysis'][:100]}...")
                
                if tx.get('risk_score', 0) > 70:
                    high_risk_detected = True
                    print(f"✅ High risk transaction detected (Score: {tx['risk_score']})")
        
        if ai_analysis_found:
            self.tests_passed += 1
            print("✅ AI Integration working - Analysis generated")
        else:
            print("❌ AI Integration issue - No analysis found")
        
        if high_risk_detected:
            self.tests_passed += 1
            print("✅ High risk detection working")
        else:
            print("⚠️  No high risk transactions detected (may be expected)")
        
        self.tests_run += 2

def main():
    print("🚀 Starting AI-Driven Fraud Detection System API Tests")
    print("="*60)
    
    tester = FraudDetectionAPITester()
    
    # Run all tests in sequence
    tester.test_user_registration()
    tester.test_user_login()
    tester.test_transaction_submission()
    tester.test_transaction_retrieval()
    tester.test_fraud_alerts()
    tester.test_investigation_cases()
    tester.test_case_updates()
    tester.test_analytics_stats()
    tester.test_ai_integration()
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
import requests
import sys
import json
from datetime import datetime

class IndianPaymentFraudTester:
    def __init__(self, base_url="https://safeguard-ai-28.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.user_token = None
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_transactions = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration with Indian context"""
        success, response = self.run_test(
            "User Registration (testindia2@test.com)",
            "POST",
            "auth/register",
            200,
            data={
                "email": "testindia2@test.com",
                "password": "password123",
                "name": "Test India User",
                "role": "user"
            }
        )
        return success

    def test_user_login(self):
        """Test user login and get token"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": "testindia2@test.com",
                "password": "password123"
            }
        )
        if success and 'token' in response:
            self.user_token = response['token']
            print(f"   User token obtained: {self.user_token[:20]}...")
            return True
        return False

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": "admin@test.com",
                "password": "password123"
            }
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            print(f"   Admin token obtained: {self.admin_token[:20]}...")
            return True
        return False

    def test_phonepe_transaction(self):
        """Test PhonePe UPI Payment transaction"""
        transaction_data = {
            "transaction_id": "UPI434567891234",
            "amount": 5000.0,
            "payment_method": "phonepe",
            "transaction_type": "upi_payment",
            "merchant": "Amazon India",
            "location": "Mumbai, Maharashtra"
        }
        
        success, response = self.run_test(
            "PhonePe UPI Payment Transaction",
            "POST",
            "transactions",
            200,
            data=transaction_data,
            token=self.user_token
        )
        
        if success:
            # Verify Indian payment context
            print(f"   Transaction ID: {response.get('transaction_id')}")
            print(f"   Amount: ₹{response.get('amount')}")
            print(f"   Payment Method: {response.get('payment_method')}")
            print(f"   Payment Verified: {response.get('payment_verified')}")
            print(f"   Risk Level: {response.get('risk_level')}")
            print(f"   AI Analysis: {response.get('ai_analysis', 'N/A')[:100]}...")
            
            # Store for later verification
            self.created_transactions.append(response.get('id'))
            
            # Verify required fields
            required_fields = ['transaction_id', 'payment_method', 'payment_verified', 'ai_analysis']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
                return False
                
        return success

    def test_paytm_high_risk_transaction(self):
        """Test Paytm high-risk transaction"""
        transaction_data = {
            "transaction_id": "PTM999888777666",
            "amount": 50000.0,
            "payment_method": "paytm",
            "transaction_type": "money_transfer",
            "merchant": "Unknown Person",
            "location": "Delhi, India"
        }
        
        success, response = self.run_test(
            "Paytm High-Risk Transaction",
            "POST",
            "transactions",
            200,
            data=transaction_data,
            token=self.user_token
        )
        
        if success:
            print(f"   Transaction ID: {response.get('transaction_id')}")
            print(f"   Amount: ₹{response.get('amount')}")
            print(f"   Risk Score: {response.get('risk_score')}")
            print(f"   Status: {response.get('status')}")
            print(f"   Payment Verified: {response.get('payment_verified')}")
            
            self.created_transactions.append(response.get('id'))
            
            # High-risk transaction should likely be flagged
            if response.get('risk_score', 0) > 70:
                print(f"   ✅ High-risk transaction properly flagged")
            else:
                print(f"   ⚠️  Expected high risk score for suspicious transaction")
                
        return success

    def test_googlepay_bill_payment(self):
        """Test Google Pay bill payment"""
        transaction_data = {
            "transaction_id": "GPAY123456789",
            "amount": 2500.0,
            "payment_method": "googlepay",
            "transaction_type": "bill_payment",
            "merchant": "HDFC Credit Card",
            "location": "Bangalore, Karnataka"
        }
        
        success, response = self.run_test(
            "Google Pay Bill Payment",
            "POST",
            "transactions",
            200,
            data=transaction_data,
            token=self.user_token
        )
        
        if success:
            print(f"   Transaction ID: {response.get('transaction_id')}")
            print(f"   Payment Method: {response.get('payment_method')}")
            print(f"   Transaction Type: {response.get('transaction_type')}")
            print(f"   Payment Verified: {response.get('payment_verified')}")
            
            self.created_transactions.append(response.get('id'))
            
        return success

    def test_get_transactions(self):
        """Test getting user transactions"""
        success, response = self.run_test(
            "Get User Transactions",
            "GET",
            "transactions",
            200,
            token=self.user_token
        )
        
        if success and isinstance(response, list):
            print(f"   Retrieved {len(response)} transactions")
            for tx in response[:2]:  # Show first 2 transactions
                print(f"   - ID: {tx.get('transaction_id')} | ₹{tx.get('amount')} | {tx.get('payment_method')}")
                
        return success

    def test_admin_analytics(self):
        """Test admin analytics endpoint"""
        if not self.admin_token:
            print("⚠️  Skipping admin analytics - no admin token")
            return True
            
        success, response = self.run_test(
            "Admin Analytics Stats",
            "GET",
            "analytics/stats",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"   Total Transactions: {response.get('total_transactions')}")
            print(f"   Flagged Transactions: {response.get('flagged_transactions')}")
            print(f"   Total Alerts: {response.get('total_alerts')}")
            print(f"   Risk Distribution: {response.get('risk_distribution')}")
            
        return success

    def test_fraud_alerts(self):
        """Test fraud alerts endpoint"""
        if not self.admin_token:
            print("⚠️  Skipping fraud alerts - no admin token")
            return True
            
        success, response = self.run_test(
            "Get Fraud Alerts",
            "GET",
            "fraud-alerts",
            200,
            token=self.admin_token
        )
        
        if success and isinstance(response, list):
            print(f"   Retrieved {len(response)} fraud alerts")
            
        return success

def main():
    print("🇮🇳 Starting Indian Payment Fraud Detection System Tests")
    print("=" * 60)
    
    tester = IndianPaymentFraudTester()
    
    # Test sequence
    tests = [
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Admin Login", tester.test_admin_login),
        ("PhonePe UPI Payment", tester.test_phonepe_transaction),
        ("Paytm High-Risk Transaction", tester.test_paytm_high_risk_transaction),
        ("Google Pay Bill Payment", tester.test_googlepay_bill_payment),
        ("Get Transactions", tester.test_get_transactions),
        ("Admin Analytics", tester.test_admin_analytics),
        ("Fraud Alerts", tester.test_fraud_alerts),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                print(f"❌ {test_name} failed - stopping critical path tests")
                # Continue with remaining tests for full coverage
        except Exception as e:
            print(f"❌ {test_name} crashed: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend tests passed!")
        return 0
    else:
        print("⚠️  Some backend tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
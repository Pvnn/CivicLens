#!/usr/bin/env python3
"""
Simple test script to verify the PolicyPulse backend setup
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    try:
        from app import create_app
        from app.models.policy import PolicyCard
        from app.services.policy_fetcher import GovernmentPolicyFetcher
        from app.services.policy_summarizer import PolicySummarizer
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_creation():
    """Test if Flask app can be created"""
    try:
        from app import create_app
        app = create_app()
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def test_policy_fetcher():
    """Test policy fetcher without external dependencies"""
    try:
        from app.services.policy_fetcher import GovernmentPolicyFetcher
        fetcher = GovernmentPolicyFetcher()
        policies = fetcher.fetch_recent_policies(7)
        print(f"✓ Policy fetcher works - found {len(policies)} sample policies")
        return True
    except Exception as e:
        print(f"✗ Policy fetcher error: {e}")
        return False

def test_policy_summarizer():
    """Test policy summarizer"""
    try:
        from app.services.policy_summarizer import PolicySummarizer
        summarizer = PolicySummarizer()
        
        sample_text = "GST Rate Notification updates tax exemptions for medicines"
        sample_title = "GST Rate Notification No. 10/2025"
        
        result = summarizer.generate_policy_card(sample_text, sample_title)
        print("✓ Policy summarizer works")
        print(f"  - English summary: {result['summary_english'][:50]}...")
        print(f"  - Nepali summary: {result['summary_nepali'][:50]}...")
        return True
    except Exception as e:
        print(f"✗ Policy summarizer error: {e}")
        return False

def main():
    """Run all tests"""
    print("PolicyPulse Backend Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_app_creation,
        test_policy_fetcher,
        test_policy_summarizer
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! The PolicyPulse backend is ready to run.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the server: python run.py")
        print("3. Test API: curl http://localhost:5000/api/policies/recent")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

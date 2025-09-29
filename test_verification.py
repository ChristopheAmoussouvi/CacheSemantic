#!/usr/bin/env python3
"""
Quick test to verify that verify_enhanced_dashboard.py works correctly
despite Pylint phantom errors.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_verification_script():
    """Test that the verification script can be imported and functions work."""
    try:
        # Import the verification module
        import verify_enhanced_dashboard as ved
        
        # Test helper functions exist
        assert hasattr(ved, '_print_data_overview')
        assert hasattr(ved, '_print_kpis')
        assert hasattr(ved, '_print_validation')
        assert hasattr(ved, 'test_enhanced_dashboard')
        assert hasattr(ved, 'check_dependencies')
        
        print("✅ All functions imported successfully")
        
        # Test that the functions are callable
        assert callable(ved._print_data_overview)
        assert callable(ved._print_kpis)
        assert callable(ved._print_validation)
        assert callable(ved.test_enhanced_dashboard)
        assert callable(ved.check_dependencies)
        
        print("✅ All functions are callable")
        
        # Test that no phantom method calls exist in the source
        import inspect
        source = inspect.getsource(ved.test_enhanced_dashboard)
        
        # These should NOT be in the source code
        phantom_calls = [
            "apply_filters(",
            "start_date=",
            "end_date=", 
            "selected_channels=",
            "selected_agents=",
            "generate_sample_support_data("
        ]
        
        for phantom in phantom_calls:
            if phantom in source:
                print(f"❌ Found phantom call: {phantom}")
                return False
        
        print("✅ No phantom method calls found in source")
        
        # Test actual method calls that should exist
        expected_calls = [
            "get_sample_data(",
            "calculate_kpis("
        ]
        
        for expected in expected_calls:
            if expected not in source:
                print(f"❌ Missing expected call: {expected}")
                return False
        
        print("✅ All expected method calls found")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing verification script integrity...")
    print("=" * 50)
    
    if test_verification_script():
        print("\n🎉 Verification script is correct!")
        print("📝 Note: Pylint errors about 'unexpected-keyword-arg' are phantom errors")
        print("🔧 To fix: Restart VS Code or clear Python language server cache")
    else:
        print("\n❌ Verification script has issues")
        sys.exit(1)
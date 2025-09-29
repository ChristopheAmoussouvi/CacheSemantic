#!/usr/bin/env python3
"""
Verification script for Enhanced Support Analytics Dashboard
Tests all components and validates the integration
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_enhanced_dashboard():
    """Test the enhanced dashboard components"""
    print("🧪 Testing Enhanced Support Analytics Dashboard")
    print("=" * 50)
    
    try:
        # Test import
        print("📦 Testing imports...")
        from src.components.enhanced_dashboard import EnhancedAnalyticsDashboard
        print("✅ EnhancedAnalyticsDashboard imported successfully")
        
        # Create dashboard instance
        print("\n🎯 Creating dashboard instance...")
        dashboard = EnhancedAnalyticsDashboard()
        print("✅ Dashboard instance created")
        
        # Test data generation
        print("\n📊 Generating sample data...")
        sample_data = dashboard.generate_sample_support_data()
        print(f"✅ Generated {len(sample_data)} sample records")
        print(f"📋 Columns: {list(sample_data.columns)}")
        print(f"📅 Date range: {sample_data['created_date'].min()} to {sample_data['created_date'].max()}")
        
        # Test KPI calculations
        print("\n📈 Testing KPI calculations...")
        kpis = dashboard.calculate_kpis(sample_data)
        print("✅ KPIs calculated successfully:")
        for key, value in kpis.items():
            if isinstance(value, (int, float)):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
        
        # Test filtering
        print("\n🔍 Testing filter functionality...")
        filtered_data = dashboard.apply_filters(
            sample_data,
            start_date=sample_data['created_date'].min(),
            end_date=sample_data['created_date'].max(),
            selected_channels=['Phone', 'Email'],
            selected_agents=['Agent_001', 'Agent_002']
        )
        print(f"✅ Filtered data: {len(filtered_data)} records (from {len(sample_data)})")
        
        # Test data validation
        print("\n✅ Data validation:")
        print(f"   Unique agents: {sample_data['agent_id'].nunique()}")
        print(f"   Unique channels: {sample_data['channel'].nunique()}")
        print(f"   Unique categories: {sample_data['category'].nunique()}")
        print(f"   CSAT range: {sample_data['csat_score'].min():.1f} - {sample_data['csat_score'].max():.1f}")
        print(f"   NPS range: {sample_data['nps_score'].min():.1f} - {sample_data['nps_score'].max():.1f}")
        
        print("\n🎉 All tests passed! Enhanced dashboard is ready to use.")
        print("\n🚀 To launch the dashboard:")
        print("   1. Run: streamlit run app.py")
        print("   2. Navigate to: 'Support Analytics' tab")
        print("   3. Explore the comprehensive KPIs and analytics!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print(f"📍 Error type: {type(e).__name__}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'plotly', 
        'scikit-learn', 'scipy', 'folium'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies available!")
    return True

if __name__ == "__main__":
    print("🎯 Enhanced Support Analytics Dashboard - Verification")
    print("=" * 60)
    
    # Check dependencies first
    deps_ok = check_dependencies()
    
    if deps_ok:
        print("\n" + "=" * 60)
        # Test the dashboard
        dashboard_ok = test_enhanced_dashboard()
        
        if dashboard_ok:
            print("\n" + "🌟" * 20)
            print("🎉 VERIFICATION SUCCESSFUL!")
            print("The Enhanced Support Analytics Dashboard is ready!")
            print("🌟" * 20)
        else:
            print("\n❌ Dashboard testing failed")
            sys.exit(1)
    else:
        print("\n❌ Dependency check failed")
        sys.exit(1)
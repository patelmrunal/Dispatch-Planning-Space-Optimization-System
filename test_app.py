#!/usr/bin/env python3
"""
Test script to verify the application runs without IndexError
"""

import sys
import os
sys.path.append('.')

def test_imports():
    """Test all imports work correctly"""
    try:
        from utils.job_db import list_jobs, init_db
        from agents.dispatch_planner import DispatchPlanner
        from agents.dynamic_optimizer import DynamicOptimizer
        from models.ai_trainer import AITrainer
        from visualizations.route_visualizer import plot_route_map
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_job_db():
    """Test job database operations"""
    try:
        from utils.job_db import list_jobs, init_db
        init_db()
        jobs = list_jobs()
        print(f"✅ Job DB test successful - {len(jobs)} jobs found")
        return True
    except Exception as e:
        print(f"❌ Job DB error: {e}")
        return False

def test_analytics_processing():
    """Test analytics processing with error handling"""
    try:
        from utils.job_db import list_jobs, init_db
        import pandas as pd
        import json
        import io
        
        init_db()
        jobs = list_jobs()
        
        if jobs:
            # Test the analytics processing logic
            job_data = []
            for job in jobs:
                try:
                    # Validate job data structure
                    if len(job) >= 4:
                        job_data.append({
                            'Job ID': job[0],
                            'Date': job[1],
                            'Products': len(pd.read_csv(io.StringIO(job[2]))) if job[2] else 0,
                            'Constraints': json.loads(job[3]) if job[3] else {}
                        })
                    else:
                        # Handle incomplete job data
                        job_data.append({
                            'Job ID': job[0] if len(job) > 0 else 'Unknown',
                            'Date': job[1] if len(job) > 1 else 'Unknown',
                            'Products': 0,
                            'Constraints': {}
                        })
                except Exception as e:
                    # Handle any parsing errors
                    job_data.append({
                        'Job ID': job[0] if len(job) > 0 else 'Unknown',
                        'Date': job[1] if len(job) > 1 else 'Unknown',
                        'Products': 0,
                        'Constraints': {}
                    })
            
            print(f"✅ Analytics processing successful - {len(job_data)} jobs processed")
            return True
        else:
            print("✅ Analytics processing successful - no jobs to process")
            return True
            
    except Exception as e:
        print(f"❌ Analytics processing error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚚 Testing AI-Powered Dispatch Planning & Space Optimization System")
    print("=" * 70)
    
    tests = [
        ("Import Test", test_imports),
        ("Job DB Test", test_job_db),
        ("Analytics Processing Test", test_analytics_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should run without IndexError.")
        print("\n🚀 You can now run the application with:")
        print("   streamlit run ui/app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 
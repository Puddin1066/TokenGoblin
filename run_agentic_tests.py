#!/usr/bin/env python3
"""
Agentic Functionality Test Runner
Comprehensive test suite for TokenGoblin's agentic capabilities.
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path


class AgenticTestRunner:
    """Test runner for agentic functionality"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_tests(self):
        """Run all agentic functionality tests"""
        print("🚀 Starting TokenGoblin Agentic Functionality Tests")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Run unit tests
        print("\n📋 Running Unit Tests...")
        unit_results = self._run_unit_tests()
        
        # Run integration tests
        print("\n🔗 Running Integration Tests...")
        integration_results = self._run_integration_tests()
        
        # Run effectiveness tests
        print("\n📊 Running Effectiveness Tests...")
        effectiveness_results = self._run_effectiveness_tests()
        
        self.end_time = time.time()
        
        # Compile results
        self.test_results = {
            'unit_tests': unit_results,
            'integration_tests': integration_results,
            'effectiveness_tests': effectiveness_results,
            'total_time': self.end_time - self.start_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate report
        self._generate_report()
        
        return self.test_results
    
    def _run_unit_tests(self):
        """Run unit tests for agentic functionality"""
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'test_agentic_functionality.py::TestAgenticFunctionality',
                '-v', '--tb=short'
            ], capture_output=True, text=True, timeout=300)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Test timeout after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }
    
    def _run_integration_tests(self):
        """Run integration tests for complete agentic flow"""
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'test_agentic_integration.py::TestAgenticIntegration',
                '-v', '--tb=short'
            ], capture_output=True, text=True, timeout=300)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Test timeout after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }
    
    def _run_effectiveness_tests(self):
        """Run effectiveness tests for agentic optimization"""
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'test_agentic_functionality.py::TestAgenticEffectiveness',
                'test_agentic_integration.py::TestAgenticEffectivenessMetrics',
                '-v', '--tb=short'
            ], capture_output=True, text=True, timeout=300)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Test timeout after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 AGENTIC FUNCTIONALITY TEST REPORT")
        print("=" * 60)
        
        # Summary
        total_tests = 0
        passed_tests = 0
        
        for test_type, results in self.test_results.items():
            if test_type != 'total_time' and test_type != 'timestamp':
                if results['success']:
                    passed_tests += 1
                total_tests += 1
        
        print(f"\n🎯 Test Summary:")
        print(f"   Total Test Suites: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "   Success Rate: 0%")
        print(f"   Total Time: {self.test_results['total_time']:.2f} seconds")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        
        for test_type, results in self.test_results.items():
            if test_type in ['total_time', 'timestamp']:
                continue
                
            status = "✅ PASSED" if results['success'] else "❌ FAILED"
            print(f"   {test_type.replace('_', ' ').title()}: {status}")
            
            if not results['success'] and results['error']:
                print(f"      Error: {results['error'][:100]}...")
        
        # Agentic capabilities assessment
        print(f"\n🤖 Agentic Capabilities Assessment:")
        self._assess_agentic_capabilities()
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        self._generate_recommendations()
        
        # Save detailed report
        self._save_detailed_report()
        
        print(f"\n📄 Detailed report saved to: agentic_test_report.json")
        print("=" * 60)
    
    def _assess_agentic_capabilities(self):
        """Assess the agentic capabilities based on test results"""
        capabilities = {
            'sales_detection': False,
            'token_calculation': False,
            'payment_recognition': False,
            'proactive_responses': False,
            'conversation_memory': False,
            'emotional_intelligence': False,
            'error_handling': False,
            'performance': False
        }
        
        # Analyze test outputs to determine capabilities
        for test_type, results in self.test_results.items():
            if test_type in ['total_time', 'timestamp']:
                continue
                
            if results['success']:
                output = results['output']
                
                if 'test_agentic_sales_detection' in output:
                    capabilities['sales_detection'] = True
                if 'test_token_amount_calculation' in output:
                    capabilities['token_calculation'] = True
                if 'test_payment_method_recognition' in output:
                    capabilities['payment_recognition'] = True
                if 'test_proactive_greeting_sales_offer' in output:
                    capabilities['proactive_responses'] = True
                if 'test_conversation_memory_integration' in output:
                    capabilities['conversation_memory'] = True
                if 'test_emotional_intelligence_integration' in output:
                    capabilities['emotional_intelligence'] = True
                if 'test_agentic_error_handling' in output:
                    capabilities['error_handling'] = True
                if 'test_agentic_performance_metrics' in output:
                    capabilities['performance'] = True
        
        # Display capabilities
        for capability, status in capabilities.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {capability.replace('_', ' ').title()}")
        
        # Overall agentic score
        active_capabilities = sum(capabilities.values())
        total_capabilities = len(capabilities)
        agentic_score = (active_capabilities / total_capabilities) * 100
        
        print(f"\n🎯 Overall Agentic Score: {agentic_score:.1f}%")
        
        if agentic_score >= 90:
            print("   🚀 Excellent! Bot is highly agentic and effective.")
        elif agentic_score >= 75:
            print("   👍 Good! Bot shows strong agentic capabilities.")
        elif agentic_score >= 50:
            print("   ⚠️  Fair. Some agentic features need improvement.")
        else:
            print("   ❌ Poor. Significant agentic improvements needed.")
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze failures and generate recommendations
        for test_type, results in self.test_results.items():
            if test_type in ['total_time', 'timestamp']:
                continue
                
            if not results['success']:
                if 'unit_tests' in test_type:
                    recommendations.append("🔧 Fix unit test failures in core agentic functionality")
                elif 'integration_tests' in test_type:
                    recommendations.append("🔗 Address integration issues between agentic components")
                elif 'effectiveness_tests' in test_type:
                    recommendations.append("📊 Optimize agentic effectiveness and performance")
        
        # Add general recommendations
        if not recommendations:
            recommendations.append("🎉 All tests passed! Consider adding more edge case tests")
        
        recommendations.extend([
            "📈 Monitor real-world agentic performance metrics",
            "🔄 Regularly update agentic response patterns",
            "🧠 Enhance conversation memory capabilities",
            "💡 Implement A/B testing for agentic responses"
        ])
        
        for i, recommendation in enumerate(recommendations, 1):
            print(f"   {i}. {recommendation}")
    
    def _save_detailed_report(self):
        """Save detailed test report to JSON file"""
        report = {
            'test_results': self.test_results,
            'summary': {
                'total_suites': len([k for k in self.test_results.keys() if k not in ['total_time', 'timestamp']]),
                'passed_suites': len([k for k, v in self.test_results.items() 
                                    if k not in ['total_time', 'timestamp'] and v.get('success', False)]),
                'total_time': self.test_results['total_time'],
                'timestamp': self.test_results['timestamp']
            }
        }
        
        with open('agentic_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)


def main():
    """Main function to run agentic tests"""
    runner = AgenticTestRunner()
    
    try:
        results = runner.run_tests()
        
        # Exit with appropriate code
        total_suites = len([k for k in results.keys() if k not in ['total_time', 'timestamp']])
        passed_suites = len([k for k, v in results.items() 
                           if k not in ['total_time', 'timestamp'] and v.get('success', False)])
        
        if passed_suites == total_suites:
            print("\n🎉 All agentic tests passed! Bot is ready for production.")
            sys.exit(0)
        else:
            print(f"\n⚠️  {total_suites - passed_suites} test suite(s) failed. Review and fix issues.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
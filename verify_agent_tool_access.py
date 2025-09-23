#!/usr/bin/env python
"""
Agent Tool & API Access Verification
=====================================
Ensures all agents can access the tools and APIs they need
"""

import os
import sys
import json
import redis
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

class AgentToolVerifier:
    """
    Verifies that agents have access to all required tools and APIs
    """

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
        self.results = {
            'apis_available': {},
            'tools_available': {},
            'agent_capabilities': {},
            'missing_access': [],
            'recommendations': []
        }

    def check_api_availability(self):
        """
        Check which APIs are available and working
        """
        print("\n🔑 CHECKING API AVAILABILITY")
        print("-" * 50)

        apis_to_check = {
            'OpenAI': 'OPENAI_API_KEY',
            'Anthropic': 'ANTHROPIC_API_KEY',
            'Google Gemini': 'GEMINI_API_KEY',
            'Groq': 'GROQ_API_KEY',
            'Serper (Web Search)': 'SERPER_API_KEY',
            'News API': 'NEWS_API_KEY',
            'Polygon (Market Data)': 'POLYGON_API_KEY',
            'Alpha Vantage (Finance)': 'ALPHA_VANTAGE_API_KEY',
            'Weather API': 'WEATHERAPI_KEY',
            'Stability AI (Images)': 'STABILITY_API_KEY',
            'Eleven Labs (Voice)': 'ELEVEN_LABS_API',
            'Replicate': 'REPLICATE_API_TOKEN',
            'Hugging Face': 'HUGGING_FACE_API',
            'SEC API': 'SEC_API_KEY',
            'CoinGecko (Crypto)': 'COINGECKO_API_KEY',
            'Telegram': 'TELEGRAM_API_ID',
            'Resend (Email)': 'RESEND_API_KEY'
        }

        for api_name, env_key in apis_to_check.items():
            api_key = os.getenv(env_key)
            if api_key:
                self.results['apis_available'][api_name] = {
                    'available': True,
                    'key_length': len(api_key),
                    'env_var': env_key
                }
                print(f"  ✅ {api_name:20} - Available")
            else:
                self.results['apis_available'][api_name] = {
                    'available': False,
                    'env_var': env_key
                }
                print(f"  ❌ {api_name:20} - Not configured")

        # Test critical APIs
        self._test_critical_apis()

    def _test_critical_apis(self):
        """
        Test that critical APIs are actually working
        """
        print("\n🧪 TESTING CRITICAL APIs")
        print("-" * 50)

        # Test OpenAI
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), timeout=5.0)
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'user', 'content': 'test'}],
                max_tokens=5
            )
            self.results['apis_available']['OpenAI']['tested'] = True
            self.results['apis_available']['OpenAI']['working'] = True
            print("  ✅ OpenAI API - Working")
        except Exception as e:
            self.results['apis_available']['OpenAI']['tested'] = True
            self.results['apis_available']['OpenAI']['working'] = False
            self.results['apis_available']['OpenAI']['error'] = str(e)
            print(f"  ❌ OpenAI API - Failed: {e}")

        # Test News API
        try:
            import requests
            response = requests.get(
                'https://newsapi.org/v2/top-headlines',
                params={
                    'country': 'us',
                    'apiKey': os.getenv('NEWS_API_KEY'),
                    'pageSize': 1
                },
                timeout=5
            )
            if response.status_code == 200:
                self.results['apis_available']['News API']['tested'] = True
                self.results['apis_available']['News API']['working'] = True
                print("  ✅ News API - Working")
            else:
                raise Exception(f"Status code: {response.status_code}")
        except Exception as e:
            self.results['apis_available']['News API']['tested'] = True
            self.results['apis_available']['News API']['working'] = False
            print(f"  ❌ News API - Failed: {e}")

    def check_tool_availability(self):
        """
        Check which tools are available to agents
        """
        print("\n🔧 CHECKING TOOL AVAILABILITY")
        print("-" * 50)

        tools = {
            'Redis': self._check_redis,
            'File System': self._check_filesystem,
            'Web Requests': self._check_web_requests,
            'WebSocket': self._check_websocket,
            'JSON Processing': self._check_json,
            'Regular Expressions': self._check_regex,
            'Datetime': self._check_datetime,
            'Math Operations': self._check_math,
            'String Operations': self._check_string_ops,
            'Data Structures': self._check_data_structures
        }

        for tool_name, check_func in tools.items():
            try:
                result = check_func()
                self.results['tools_available'][tool_name] = {
                    'available': result,
                    'status': 'working' if result else 'failed'
                }
                status = "✅" if result else "❌"
                print(f"  {status} {tool_name:20} - {'Available' if result else 'Not available'}")
            except Exception as e:
                self.results['tools_available'][tool_name] = {
                    'available': False,
                    'error': str(e)
                }
                print(f"  ❌ {tool_name:20} - Error: {e}")

    def _check_redis(self):
        """Check Redis availability"""
        try:
            self.redis.ping()
            self.redis.set('test:tool_check', 'working')
            value = self.redis.get('test:tool_check')
            self.redis.delete('test:tool_check')
            return value == 'working'
        except:
            return False

    def _check_filesystem(self):
        """Check file system access"""
        try:
            test_file = '/tmp/agent_test.txt'
            with open(test_file, 'w') as f:
                f.write('test')
            with open(test_file, 'r') as f:
                content = f.read()
            os.remove(test_file)
            return content == 'test'
        except:
            return False

    def _check_web_requests(self):
        """Check web request capability"""
        try:
            import requests
            response = requests.get('https://api.github.com', timeout=5)
            return response.status_code == 200
        except:
            return False

    def _check_websocket(self):
        """Check WebSocket capability"""
        try:
            import websocket
            return True
        except ImportError:
            return False

    def _check_json(self):
        """Check JSON processing"""
        try:
            test_data = {'test': 'data'}
            json_str = json.dumps(test_data)
            parsed = json.loads(json_str)
            return parsed == test_data
        except:
            return False

    def _check_regex(self):
        """Check regular expression support"""
        try:
            import re
            pattern = re.compile(r'\d+')
            matches = pattern.findall('test 123 data')
            return matches == ['123']
        except:
            return False

    def _check_datetime(self):
        """Check datetime operations"""
        try:
            from datetime import datetime, timedelta
            now = datetime.now()
            future = now + timedelta(days=1)
            return future > now
        except:
            return False

    def _check_math(self):
        """Check math operations"""
        try:
            import math
            return math.sqrt(16) == 4.0
        except:
            return False

    def _check_string_ops(self):
        """Check string operations"""
        try:
            test_str = "Hello World"
            return (test_str.lower() == "hello world" and
                    test_str.upper() == "HELLO WORLD" and
                    test_str.split() == ["Hello", "World"])
        except:
            return False

    def _check_data_structures(self):
        """Check data structure operations"""
        try:
            # Lists
            lst = [1, 2, 3]
            lst.append(4)

            # Dictionaries
            dct = {'a': 1, 'b': 2}
            dct['c'] = 3

            # Sets
            st = {1, 2, 3}
            st.add(4)

            return len(lst) == 4 and len(dct) == 3 and len(st) == 4
        except:
            return False

    def check_agent_capabilities(self):
        """
        Map which agents need which tools/APIs
        """
        print("\n🤖 AGENT CAPABILITY REQUIREMENTS")
        print("-" * 50)

        agent_requirements = {
            'Content Creator': {
                'apis': ['OpenAI', 'News API'],
                'tools': ['Redis', 'JSON Processing', 'File System']
            },
            'Market Analyst': {
                'apis': ['Polygon', 'Alpha Vantage', 'News API'],
                'tools': ['Redis', 'Web Requests', 'JSON Processing']
            },
            'Skill Advisor': {
                'apis': ['OpenAI'],
                'tools': ['Redis', 'JSON Processing']
            },
            'Spider Agents': {
                'apis': ['Serper', 'News API'],
                'tools': ['Web Requests', 'Redis', 'Regular Expressions']
            },
            'Job Finder': {
                'apis': ['Serper', 'OpenAI'],
                'tools': ['Web Requests', 'JSON Processing', 'Redis']
            },
            'Revenue Tracker': {
                'apis': ['Polygon', 'CoinGecko'],
                'tools': ['Redis', 'Math Operations', 'Datetime']
            },
            'Email Sender': {
                'apis': ['Resend'],
                'tools': ['String Operations', 'File System']
            },
            'Voice Generator': {
                'apis': ['Eleven Labs'],
                'tools': ['File System', 'Web Requests']
            },
            'Image Creator': {
                'apis': ['Stability AI', 'Replicate'],
                'tools': ['File System', 'Web Requests']
            },
            'Trend Predictor': {
                'apis': ['OpenAI', 'News API', 'Polygon'],
                'tools': ['Redis', 'Math Operations', 'Datetime']
            }
        }

        for agent, requirements in agent_requirements.items():
            print(f"\n  📋 {agent}")

            all_apis_available = True
            all_tools_available = True

            # Check required APIs
            print(f"     Required APIs:")
            for api in requirements['apis']:
                if api in self.results['apis_available']:
                    available = self.results['apis_available'][api].get('available', False)
                    working = self.results['apis_available'][api].get('working', None)

                    if available and working:
                        print(f"       ✅ {api}")
                    elif available and working is False:
                        print(f"       ⚠️ {api} - Key present but not working")
                        all_apis_available = False
                    elif available:
                        print(f"       ✓ {api} - Key present (not tested)")
                    else:
                        print(f"       ❌ {api} - Missing")
                        all_apis_available = False
                        self.results['missing_access'].append(f"{agent} needs {api}")

            # Check required tools
            print(f"     Required Tools:")
            for tool in requirements['tools']:
                if tool in self.results['tools_available']:
                    available = self.results['tools_available'][tool].get('available', False)
                    if available:
                        print(f"       ✅ {tool}")
                    else:
                        print(f"       ❌ {tool}")
                        all_tools_available = False
                        self.results['missing_access'].append(f"{agent} needs {tool}")

            # Store capability status
            self.results['agent_capabilities'][agent] = {
                'apis_ready': all_apis_available,
                'tools_ready': all_tools_available,
                'fully_operational': all_apis_available and all_tools_available
            }

            status = "✅ Fully Operational" if (all_apis_available and all_tools_available) else "⚠️ Partially Operational"
            print(f"     Status: {status}")

    def generate_recommendations(self):
        """
        Generate recommendations based on findings
        """
        print("\n💡 RECOMMENDATIONS")
        print("-" * 50)

        # Check for critical missing APIs
        critical_apis = ['OpenAI', 'News API']
        for api in critical_apis:
            if not self.results['apis_available'].get(api, {}).get('available', False):
                self.results['recommendations'].append(
                    f"Critical: Configure {api} for core functionality"
                )

        # Check for enhancement APIs
        enhancement_apis = ['Serper', 'Polygon', 'Stability AI']
        for api in enhancement_apis:
            if not self.results['apis_available'].get(api, {}).get('available', False):
                self.results['recommendations'].append(
                    f"Enhancement: Add {api} for extended capabilities"
                )

        # Check for non-operational agents
        for agent, status in self.results['agent_capabilities'].items():
            if not status['fully_operational']:
                if not status['apis_ready']:
                    self.results['recommendations'].append(
                        f"Fix: {agent} needs API configuration"
                    )
                if not status['tools_ready']:
                    self.results['recommendations'].append(
                        f"Fix: {agent} missing required tools"
                    )

        if self.results['recommendations']:
            for rec in self.results['recommendations']:
                print(f"  • {rec}")
        else:
            print("  ✨ All systems optimal - no recommendations")

    def save_report(self):
        """
        Save verification report to file
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_apis': len(self.results['apis_available']),
                'available_apis': sum(1 for api in self.results['apis_available'].values() if api.get('available')),
                'working_apis': sum(1 for api in self.results['apis_available'].values() if api.get('working')),
                'total_tools': len(self.results['tools_available']),
                'available_tools': sum(1 for tool in self.results['tools_available'].values() if tool.get('available')),
                'total_agents': len(self.results['agent_capabilities']),
                'operational_agents': sum(1 for agent in self.results['agent_capabilities'].values() if agent.get('fully_operational'))
            },
            'details': self.results
        }

        with open('agent_tool_access_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        # Also save to Redis
        self.redis.set('agent:tool:verification', json.dumps(report))

        return report

    def run_verification(self):
        """
        Run complete verification
        """
        print("=" * 60)
        print("🔍 AGENT TOOL & API ACCESS VERIFICATION")
        print("=" * 60)
        print(f"Time: {datetime.now()}")

        self.check_api_availability()
        self.check_tool_availability()
        self.check_agent_capabilities()
        self.generate_recommendations()

        report = self.save_report()

        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("-" * 50)
        print(f"APIs Available: {report['summary']['available_apis']}/{report['summary']['total_apis']}")
        print(f"APIs Working: {report['summary']['working_apis']}/{report['summary']['available_apis']}")
        print(f"Tools Available: {report['summary']['available_tools']}/{report['summary']['total_tools']}")
        print(f"Agents Operational: {report['summary']['operational_agents']}/{report['summary']['total_agents']}")

        if report['summary']['operational_agents'] == report['summary']['total_agents']:
            print("\n✅ All agents have required tool and API access!")
        else:
            print(f"\n⚠️ {report['summary']['total_agents'] - report['summary']['operational_agents']} agents need attention")

        print("\n📄 Full report saved to: agent_tool_access_report.json")
        print("=" * 60)

        return report


if __name__ == "__main__":
    verifier = AgentToolVerifier()
    report = verifier.run_verification()
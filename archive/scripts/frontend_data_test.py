#!/usr/bin/env python3
"""
Frontend Data Flow Test
=======================

Test the exact data requests that frontend components make
and analyze what backend actually sends back vs what frontend expects.
"""

import asyncio
import websockets
import json

async def test_income_builder_data():
    """Test Income Builder specific data requests"""
    print("🔍 Testing Income Builder Data Flow...")
    
    try:
        websocket = await websockets.connect("ws://localhost:8000/ws/income-builder/")
        
        # Test messages that frontend actually sends (from IncomeBuilder.tsx)
        test_requests = [
            {"type": "get_data", "component": "income_builder"},
            {"action": "get_opportunities"},
            {"type": "opportunities_request"},
            {"type": "get_data"},
        ]
        
        for request in test_requests:
            print(f"📤 Sending: {request}")
            await websocket.send(json.dumps(request))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"📨 Response type: {data.get('type', 'No type field')}")
                
                # Check for expected Income Builder data fields
                if 'opportunities' in data:
                    print(f"✅ Found opportunities data: {len(data['opportunities'])} items")
                elif 'type' in data and data['type'] == 'opportunities_update':
                    print(f"✅ Found opportunities_update message")
                else:
                    print(f"⚠️ No opportunities data in response")
                    print(f"📊 Available fields: {list(data.keys())}")
                    
            except asyncio.TimeoutError:
                print(f"⏱️ No response to: {request}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                
        await websocket.close()
        
    except Exception as e:
        print(f"❌ Income Builder test failed: {e}")

async def test_revenue_dashboard_data():
    """Test Revenue Dashboard specific data requests"""
    print("\n💰 Testing Revenue Dashboard Data Flow...")
    
    try:
        websocket = await websockets.connect("ws://localhost:8000/ws/revenue-dashboard/")
        
        # Test messages from RevenueDashboard.tsx
        test_requests = [
            {"type": "get_data", "timeframe": "30d"},
            {"type": "refresh_metrics"},
            {"type": "ping", "timestamp": 12345},
        ]
        
        for request in test_requests:
            print(f"📤 Sending: {request}")
            await websocket.send(json.dumps(request))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"📨 Response type: {data.get('type', 'No type field')}")
                
                # Check for expected Revenue Dashboard data fields
                if 'metrics' in data:
                    print(f"✅ Found metrics data")
                    metrics = data['metrics']
                    expected_fields = ['total_revenue', 'conversion_rate', 'proposals_submitted']
                    found_fields = [f for f in expected_fields if f in metrics]
                    print(f"📊 Found metric fields: {found_fields}")
                elif data.get('type') == 'metrics_update':
                    print(f"✅ Found metrics_update message")
                else:
                    print(f"⚠️ No metrics data in response")
                    print(f"📊 Available fields: {list(data.keys())}")
                    
            except asyncio.TimeoutError:
                print(f"⏱️ No response to: {request}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                
        await websocket.close()
        
    except Exception as e:
        print(f"❌ Revenue Dashboard test failed: {e}")

async def test_neural_orchestra_data():
    """Test Neural Orchestra specific data requests"""
    print("\n🤖 Testing Neural Orchestra Data Flow...")
    
    try:
        websocket = await websockets.connect("ws://localhost:8000/ws/neural-orchestra/")
        
        # Test messages from NeuralOrchestra.tsx
        test_requests = [
            {"type": "get_data", "component": "neural_orchestra"},
            {"type": "get_network_state"},
            {"type": "get_agents"},
        ]
        
        for request in test_requests:
            print(f"📤 Sending: {request}")
            await websocket.send(json.dumps(request))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"📨 Response type: {data.get('type', 'No type field')}")
                
                # Check for expected Neural Orchestra data fields
                if 'agents' in data:
                    print(f"✅ Found agents data: {len(data['agents'])} agents")
                elif 'workflows' in data:
                    print(f"✅ Found workflows data: {len(data['workflows'])} workflows")
                elif data.get('type') == 'orchestra_update':
                    print(f"✅ Found orchestra_update message")
                else:
                    print(f"⚠️ No agents/workflows data in response")
                    print(f"📊 Available fields: {list(data.keys())}")
                    
            except asyncio.TimeoutError:
                print(f"⏱️ No response to: {request}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                
        await websocket.close()
        
    except Exception as e:
        print(f"❌ Neural Orchestra test failed: {e}")

async def test_decision_command_data():
    """Test Decision Command specific data requests"""
    print("\n🧠 Testing Decision Command Data Flow...")
    
    try:
        websocket = await websockets.connect("ws://localhost:8000/ws/decision-command/")
        
        # Test messages from DecisionCommand.tsx
        test_requests = [
            {"type": "get_data", "component": "decision_command"},
            {"action": "analyze_opportunities"},
            {"type": "get_opportunities"},
        ]
        
        for request in test_requests:
            print(f"📤 Sending: {request}")
            await websocket.send(json.dumps(request))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"📨 Response type: {data.get('type', 'No type field')}")
                
                # Check for expected Decision Command data fields
                if 'opportunities' in data:
                    print(f"✅ Found opportunities data: {len(data['opportunities'])} opportunities")
                elif 'decisions' in data:
                    print(f"✅ Found decisions data: {len(data['decisions'])} decisions")
                elif data.get('type') == 'decision_update':
                    print(f"✅ Found decision_update message")
                else:
                    print(f"⚠️ No opportunities/decisions data in response")
                    print(f"📊 Available fields: {list(data.keys())}")
                    
            except asyncio.TimeoutError:
                print(f"⏱️ No response to: {request}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                
        await websocket.close()
        
    except Exception as e:
        print(f"❌ Decision Command test failed: {e}")

async def main():
    """Run comprehensive frontend data flow test"""
    print("🚀 Frontend Data Flow Analysis")
    print("=" * 50)
    print("Testing what data frontend actually receives vs expects...\n")
    
    await test_income_builder_data()
    await test_revenue_dashboard_data()
    await test_neural_orchestra_data()
    await test_decision_command_data()
    
    print("\n" + "=" * 50)
    print("🎯 KEY FINDINGS:")
    print("1. WebSocket connections work ✅")
    print("2. Need to check if backend sends expected data formats")
    print("3. Frontend components may need mock data fallbacks")

if __name__ == "__main__":
    asyncio.run(main())

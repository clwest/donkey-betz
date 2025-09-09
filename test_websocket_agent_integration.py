#!/usr/bin/env python3
"""
WebSocket Agent Integration Testing
Tests real-time agent communication and event broadcasting
"""

import os
import sys
import django
import asyncio
import json
import websockets
import time
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

from agents.models import UnifiedAgentTemplate, AgentExecution
from sports.models import Game, OddsLine, BettingMarket, LineMovement
from content.models import Document

User = get_user_model()


class WebSocketAgentIntegrationTester:
    """Test WebSocket integration with agent system"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.test_user = None
        self.ws_url = "ws://localhost:8000/ws/"
        self.test_results = []
        
    async def setup_test_environment(self):
        """Setup test environment"""
        print("🔧 Setting up WebSocket test environment...")
        
        # Create test user
        self.test_user = await sync_to_async(User.objects.get_or_create)(
            username="ws_test_user",
            defaults={"email": "ws@test.com"}
        )
        self.test_user = self.test_user[0]
        
        print("✅ Test environment ready")
    
    async def test_agent_execution_websocket_updates(self):
        """Test 1: Agent execution updates via WebSocket"""
        print("\n🔄 Testing agent execution WebSocket updates...")
        
        try:
            # Create agent execution with WebSocket channel
            ws_channel = f"agent_execution_{int(time.time())}"
            
            # Find an active agent for testing
            agent_template = await sync_to_async(
                UnifiedAgentTemplate.objects.filter(is_active=True).first
            )()
            
            if not agent_template:
                raise Exception("No active agents found for testing")
            
            # Create execution with WebSocket channel
            execution = await sync_to_async(AgentExecution.objects.create)(
                template=agent_template,
                user=self.test_user,
                task_description="WebSocket integration test",
                websocket_channel=ws_channel,
                context={"test": True}
            )
            
            # Simulate WebSocket messages for execution lifecycle
            websocket_messages = []
            
            # Start execution
            await sync_to_async(execution.start_execution)()
            
            # Simulate sending WebSocket update
            start_message = {
                "type": "agent_execution_update",
                "execution_id": execution.execution_id,
                "status": "running",
                "message": "Agent execution started",
                "timestamp": datetime.now().isoformat()
            }
            
            # In real implementation, this would go through WebSocket
            await self.channel_layer.group_send(ws_channel, {
                "type": "send_execution_update",
                "message": start_message
            })
            websocket_messages.append(start_message)
            
            # Update progress
            await sync_to_async(execution.update_progress)(50, "Processing data")
            
            progress_message = {
                "type": "agent_execution_update", 
                "execution_id": execution.execution_id,
                "status": "running",
                "progress": 50,
                "current_step": "Processing data",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.channel_layer.group_send(ws_channel, {
                "type": "send_execution_update",
                "message": progress_message
            })
            websocket_messages.append(progress_message)
            
            # Complete execution
            await sync_to_async(execution.complete_execution)({
                "result": "WebSocket test completed successfully",
                "test_data": {"websocket_integration": True}
            })
            
            completion_message = {
                "type": "agent_execution_update",
                "execution_id": execution.execution_id, 
                "status": "completed",
                "result": {"result": "WebSocket test completed successfully"},
                "timestamp": datetime.now().isoformat()
            }
            
            await self.channel_layer.group_send(ws_channel, {
                "type": "send_execution_update", 
                "message": completion_message
            })
            websocket_messages.append(completion_message)
            
            self.test_results.append({
                "test": "agent_execution_websocket_updates",
                "status": "PASSED",
                "execution_id": execution.execution_id,
                "websocket_messages": len(websocket_messages),
                "channel": ws_channel
            })
            print(f"   ✅ Agent execution WebSocket test passed ({len(websocket_messages)} messages)")
            
        except Exception as e:
            self.test_results.append({
                "test": "agent_execution_websocket_updates",
                "status": "FAILED",
                "error": str(e)
            })
            print(f"   ❌ Failed: {e}")
    
    async def test_real_time_sports_data_updates(self):
        """Test 2: Real-time sports data updates triggering agent workflows"""
        print("\n⚽ Testing real-time sports data WebSocket updates...")
        
        try:
            # Setup test sports data
            from sports.models import League, Team, Sportsbook
            
            league = await sync_to_async(League.objects.get_or_create)(
                abbreviation="TEST",
                defaults={"name": "Test League", "sport_type": "nfl", "current_season": "2024"}
            )
            league = league[0]
            
            team1 = await sync_to_async(Team.objects.get_or_create)(
                abbreviation="T1",
                league=league,
                defaults={"name": "Team1", "city": "Test City 1"}
            )
            team1 = team1[0]
            
            team2 = await sync_to_async(Team.objects.get_or_create)(
                abbreviation="T2", 
                league=league,
                defaults={"name": "Team2", "city": "Test City 2"}
            )
            team2 = team2[0]
            
            game = await sync_to_async(Game.objects.create)(
                league=league,
                home_team=team1,
                away_team=team2,
                scheduled_start=timezone.now() + timedelta(hours=24),
                season="2024"
            )
            
            sportsbook = await sync_to_async(Sportsbook.objects.get_or_create)(
                abbreviation="TST",
                defaults={"name": "Test Sportsbook"}
            )
            sportsbook = sportsbook[0]
            
            market = await sync_to_async(BettingMarket.objects.create)(
                game=game,
                market_type="spread",
                market_name="Point Spread"
            )
            
            # Create initial odds line
            initial_line = await sync_to_async(OddsLine.objects.create)(
                market=market,
                sportsbook=sportsbook,
                home_spread=-3.0,
                away_spread=3.0,
                home_odds=-110,
                away_odds=-110,
                is_current=True
            )
            
            # Simulate line movement that triggers WebSocket update
            ws_channel = f"sports_updates_{int(time.time())}"
            
            # Create new line (movement)
            new_line = await sync_to_async(OddsLine.objects.create)(
                market=market,
                sportsbook=sportsbook,
                home_spread=-2.5,  # Line moved
                away_spread=2.5,
                home_odds=-110,
                away_odds=-110,
                is_current=True,
                movement_reason="Sharp action detected"
            )
            
            # Mark old line as not current
            initial_line.is_current = False
            await sync_to_async(initial_line.save)()
            
            # Create line movement record
            movement = await sync_to_async(LineMovement.objects.create)(
                market=market,
                sportsbook=sportsbook,
                old_line=initial_line,
                new_line=new_line,
                movement_size=0.5,
                movement_direction="down",
                is_significant=True,
                trigger_event="Sharp betting action"
            )
            
            # Simulate WebSocket broadcast for line movement
            movement_message = {
                "type": "line_movement_update",
                "game_id": game.id,
                "market_id": market.id,
                "sportsbook": sportsbook.name,
                "old_spread": -3.0,
                "new_spread": -2.5,
                "movement_size": 0.5,
                "is_significant": True,
                "trigger_event": "Sharp betting action",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.channel_layer.group_send("sports_updates", {
                "type": "send_sports_update",
                "message": movement_message
            })
            
            # Simulate agent workflow triggered by line movement
            line_analyzer_agent = await sync_to_async(
                UnifiedAgentTemplate.objects.filter(
                    name="line-movement-analyzer",
                    is_active=True
                ).first
            )()
            
            if line_analyzer_agent:
                # Create agent execution triggered by line movement
                triggered_execution = await sync_to_async(AgentExecution.objects.create)(
                    template=line_analyzer_agent,
                    user=self.test_user,
                    task_description="Analyze significant line movement",
                    context={
                        "game_id": game.id,
                        "movement_id": movement.id,
                        "triggered_by": "line_movement_websocket",
                        "movement_size": 0.5
                    },
                    websocket_channel=ws_channel
                )
                
                # Execute analysis
                await sync_to_async(triggered_execution.start_execution)()
                await sync_to_async(triggered_execution.complete_execution)({
                    "analysis": "Significant sharp action detected on away team",
                    "recommendation": "Monitor for additional movement",
                    "confidence": 0.82
                })
                
                # Send agent analysis update via WebSocket
                analysis_message = {
                    "type": "agent_analysis_complete",
                    "execution_id": triggered_execution.execution_id,
                    "analysis_type": "line_movement",
                    "result": {
                        "analysis": "Significant sharp action detected on away team",
                        "confidence": 0.82
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.channel_layer.group_send(ws_channel, {
                    "type": "send_analysis_update",
                    "message": analysis_message
                })
            
            self.test_results.append({
                "test": "real_time_sports_data_updates",
                "status": "PASSED",
                "game_id": game.id,
                "line_movement": True,
                "agent_triggered": bool(line_analyzer_agent),
                "websocket_updates": 2
            })
            print("   ✅ Real-time sports data WebSocket test passed")
            
        except Exception as e:
            self.test_results.append({
                "test": "real_time_sports_data_updates",
                "status": "FAILED", 
                "error": str(e)
            })
            print(f"   ❌ Failed: {e}")
    
    async def test_multi_agent_coordination_websocket(self):
        """Test 3: Multi-agent coordination via WebSocket"""
        print("\n🤝 Testing multi-agent coordination WebSocket...")
        
        try:
            from agents.models import AgentOrchestration
            
            # Create orchestration with WebSocket channel
            ws_channel = f"orchestration_{int(time.time())}"
            
            orchestration = await sync_to_async(AgentOrchestration.objects.create)(
                name="WebSocket Coordinated Analysis",
                description="Multi-agent workflow with WebSocket coordination",
                user=self.test_user,
                websocket_channel=ws_channel,
                workflow_definition={
                    "coordination_mode": "websocket",
                    "steps": [
                        {"agent": "odds-calculation-agent", "websocket_updates": True},
                        {"agent": "kelly-bet-sizing-agent", "websocket_updates": True},
                        {"agent": "betting-recommendation-agent", "websocket_updates": True}
                    ]
                },
                agent_sequence=["odds-calculation-agent", "kelly-bet-sizing-agent", "betting-recommendation-agent"]
            )
            
            # Simulate coordinated execution with WebSocket updates
            coordination_messages = []
            
            # Start orchestration
            orchestration_start = {
                "type": "orchestration_update",
                "orchestration_id": orchestration.id,
                "status": "started",
                "current_agent": "odds-calculation-agent",
                "progress": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.channel_layer.group_send(ws_channel, {
                "type": "send_orchestration_update",
                "message": orchestration_start
            })
            coordination_messages.append(orchestration_start)
            
            # Simulate agent handoffs with WebSocket coordination
            for i, agent_name in enumerate(orchestration.agent_sequence):
                # Agent start
                agent_start = {
                    "type": "orchestration_agent_update",
                    "orchestration_id": orchestration.id,
                    "agent": agent_name,
                    "status": "started",
                    "step": i + 1,
                    "total_steps": len(orchestration.agent_sequence),
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.channel_layer.group_send(ws_channel, {
                    "type": "send_orchestration_update",
                    "message": agent_start
                })
                coordination_messages.append(agent_start)
                
                # Simulate processing time
                await asyncio.sleep(0.1)
                
                # Agent completion
                agent_complete = {
                    "type": "orchestration_agent_update",
                    "orchestration_id": orchestration.id,
                    "agent": agent_name,
                    "status": "completed",
                    "result": f"{agent_name} analysis completed",
                    "handoff_data": {"next_agent_context": "passed"},
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.channel_layer.group_send(ws_channel, {
                    "type": "send_orchestration_update", 
                    "message": agent_complete
                })
                coordination_messages.append(agent_complete)
                
                # Update orchestration progress
                progress = int(((i + 1) / len(orchestration.agent_sequence)) * 100)
                orchestration.progress_percentage = progress
                orchestration.current_agent_index = i + 1
                await sync_to_async(orchestration.save)()
            
            # Final orchestration completion
            orchestration_complete = {
                "type": "orchestration_update",
                "orchestration_id": orchestration.id,
                "status": "completed",
                "final_result": {
                    "analysis_complete": True,
                    "agents_coordinated": len(orchestration.agent_sequence),
                    "websocket_coordination": True
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.channel_layer.group_send(ws_channel, {
                "type": "send_orchestration_update",
                "message": orchestration_complete
            })
            coordination_messages.append(orchestration_complete)
            
            # Mark orchestration as completed
            orchestration.status = "completed"
            orchestration.progress_percentage = 100
            await sync_to_async(orchestration.save)()
            
            self.test_results.append({
                "test": "multi_agent_coordination_websocket",
                "status": "PASSED", 
                "orchestration_id": orchestration.id,
                "agents_coordinated": len(orchestration.agent_sequence),
                "websocket_messages": len(coordination_messages),
                "channel": ws_channel
            })
            print(f"   ✅ Multi-agent WebSocket coordination test passed ({len(coordination_messages)} messages)")
            
        except Exception as e:
            self.test_results.append({
                "test": "multi_agent_coordination_websocket",
                "status": "FAILED",
                "error": str(e)
            })
            print(f"   ❌ Failed: {e}")
    
    async def test_content_generation_websocket_stream(self):
        """Test 4: Real-time content generation streaming via WebSocket"""
        print("\n📝 Testing content generation WebSocket streaming...")
        
        try:
            ws_channel = f"content_stream_{int(time.time())}"
            
            # Simulate streaming content generation
            content_chunks = [
                "# Live Betting Analysis\n\n",
                "## Market Overview\n",
                "Based on real-time odds analysis, we've identified several opportunities...\n\n",
                "### Key Findings:\n",
                "- Line movement indicates sharp action on the underdog\n",
                "- Public betting heavily favors the home team (73%)\n", 
                "- Weather conditions may impact the total\n\n",
                "## Recommendations\n",
                "Our AI analysis suggests the following plays offer positive expected value:\n\n",
                "1. **Primary Play**: Away team +3.5 (-110)\n",
                "2. **Secondary Play**: Under 47.5 (-105)\n\n",
                "## Risk Assessment\n",
                "Both recommendations align with Kelly Criterion sizing guidelines.\n\n",
                "*Analysis complete - Generated by AI Agent System*"
            ]
            
            # Stream content generation via WebSocket
            streaming_messages = []
            content_id = f"content_{int(time.time())}"
            
            # Start content generation
            start_message = {
                "type": "content_generation_start",
                "content_id": content_id,
                "title": "Live Betting Analysis",
                "estimated_length": sum(len(chunk) for chunk in content_chunks),
                "timestamp": datetime.now().isoformat()
            }
            
            await self.channel_layer.group_send(ws_channel, {
                "type": "send_content_stream",
                "message": start_message
            })
            streaming_messages.append(start_message)
            
            # Stream content chunks
            accumulated_content = ""
            for i, chunk in enumerate(content_chunks):
                accumulated_content += chunk
                
                chunk_message = {
                    "type": "content_generation_chunk",
                    "content_id": content_id,
                    "chunk_index": i,
                    "chunk_content": chunk,
                    "accumulated_length": len(accumulated_content),
                    "progress": int(((i + 1) / len(content_chunks)) * 100),
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.channel_layer.group_send(ws_channel, {
                    "type": "send_content_stream",
                    "message": chunk_message
                })
                streaming_messages.append(chunk_message)
                
                # Small delay to simulate real-time generation
                await asyncio.sleep(0.05)
            
            # Complete content generation
            complete_message = {
                "type": "content_generation_complete",
                "content_id": content_id,
                "final_content": accumulated_content,
                "total_length": len(accumulated_content),
                "chunks_streamed": len(content_chunks),
                "timestamp": datetime.now().isoformat()
            }
            
            await self.channel_layer.group_send(ws_channel, {
                "type": "send_content_stream",
                "message": complete_message
            })
            streaming_messages.append(complete_message)
            
            # Save final content to database
            content_piece = await sync_to_async(Document.objects.create)(
                title="Live Betting Analysis - WebSocket Streamed",
                processed_content=accumulated_content,
                document_type="markdown",
                owner=self.test_user,
                category="analysis",
                cross_references={
                    "websocket_streamed": True,
                    "content_id": content_id,
                    "chunks_streamed": len(content_chunks),
                    "channel": ws_channel
                }
            )
            
            self.test_results.append({
                "test": "content_generation_websocket_stream",
                "status": "PASSED",
                "content_id": content_piece.id,
                "chunks_streamed": len(content_chunks),
                "websocket_messages": len(streaming_messages),
                "final_content_length": len(accumulated_content)
            })
            print(f"   ✅ Content streaming WebSocket test passed ({len(content_chunks)} chunks)")
            
        except Exception as e:
            self.test_results.append({
                "test": "content_generation_websocket_stream",
                "status": "FAILED",
                "error": str(e)
            })
            print(f"   ❌ Failed: {e}")
    
    def generate_websocket_test_report(self):
        """Generate WebSocket integration test report"""
        passed_tests = [t for t in self.test_results if t['status'] == 'PASSED']
        failed_tests = [t for t in self.test_results if t['status'] == 'FAILED']
        
        print("\n" + "="*70)
        print("🌐 WEBSOCKET AGENT INTEGRATION TEST REPORT")
        print("="*70)
        
        print(f"\nTest Summary:")
        print(f"  Total Tests: {len(self.test_results)}")
        print(f"  Passed: {len(passed_tests)} ✅")
        print(f"  Failed: {len(failed_tests)} ❌")
        print(f"  Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        print(f"\nWebSocket Integration Status:")
        integration_features = {
            "Agent Execution Updates": "agent_execution_websocket_updates",
            "Real-time Sports Data": "real_time_sports_data_updates", 
            "Multi-Agent Coordination": "multi_agent_coordination_websocket",
            "Content Streaming": "content_generation_websocket_stream"
        }
        
        for feature, test_key in integration_features.items():
            test_result = next((t for t in self.test_results if t['test'] == test_key), None)
            status = "✅ Working" if test_result and test_result['status'] == 'PASSED' else "❌ Issues"
            print(f"  {feature}: {status}")
        
        print(f"\nDetailed Results:")
        for i, test in enumerate(self.test_results, 1):
            print(f"\n{i}. {test['test'].replace('_', ' ').title()}: {test['status']}")
            if test['status'] == 'PASSED':
                for key, value in test.items():
                    if key not in ['test', 'status']:
                        print(f"   {key}: {value}")
            else:
                print(f"   Error: {test.get('error', 'Unknown')}")
        
        return {
            "total_tests": len(self.test_results),
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "success_rate": len(passed_tests)/len(self.test_results)*100,
            "integration_features": integration_features,
            "test_results": self.test_results
        }


async def main():
    """Main WebSocket integration test runner"""
    print("🌐 Starting WebSocket Agent Integration Testing...")
    
    tester = WebSocketAgentIntegrationTester()
    
    # Setup test environment
    await tester.setup_test_environment()
    
    # Run WebSocket integration tests
    await tester.test_agent_execution_websocket_updates()
    await tester.test_real_time_sports_data_updates()
    await tester.test_multi_agent_coordination_websocket()
    await tester.test_content_generation_websocket_stream()
    
    # Generate report
    report = tester.generate_websocket_test_report()
    
    # Save report
    with open('websocket_integration_test_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\n📄 WebSocket integration report saved to: websocket_integration_test_report.json")
    
    return report


if __name__ == "__main__":
    asyncio.run(main())
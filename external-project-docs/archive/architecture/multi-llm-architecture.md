<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-LLM Agent Teams Architecture</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #e0e0e0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            color: #00ff88;
            margin-bottom: 40px;
        }
        
        .architecture {
            background: #1a1a1a;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.1);
        }
        
        .layer {
            margin-bottom: 40px;
            padding: 20px;
            background: #222;
            border-radius: 8px;
            border: 1px solid #333;
        }
        
        .layer-title {
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 15px;
        }
        
        .components {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .component {
            flex: 1;
            min-width: 200px;
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 15px;
            transition: all 0.3s ease;
        }
        
        .component:hover {
            border-color: #00ff88;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
            transform: translateY(-2px);
        }
        
        .component-title {
            font-weight: bold;
            color: #fff;
            margin-bottom: 8px;
        }
        
        .component-desc {
            font-size: 14px;
            color: #999;
            line-height: 1.5;
        }
        
        .flow-arrow {
            text-align: center;
            font-size: 24px;
            color: #00ff88;
            margin: 20px 0;
        }
        
        .experiment-flow {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 25px;
            margin-top: 30px;
        }
        
        .flow-step {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            gap: 20px;
        }
        
        .step-number {
            width: 40px;
            height: 40px;
            background: #00ff88;
            color: #000;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }
        
        .step-content {
            flex: 1;
        }
        
        .step-title {
            font-weight: bold;
            color: #fff;
            margin-bottom: 5px;
        }
        
        .step-desc {
            color: #999;
            font-size: 14px;
        }
        
        .team-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }
        
        .team {
            background: #222;
            border-radius: 8px;
            padding: 20px;
            border: 2px solid #333;
        }
        
        .team.homogeneous {
            border-color: #0088ff;
        }
        
        .team.heterogeneous {
            border-color: #ff0088;
        }
        
        .team-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .agent-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .agent-item {
            background: #2a2a2a;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .llm-badge {
            background: #444;
            color: #fff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .llm-badge.openai { background: #74aa9c; }
        .llm-badge.anthropic { background: #d4a574; }
        .llm-badge.ollama { background: #9474d4; }
        .llm-badge.google { background: #4285f4; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Multi-LLM Agent Teams Architecture</h1>
        
        <div class="architecture">
            <div class="layer">
                <div class="layer-title">🎯 Experiment Layer</div>
                <div class="components">
                    <div class="component">
                        <div class="component-title">Mythology Lab UI</div>
                        <div class="component-desc">Configure teams, select LLMs, design experiments</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Experiment Runner</div>
                        <div class="component-desc">Orchestrate team execution, track mythology propagation</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Results Analyzer</div>
                        <div class="component-desc">Compare team performance, cross-model friction metrics</div>
                    </div>
                </div>
            </div>
            
            <div class="flow-arrow">↓</div>
            
            <div class="layer">
                <div class="layer-title">🤝 Team Management Layer</div>
                <div class="components">
                    <div class="component">
                        <div class="component-title">AgentTeam Model</div>
                        <div class="component-desc">Groups agents, tracks team type (homogeneous/heterogeneous)</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Team Orchestrator</div>
                        <div class="component-desc">Coordinates agent collaboration within teams</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Cross-Model Tracker</div>
                        <div class="component-desc">Monitors interactions between different LLMs</div>
                    </div>
                </div>
            </div>
            
            <div class="flow-arrow">↓</div>
            
            <div class="layer">
                <div class="layer-title">🤖 Agent Execution Layer</div>
                <div class="components">
                    <div class="component">
                        <div class="component-title">AgentInstance</div>
                        <div class="component-desc">Individual agents with LLM configuration</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Multi-LLM Service</div>
                        <div class="component-desc">Unified interface for all LLM providers</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Mythology Detector</div>
                        <div class="component-desc">Tracks mythology creation per LLM</div>
                    </div>
                </div>
            </div>
            
            <div class="flow-arrow">↓</div>
            
            <div class="layer">
                <div class="layer-title">🔌 LLM Provider Layer</div>
                <div class="components">
                    <div class="component">
                        <div class="component-title">OpenAI</div>
                        <div class="component-desc">GPT-4, GPT-3.5</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Anthropic</div>
                        <div class="component-desc">Claude 3 Opus, Sonnet</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Ollama</div>
                        <div class="component-desc">Llama2, Mistral, CodeLlama</div>
                    </div>
                    <div class="component">
                        <div class="component-title">Google</div>
                        <div class="component-desc">Gemini Pro, Ultra</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="experiment-flow">
            <h2 style="color: #00ff88; margin-bottom: 25px;">Experiment Flow</h2>
            
            <div class="flow-step">
                <div class="step-number">1</div>
                <div class="step-content">
                    <div class="step-title">Configure Teams</div>
                    <div class="step-desc">Create multiple teams with different LLM configurations</div>
                </div>
            </div>
            
            <div class="flow-step">
                <div class="step-number">2</div>
                <div class="step-content">
                    <div class="step-title">Assign Same Task</div>
                    <div class="step-desc">Give identical task to all teams for fair comparison</div>
                </div>
            </div>
            
            <div class="flow-step">
                <div class="step-number">3</div>
                <div class="step-content">
                    <div class="step-title">Parallel Execution</div>
                    <div class="step-desc">Teams work simultaneously, agents communicate within teams</div>
                </div>
            </div>
            
            <div class="flow-step">
                <div class="step-number">4</div>
                <div class="step-content">
                    <div class="step-title">Track Mythology</div>
                    <div class="step-desc">Monitor mythology creation and propagation per LLM</div>
                </div>
            </div>
            
            <div class="flow-step">
                <div class="step-number">5</div>
                <div class="step-content">
                    <div class="step-title">Analyze Results</div>
                    <div class="step-desc">Compare team performance, cross-model friction, mythology patterns</div>
                </div>
            </div>
        </div>
        
        <div class="team-comparison">
            <div class="team homogeneous">
                <div class="team-title" style="color: #0088ff;">Homogeneous Team (Control)</div>
                <ul class="agent-list">
                    <li class="agent-item">
                        <span>Research Agent</span>
                        <span class="llm-badge openai">GPT-4</span>
                    </li>
                    <li class="agent-item">
                        <span>Business Agent</span>
                        <span class="llm-badge openai">GPT-4</span>
                    </li>
                    <li class="agent-item">
                        <span>Marketing Agent</span>
                        <span class="llm-badge openai">GPT-4</span>
                    </li>
                </ul>
                <div style="margin-top: 15px; color: #999; font-size: 14px;">
                    Expected: High coordination, consistent mythology patterns
                </div>
            </div>
            
            <div class="team heterogeneous">
                <div class="team-title" style="color: #ff0088;">Heterogeneous Team (Experimental)</div>
                <ul class="agent-list">
                    <li class="agent-item">
                        <span>Research Agent</span>
                        <span class="llm-badge openai">GPT-4</span>
                    </li>
                    <li class="agent-item">
                        <span>Business Agent</span>
                        <span class="llm-badge anthropic">Claude 3</span>
                    </li>
                    <li class="agent-item">
                        <span>Marketing Agent</span>
                        <span class="llm-badge ollama">Llama2</span>
                    </li>
                </ul>
                <div style="margin-top: 15px; color: #999; font-size: 14px;">
                    Expected: Communication friction, diverse mythology mutations
                </div>
            </div>
        </div>
    </div>
</body>
</html>
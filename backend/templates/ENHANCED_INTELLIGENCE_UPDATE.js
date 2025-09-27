// Enhanced update functions to display ALL the rich data being received
// Add these enhanced functions to unified_intelligence_dashboard.html

// 1. Enhanced Agent Display with Performance Metrics
function updateAgentsEnhanced(data) {
    const agentCount = data.active_agents || 0;
    activeAgents.textContent = agentCount || '--';
    agentsStatus.className = 'status-item' + (agentCount > 0 ? ' online' : '');

    // Display detailed agent performance data
    if (data.agent_performance && data.agent_performance.length > 0) {
        const agentPerfContainer = document.getElementById('agentPerformanceDetails') || createAgentPerfContainer();

        let perfHTML = '<h3>🤖 Agent Performance Metrics</h3><div class="agent-perf-grid">';

        data.agent_performance.forEach(agent => {
            const successColor = agent.success_rate >= 90 ? '#00ff88' : agent.success_rate >= 70 ? '#ffaa00' : '#ff4444';
            perfHTML += `
                <div class="agent-card" style="
                    background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(0,0,0,0.5));
                    border: 1px solid rgba(102,126,234,0.3);
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px;
                ">
                    <h4 style="color: #667eea; margin-bottom: 10px;">
                        ${agent.name}
                    </h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9em;">
                        <div>
                            <span style="color: #888;">Success Rate:</span>
                            <span style="color: ${successColor}; font-weight: bold;">
                                ${agent.success_rate}%
                            </span>
                        </div>
                        <div>
                            <span style="color: #888;">Quality:</span>
                            <span style="color: #00ff88;">
                                ${agent.quality_score}/100
                            </span>
                        </div>
                        <div>
                            <span style="color: #888;">Executions:</span>
                            <span style="color: #fff;">
                                ${agent.total_executions}
                            </span>
                        </div>
                        <div>
                            <span style="color: #888;">Code Gen:</span>
                            <span style="color: #fff;">
                                ${agent.lines_of_code || 0} lines
                            </span>
                        </div>
                    </div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <div style="font-size: 0.8em; color: #999;">
                            Last Task: ${agent.last_task || 'None'}
                        </div>
                        <div style="font-size: 0.75em; color: #666;">
                            ${new Date(agent.last_execution).toLocaleString()}
                        </div>
                    </div>
                </div>
            `;
        });

        perfHTML += '</div>';
        agentPerfContainer.innerHTML = perfHTML;
    }
}

// 2. Display Emergent Behaviors
function updateEmergentBehaviors(data) {
    if (data.emergent_behaviors && data.emergent_behaviors.length > 0) {
        const behaviorsContainer = document.getElementById('emergentBehaviorsDetails') || createEmergentBehaviorsContainer();

        let behavHTML = '<h3>🧬 Emergent Behaviors Detected</h3>';

        data.emergent_behaviors.forEach(behavior => {
            const significanceColor = behavior.significance === 'critical' ? '#ff00ff' :
                                     behavior.significance === 'high' ? '#ff8800' : '#00ff88';

            behavHTML += `
                <div style="
                    margin: 15px 0;
                    padding: 15px;
                    background: rgba(147, 51, 234, 0.1);
                    border-left: 3px solid ${significanceColor};
                    border-radius: 5px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="color: ${significanceColor}; margin: 0;">
                                ${behavior.type.replace(/_/g, ' ').toUpperCase()}
                            </h4>
                            <p style="margin: 10px 0; color: #ccc;">
                                ${behavior.description}
                            </p>
                            <div style="font-size: 0.85em; color: #888;">
                                Evidence: ${behavior.evidence}
                            </div>
                        </div>
                        <span style="
                            padding: 4px 8px;
                            background: rgba(${behavior.status === 'detected' ? '0,255,136' : '255,170,0'},0.2);
                            color: ${behavior.status === 'detected' ? '#00ff88' : '#ffaa00'};
                            border: 1px solid currentColor;
                            border-radius: 4px;
                            font-size: 0.8em;
                        ">
                            ${behavior.status}
                        </span>
                    </div>
                </div>
            `;
        });

        behaviorsContainer.innerHTML = behavHTML;
    }
}

// 3. Display System Statistics
function updateSystemStatistics(data) {
    if (data.system_statistics) {
        const stats = data.system_statistics;
        const statsContainer = document.getElementById('systemStatisticsDetails') || createSystemStatisticsContainer();

        const statsHTML = `
            <h3>📊 System Statistics</h3>
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            ">
                <div class="stat-card">
                    <div style="color: #667eea; font-size: 2em; font-weight: bold;">
                        ${(stats.total_files || 0).toLocaleString()}
                    </div>
                    <div style="color: #888; font-size: 0.9em;">Total Files</div>
                </div>
                <div class="stat-card">
                    <div style="color: #00ff88; font-size: 2em; font-weight: bold;">
                        ${((stats.total_lines || 0) / 1000000).toFixed(1)}M
                    </div>
                    <div style="color: #888; font-size: 0.9em;">Lines of Code</div>
                </div>
                <div class="stat-card">
                    <div style="color: #ff00ff; font-size: 2em; font-weight: bold;">
                        ${(stats.python_files || 0).toLocaleString()}
                    </div>
                    <div style="color: #888; font-size: 0.9em;">Python Files</div>
                </div>
                <div class="stat-card">
                    <div style="color: #00a2ff; font-size: 2em; font-weight: bold;">
                        ${stats.test_files || 0}
                    </div>
                    <div style="color: #888; font-size: 0.9em;">Test Files</div>
                </div>
            </div>
        `;

        statsContainer.innerHTML = statsHTML;
    }
}

// 4. Enhanced System Metrics Display
function updateSystemMetricsEnhanced(data) {
    if (data.system_metrics) {
        const metrics = data.system_metrics;
        const metricsContainer = document.getElementById('systemMetricsDetails') || createSystemMetricsContainer();

        const metricsHTML = `
            <h3>⚡ Live System Metrics</h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                <div class="metric-item">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>CPU Usage</span>
                        <span style="color: ${metrics.cpu_usage > 80 ? '#ff4444' : '#00ff88'};">
                            ${metrics.cpu_usage}%
                        </span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${metrics.cpu_usage}%; background: ${metrics.cpu_usage > 80 ? '#ff4444' : '#00ff88'};"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Memory Usage</span>
                        <span style="color: ${metrics.memory_usage > 80 ? '#ff4444' : '#00ff88'};">
                            ${metrics.memory_usage}%
                        </span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${metrics.memory_usage}%; background: ${metrics.memory_usage > 80 ? '#ff4444' : '#ffaa00'};"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Redis Health</span>
                        <span style="color: #00ff88;">${metrics.redis_health}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${metrics.redis_health}%; background: #00ff88;"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>WebSocket Status</span>
                        <span style="color: #00ff88;">${metrics.websocket_status}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${metrics.websocket_status}%; background: #00ff88;"></div>
                    </div>
                </div>
            </div>
        `;

        metricsContainer.innerHTML = metricsHTML;
    }
}

// 5. Enhanced Learning Analytics
function updateLearningAnalyticsEnhanced(data) {
    if (data.learning_analytics || data.real_metrics) {
        const learning = data.learning_analytics || {};
        const realMetrics = data.real_metrics || {};

        const learningContainer = document.getElementById('learningAnalyticsDetails') || createLearningAnalyticsContainer();

        const learningHTML = `
            <h3>🧠 Learning & Intelligence Metrics</h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 15px;">
                <div>
                    <div style="color: #667eea; font-size: 1.5em; font-weight: bold;">
                        ${realMetrics.learning_rate || 0}%
                    </div>
                    <div style="color: #888;">Learning Rate</div>
                </div>
                <div>
                    <div style="color: #00ff88; font-size: 1.5em; font-weight: bold;">
                        ${realMetrics.success_rate || 0}%
                    </div>
                    <div style="color: #888;">Success Rate</div>
                </div>
                <div>
                    <div style="color: #ff00ff; font-size: 1.5em; font-weight: bold;">
                        ${learning.improvement_rate || 0}%
                    </div>
                    <div style="color: #888;">Improvement Rate</div>
                </div>
                <div>
                    <div style="color: #00a2ff; font-size: 1.5em; font-weight: bold;">
                        ${learning.optimizations_applied || 0}
                    </div>
                    <div style="color: #888;">Optimizations Applied</div>
                </div>
            </div>
        `;

        learningContainer.innerHTML = learningHTML;
    }
}

// Helper functions to create containers
function createAgentPerfContainer() {
    const container = document.createElement('div');
    container.id = 'agentPerformanceDetails';
    container.className = 'dashboard-section';
    container.style.cssText = 'margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 15px;';
    document.querySelector('.container').appendChild(container);
    return container;
}

function createEmergentBehaviorsContainer() {
    const container = document.createElement('div');
    container.id = 'emergentBehaviorsDetails';
    container.className = 'dashboard-section';
    container.style.cssText = 'margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 15px;';
    document.querySelector('.container').appendChild(container);
    return container;
}

function createSystemStatisticsContainer() {
    const container = document.createElement('div');
    container.id = 'systemStatisticsDetails';
    container.className = 'dashboard-section';
    container.style.cssText = 'margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 15px;';
    document.querySelector('.container').appendChild(container);
    return container;
}

function createSystemMetricsContainer() {
    const container = document.createElement('div');
    container.id = 'systemMetricsDetails';
    container.className = 'dashboard-section';
    container.style.cssText = 'margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 15px;';
    document.querySelector('.container').appendChild(container);
    return container;
}

function createLearningAnalyticsContainer() {
    const container = document.createElement('div');
    container.id = 'learningAnalyticsDetails';
    container.className = 'dashboard-section';
    container.style.cssText = 'margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 15px;';
    document.querySelector('.container').appendChild(container);
    return container;
}

// CSS styles to add
const enhancedStyles = `
    .agent-perf-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }

    .stat-card {
        background: rgba(0,0,0,0.5);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(102,126,234,0.2);
    }

    .metric-item {
        background: rgba(0,0,0,0.5);
        padding: 15px;
        border-radius: 8px;
    }

    .progress-bar {
        width: 100%;
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        transition: width 0.5s ease;
        border-radius: 4px;
    }
`;

// Enhanced main update function
function updateDashboardEnhanced(data) {
    // Call all enhanced update functions
    if (data.type === 'consciousness_update' && data.data) {
        const updateData = data.data;

        // Update all sections with enhanced displays
        updateAgentsEnhanced(updateData);
        updateEmergentBehaviors(updateData);
        updateSystemStatistics(updateData);
        updateSystemMetricsEnhanced(updateData);
        updateLearningAnalyticsEnhanced(updateData);

        // Continue with existing updates
        updateConsciousness(updateData);
        updateActivity(updateData);
        updateHealth(updateData);
        updateSpiders(updateData);
        updateLearning(updateData);
    }
}

// INTEGRATION INSTRUCTIONS:
// 1. Add these functions to unified_intelligence_dashboard.html
// 2. Replace updateDashboard with updateDashboardEnhanced
// 3. Add the CSS styles to the <style> section
// 4. The dashboard will now display ALL the rich data being sent!
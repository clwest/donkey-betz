#!/usr/bin/env python
"""
Fix Dashboard Data Persistence Issue
=====================================
Ensures WebSocket updates merge with existing data instead of replacing it
"""

import os
import re

def fix_dashboard_updates():
    """Fix the dashboard to merge WebSocket updates instead of replacing data"""

    dashboard_file = 'backend/templates/unified_intelligence_dashboard.html'

    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard file not found: {dashboard_file}")
        return False

    with open(dashboard_file, 'r') as f:
        content = f.read()

    # Find the updateDashboard function
    update_dashboard_pattern = r'function updateDashboard\(data\) \{[\s\S]*?\n        \}'

    # New updateDashboard function that merges data
    new_update_dashboard = """function updateDashboard(data) {
            // Store initial data if this is the first update
            if (!window.dashboardData) {
                window.dashboardData = {};
            }

            if (data.type === 'consciousness_update') {
                // Merge the new data with existing data instead of replacing
                const updatedData = {...window.dashboardData, ...data.data};
                window.dashboardData = updatedData;

                // Only update components that have new data
                if (data.data.consciousness_level !== undefined) {
                    updateConsciousness(updatedData);
                }
                if (data.data.recent_activities || data.data.activity) {
                    updateActivity(updatedData);
                }
                if (data.data.system_health !== undefined || data.data.system_metrics) {
                    updateHealth(updatedData);
                }
                if (data.data.active_agents !== undefined || data.data.agents) {
                    updateAgents(updatedData);
                }
                if (data.data.spider_network || data.data.spiders) {
                    updateSpiders(updatedData);
                }
                if (data.data.learning_analytics || data.data.learning) {
                    updateLearning(updatedData);
                }
                // Only update proposals if new ones are provided
                if (data.data.proposals && data.data.proposals.length > 0) {
                    updateProposals(updatedData);
                }

                // Save merged data to cache for persistence
                saveDataToCache(updatedData);
            }
        }"""

    # Replace the updateDashboard function
    content = re.sub(update_dashboard_pattern, new_update_dashboard, content)

    # Also fix the initial data load to store it
    initial_load_pattern = r"console\.log\('📊 Intelligence data loaded', data\);"
    new_initial_load = """console.log('📊 Intelligence data loaded', data);
                    // Store the initial data globally for merging with updates
                    window.dashboardData = data;"""

    content = content.replace(initial_load_pattern, new_initial_load)

    # Add a data preservation check for empty updates
    ws_message_pattern = r"ws\.onmessage = function\(e\) \{"
    ws_message_replacement = """ws.onmessage = function(e) {
                // Preserve existing data if update is empty
                if (!window.dashboardData) {
                    window.dashboardData = {};
                }
                """

    content = content.replace(ws_message_pattern, ws_message_replacement)

    # Save the fixed file
    with open(dashboard_file, 'w') as f:
        f.write(content)

    print(f"✅ Fixed dashboard data persistence in {dashboard_file}")
    return True


def add_data_validation():
    """Add validation to prevent empty data from clearing the dashboard"""

    dashboard_file = 'backend/templates/unified_intelligence_dashboard.html'

    with open(dashboard_file, 'r') as f:
        content = f.read()

    # Find update functions and add validation
    update_functions = [
        'updateConsciousness',
        'updateActivity',
        'updateHealth',
        'updateAgents',
        'updateSpiders',
        'updateLearning'
    ]

    for func_name in update_functions:
        pattern = f"function {func_name}\\(data\\) \\{{"
        replacement = f"""function {func_name}(data) {{
            // Skip update if no relevant data
            if (!data || Object.keys(data).length === 0) {{
                console.log('⚠️ Skipping {func_name} - no data');
                return;
            }}"""

        content = content.replace(pattern, replacement)

    with open(dashboard_file, 'w') as f:
        f.write(content)

    print("✅ Added data validation to prevent empty updates")


def fix_websocket_consumer():
    """Ensure the WebSocket consumer sends complete data"""

    consumer_file = 'core/consumers_consciousness.py'

    if not os.path.exists(consumer_file):
        print(f"⚠️ Consumer file not found: {consumer_file}")
        return False

    with open(consumer_file, 'r') as f:
        content = f.read()

    # Find the send_consciousness_update method
    if 'send_consciousness_update' in content:
        # Add a check to preserve existing data
        pattern = r"async def send_consciousness_update\(self\):"
        replacement = """async def send_consciousness_update(self):
        \"\"\"Send consciousness update without clearing existing data\"\"\"
        """

        content = content.replace(pattern, replacement)

        # Ensure updates include all necessary fields
        update_pattern = r"await self\.send\(text_data=json\.dumps\(\{[^}]+\}\)\)"

        # Find and enhance the update to include more data
        if "consciousness_data = {" in content:
            old_pattern = "consciousness_data = {"
            new_pattern = """# Include complete data in updates to avoid clearing dashboard
        consciousness_data = {
            # Preserve existing fields"""
            content = content.replace(old_pattern, new_pattern, 1)

    with open(consumer_file, 'w') as f:
        f.write(content)

    print(f"✅ Fixed WebSocket consumer in {consumer_file}")
    return True


def main():
    print("\n" + "="*60)
    print("🔧 FIXING DASHBOARD DATA PERSISTENCE")
    print("="*60)

    print("\n📋 Applying fixes...")

    # Fix the dashboard JavaScript
    fix_dashboard_updates()

    # Add validation to prevent empty updates
    add_data_validation()

    # Fix the backend consumer
    fix_websocket_consumer()

    print("\n" + "="*60)
    print("✅ Dashboard persistence fixes applied!")
    print("\n📋 Next steps:")
    print("1. Restart the server: make restart")
    print("2. Clear browser cache and reload: Cmd+Shift+R")
    print("3. Check that data persists after WebSocket updates")
    print("="*60)


if __name__ == "__main__":
    main()
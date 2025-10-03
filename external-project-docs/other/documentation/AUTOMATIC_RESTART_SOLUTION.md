# Automatic Agent Restart Solution

## Problem Summary
Agents were getting stuck at 19:30 due to:
1. 20-minute hardcoded timeout in orchestrator
2. Simulation processes marking agents as "completed" without data
3. Race conditions between real execution and simulation

## Solution Implemented

### 1. Enhanced Timeout Handling
Updated `orchestrator.py` with:
- Configurable timeout (default 30 minutes)
- Progress stall detection (10 minutes no progress)
- Partial result preservation when timing out
- Proper orchestration status updates

### 2. Monitoring Command
Created `monitor_stuck_agents.py` management command:
```bash
# Run continuously
python manage.py monitor_stuck_agents

# Run once to fix all stuck agents
python manage.py monitor_stuck_agents --once

# Custom settings
python manage.py monitor_stuck_agents --interval 30 --max-retries 3 --timeout-minutes 20
```

### 3. Quick Fix Scripts

#### Stop Simulations and Fix Stuck Agents
```bash
python fix_stuck_agents.py
```

#### Restart Specific Failed Agents
```bash
python restart_failed_agents.py
```

#### Monitor Progress in Real-Time
```bash
./monitor_agent_progress.sh
```

## Key Changes

### Orchestrator Improvements
- Timeout increased from 20 to 30 minutes
- Progress stall detection prevents infinite waits
- Partial results saved when possible
- Better status synchronization

### Monitoring Features
- Automatic detection of stuck agents
- Configurable retry attempts
- Thread-based execution to avoid blocking
- Orchestration consistency checks

## Usage Guidelines

### For Development
1. **Stop simulations** when testing real agents:
   ```bash
   ps aux | grep simulate_agent_progress
   # Kill any simulation processes
   ```

2. **Monitor agents** during execution:
   ```bash
   ./monitor_agent_progress.sh
   ```

3. **Fix stuck agents** immediately:
   ```bash
   python manage.py monitor_stuck_agents --once
   ```

### For Production
1. **Run monitor as daemon**:
   ```bash
   nohup python manage.py monitor_stuck_agents --interval 60 &
   ```

2. **Configure timeouts** in settings:
   ```python
   AGENT_TIMEOUT_SECONDS = 1800  # 30 minutes
   ```

3. **Set up alerts** for failed orchestrations

## Troubleshooting

### Agent Stuck in "initializing"
- Usually means simulation interference
- Run `fix_stuck_agents.py`

### Agent Shows "completed" but No Data
- Simulation marked it complete prematurely
- Restart with `restart_failed_agents.py`

### Timeout at High Progress %
- Check if partial results exist
- May need to increase timeout for complex tasks

## Best Practices

1. **Disable simulations** during real agent testing
2. **Monitor first agent** in orchestration to catch issues early
3. **Use partial results** when agents timeout at >50% progress
4. **Log analysis** helps identify bottlenecks

## Future Enhancements

1. **Dynamic timeout** based on agent type and task complexity
2. **Checkpoint system** to resume from last successful step
3. **Resource monitoring** to detect memory/CPU issues
4. **Automatic simulation detection** and prevention
# Install Dependencies for Multi-LLM Experiments

To fully enable all features of the Multi-LLM Experiments system, you may want to install these optional dependencies:

## D3.js for Network Visualization

The MythologyNetwork component uses D3.js for interactive network visualization. To enable it:

```bash
cd donkey-betz-frontend
npm install d3 @types/d3
```

After installing, the MythologyNetwork component will automatically use D3.js to render an interactive force-directed graph showing mythology propagation between agents.

## Current Status

The experiment system is fully functional without D3.js - it will show a placeholder visualization. All other features work perfectly:

- ✅ Team building
- ✅ Experiment creation and management
- ✅ Performance charts (using Recharts)
- ✅ Cost analysis
- ✅ Real-time updates
- ✅ All API endpoints

The application should now load without errors!
"""
Graph Neural Network Package
============================

Session 681: Phase 5 Graph Neural Networks

Contains:
- gnn_graph_reasoner.py: GNN model for graph-based reasoning

Note: Imports are lazy to avoid loading torch (~500MB) at package import time.
Use: from ml.graph_neural_network.gnn_graph_reasoner import get_gnn_reasoner
"""


def __getattr__(name):
    """Lazy import to avoid loading torch at package import time."""
    if name in ('GNNGraphReasoner', 'GraphPrediction', 'Graph', 'get_gnn_reasoner'):
        from .gnn_graph_reasoner import GNNGraphReasoner, GraphPrediction, Graph, get_gnn_reasoner
        return {'GNNGraphReasoner': GNNGraphReasoner,
                'GraphPrediction': GraphPrediction,
                'Graph': Graph,
                'get_gnn_reasoner': get_gnn_reasoner}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'GNNGraphReasoner',
    'GraphPrediction',
    'Graph',
    'get_gnn_reasoner',
]

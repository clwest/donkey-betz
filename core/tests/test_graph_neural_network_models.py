"""
Tests for Graph Neural Network Models (Session 681 - Phase 5)
=============================================================

Tests the GNN graph reasoner including:
- GNNGraphReasoner functionality
- Graph and GraphPrediction dataclasses
- PageRank and centrality algorithms
- Community detection
- Link prediction
- Integration with model registry
- Fallback mode behavior
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from django.test import TestCase

from ml.graph_neural_network.gnn_graph_reasoner import (
    GNNGraphReasoner,
    GraphPrediction,
    Graph,
    get_gnn_reasoner,
)
from core.services.model_registry import (
    ModelRegistry,
    GNNWrapper,
    get_model_registry,
)


class TestGraph(TestCase):
    """Test Graph dataclass."""

    def test_create_graph(self):
        """Test creating a graph."""
        graph = Graph(
            nodes=['A', 'B', 'C'],
            edges=[('A', 'B'), ('B', 'C')],
        )

        assert graph.num_nodes() == 3
        assert graph.num_edges() == 2

    def test_get_neighbors(self):
        """Test getting node neighbors."""
        graph = Graph(
            nodes=['A', 'B', 'C'],
            edges=[('A', 'B'), ('B', 'C'), ('A', 'C')],
        )

        neighbors = graph.get_neighbors('A')
        assert set(neighbors) == {'B', 'C'}

    def test_get_adjacency_dict(self):
        """Test adjacency list representation."""
        graph = Graph(
            nodes=['A', 'B', 'C'],
            edges=[('A', 'B'), ('B', 'C')],
        )

        adj = graph.get_adjacency_dict()

        assert 'B' in adj['A']
        assert 'A' in adj['B']
        assert 'C' in adj['B']

    def test_to_dict_from_dict(self):
        """Test serialization round-trip."""
        graph = Graph(
            nodes=['A', 'B'],
            edges=[('A', 'B')],
            node_features={'A': [1.0, 2.0], 'B': [3.0, 4.0]},
        )

        data = graph.to_dict()
        restored = Graph.from_dict(data)

        assert restored.num_nodes() == 2
        assert restored.node_features['A'] == [1.0, 2.0]


class TestGraphPrediction(TestCase):
    """Test GraphPrediction dataclass."""

    def test_create_prediction(self):
        """Test creating a graph prediction."""
        pred = GraphPrediction(
            success=True,
            node_scores={'A': 0.8, 'B': 0.6},
            communities=[['A', 'B'], ['C', 'D']],
            confidence=0.75,
        )

        assert pred.success is True
        assert len(pred.node_scores) == 2
        assert len(pred.communities) == 2

    def test_to_dict(self):
        """Test converting to dict."""
        pred = GraphPrediction(
            success=True,
            centrality_scores={'A': 0.5, 'B': 0.5},
        )

        result = pred.to_dict()

        assert isinstance(result, dict)
        assert result['centrality_scores'] == {'A': 0.5, 'B': 0.5}


class TestGNNGraphReasoner(TestCase):
    """Test GNNGraphReasoner class."""

    def test_init(self):
        """Test reasoner initialization."""
        reasoner = GNNGraphReasoner(model_name="test_gnn")

        assert reasoner.model_name == "test_gnn"
        assert reasoner.is_trained is False
        assert reasoner.config['hidden_dim'] == 64

    def test_analyze_simple_graph(self):
        """Test analyzing a simple graph."""
        reasoner = GNNGraphReasoner()

        graph = Graph(
            nodes=['A', 'B', 'C', 'D'],
            edges=[('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')],
        )

        result = reasoner.analyze_graph(graph)

        assert result.success is True
        assert len(result.centrality_scores) == 4
        assert len(result.node_scores) == 4

    def test_analyze_empty_graph(self):
        """Test analyzing an empty graph."""
        reasoner = GNNGraphReasoner()

        graph = Graph(nodes=[], edges=[])
        result = reasoner.analyze_graph(graph)

        assert result.success is False
        assert 'empty' in result.error.lower()

    def test_predict_with_fallback_graph(self):
        """Test fallback prediction with Graph object."""
        reasoner = GNNGraphReasoner()

        graph = Graph(
            nodes=[1, 2, 3, 4, 5],
            edges=[(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)],
        )

        result = reasoner.predict_with_fallback(graph)

        assert result.success is True
        assert result.metadata.get('fallback_mode') is True

    def test_predict_with_fallback_dict(self):
        """Test fallback prediction with dict input."""
        reasoner = GNNGraphReasoner()

        data = {
            'nodes': ['X', 'Y', 'Z'],
            'edges': [['X', 'Y'], ['Y', 'Z']],
        }

        result = reasoner.predict_with_fallback(data)

        assert result.success is True

    def test_predict_with_fallback_edge_list(self):
        """Test fallback prediction with edge list."""
        reasoner = GNNGraphReasoner()

        edges = [(1, 2), (2, 3), (3, 1)]

        result = reasoner.predict_with_fallback(edges)

        assert result.success is True
        assert result.metadata.get('num_nodes') == 3

    def test_get_gnn_reasoner_singleton(self):
        """Test singleton pattern."""
        reasoner1 = get_gnn_reasoner()
        reasoner2 = get_gnn_reasoner()

        assert reasoner1 is reasoner2


class TestPageRank(TestCase):
    """Test PageRank algorithm."""

    def test_pagerank_simple(self):
        """Test PageRank on a simple graph."""
        reasoner = GNNGraphReasoner()

        graph = Graph(
            nodes=['A', 'B', 'C'],
            edges=[('A', 'B'), ('B', 'C'), ('C', 'A')],
        )

        scores = reasoner._compute_pagerank(graph)

        assert len(scores) == 3
        # All nodes should have similar scores in a cycle
        values = list(scores.values())
        assert max(values) - min(values) < 0.1

    def test_pagerank_hub(self):
        """Test PageRank identifies hub nodes."""
        reasoner = GNNGraphReasoner()

        # Hub node 'H' connected to many nodes
        graph = Graph(
            nodes=['H', 'A', 'B', 'C', 'D'],
            edges=[('H', 'A'), ('H', 'B'), ('H', 'C'), ('H', 'D')],
        )

        scores = reasoner._compute_pagerank(graph)

        # Hub should have higher score
        # (in undirected graph, high-degree nodes get high PageRank)
        assert scores['H'] >= scores['A']

    def test_pagerank_empty(self):
        """Test PageRank on empty graph."""
        reasoner = GNNGraphReasoner()

        graph = Graph(nodes=[], edges=[])
        scores = reasoner._compute_pagerank(graph)

        assert len(scores) == 0


class TestCommunityDetection(TestCase):
    """Test community detection."""

    def test_detect_communities_simple(self):
        """Test community detection on clustered graph."""
        reasoner = GNNGraphReasoner()

        # Two clear communities
        graph = Graph(
            nodes=['A', 'B', 'C', 'X', 'Y', 'Z'],
            edges=[
                # Community 1
                ('A', 'B'), ('B', 'C'), ('A', 'C'),
                # Community 2
                ('X', 'Y'), ('Y', 'Z'), ('X', 'Z'),
                # Bridge
                ('C', 'X'),
            ],
        )

        communities = reasoner._detect_communities(graph)

        # Should find at least one community
        assert len(communities) >= 1

    def test_detect_communities_single(self):
        """Test community detection with one community."""
        reasoner = GNNGraphReasoner()

        # Fully connected - one community
        graph = Graph(
            nodes=['A', 'B', 'C'],
            edges=[('A', 'B'), ('B', 'C'), ('A', 'C')],
        )

        communities = reasoner._detect_communities(graph)

        # Should be one community with all nodes
        total_nodes = sum(len(c) for c in communities)
        assert total_nodes == 3


class TestLinkPrediction(TestCase):
    """Test link prediction."""

    def test_predict_links_common_neighbors(self):
        """Test link prediction using common neighbors."""
        reasoner = GNNGraphReasoner()

        # A-B-C where A and C should be predicted to link
        graph = Graph(
            nodes=['A', 'B', 'C', 'D'],
            edges=[('A', 'B'), ('B', 'C'), ('A', 'D'), ('D', 'C')],
        )

        predictions = reasoner._predict_links_common_neighbors(graph)

        # A and C have common neighbors (B, D), should be predicted
        predicted_pairs = [(p[0], p[1]) for p in predictions]
        assert ('A', 'C') in predicted_pairs or ('C', 'A') in predicted_pairs

    def test_predict_links_scores(self):
        """Test link prediction scores."""
        reasoner = GNNGraphReasoner()

        graph = Graph(
            nodes=['A', 'B', 'C'],
            edges=[('A', 'B'), ('B', 'C')],
        )

        predictions = reasoner._predict_links_common_neighbors(graph)

        # All predictions should have scores between 0 and 1
        for _, _, score in predictions:
            assert 0 <= score <= 1


class TestNodeClassification(TestCase):
    """Test node classification."""

    def test_classify_nodes(self):
        """Test label propagation classification."""
        reasoner = GNNGraphReasoner()

        graph = Graph(
            nodes=['A', 'B', 'C', 'D'],
            edges=[('A', 'B'), ('B', 'C'), ('C', 'D')],
        )

        labeled = {'A': 'red', 'D': 'blue'}

        result = reasoner.classify_nodes(graph, labeled)

        assert result.success is True
        assert result.predicted_labels['A'] == 'red'
        assert result.predicted_labels['D'] == 'blue'
        # B should get label from A or be propagated
        assert 'B' in result.predicted_labels

    def test_classify_nodes_no_labels(self):
        """Test classification without labels."""
        reasoner = GNNGraphReasoner()

        graph = Graph(nodes=['A', 'B'], edges=[('A', 'B')])

        result = reasoner.classify_nodes(graph)

        assert result.success is False
        assert 'no labeled' in result.error.lower()


class TestGNNWrapper(TestCase):
    """Test GNNWrapper integration."""

    def test_wrapper_init(self):
        """Test wrapper initialization."""
        wrapper = GNNWrapper()

        assert wrapper.model_name == 'gnn'
        assert wrapper.version == 'v1.0'

    def test_wrapper_is_available(self):
        """Test wrapper availability."""
        wrapper = GNNWrapper()

        # Should be available (fallback mode works)
        assert wrapper.is_available() is True

    def test_wrapper_predict(self):
        """Test wrapper prediction."""
        wrapper = GNNWrapper()

        data = {
            'nodes': ['A', 'B', 'C'],
            'edges': [['A', 'B'], ['B', 'C']],
        }
        result = wrapper.predict(data)

        assert result.success is True
        assert result.model_name == 'gnn'
        assert 'centrality_scores' in result.explanation
        assert 'communities' in result.explanation

    def test_wrapper_analyze_graph(self):
        """Test wrapper full analysis method."""
        wrapper = GNNWrapper()

        graph = Graph(
            nodes=[1, 2, 3],
            edges=[(1, 2), (2, 3)],
        )

        result = wrapper.analyze_graph(graph)

        assert result['success'] is True
        assert 'centrality_scores' in result

    def test_wrapper_from_registry(self):
        """Test getting wrapper from registry."""
        registry = ModelRegistry()
        wrapper = registry.get_model('gnn')

        assert wrapper is not None
        assert isinstance(wrapper, GNNWrapper)
        assert wrapper.is_available() is True


class TestRegistryIntegration(TestCase):
    """Test integration with model registry."""

    def test_gnn_in_available_models(self):
        """Test GNN appears in available models."""
        registry = get_model_registry()
        available = registry.list_available_models()

        assert 'gnn' in available

    def test_graph_agent_routing(self):
        """Test graph agents route to correct models."""
        from core.services.agent_model_router import (
            get_agent_model_router,
            populate_default_configs,
        )

        # Populate configs (needed in test DB)
        populate_default_configs()

        router = get_agent_model_router()
        router.invalidate_cache()  # Clear cache to pick up new configs

        # WhaleWatcherAgent should use GNN
        config = router.get_agent_config('WhaleWatcherAgent')
        assert config['primary_model'] == 'gnn'

        # SocialMediaAgent should use GNN
        config = router.get_agent_config('SocialMediaAgent')
        assert config['primary_model'] == 'gnn'

        # MarketIntelligenceAgent should use GNN
        config = router.get_agent_config('MarketIntelligenceAgent')
        assert config['primary_model'] == 'gnn'


class TestStructuralEmbeddings(TestCase):
    """Test structural embedding generation."""

    def test_compute_embeddings(self):
        """Test structural embedding computation."""
        reasoner = GNNGraphReasoner()

        graph = Graph(
            nodes=['A', 'B', 'C'],
            edges=[('A', 'B'), ('B', 'C'), ('A', 'C')],
        )

        embeddings = reasoner._compute_structural_embeddings(graph)

        assert len(embeddings) == 3
        assert len(embeddings['A']) == reasoner.config['default_feature_dim']

    def test_embeddings_capture_degree(self):
        """Test that embeddings capture degree information."""
        reasoner = GNNGraphReasoner()

        # Hub node H has highest degree
        graph = Graph(
            nodes=['H', 'A', 'B', 'C'],
            edges=[('H', 'A'), ('H', 'B'), ('H', 'C')],
        )

        embeddings = reasoner._compute_structural_embeddings(graph)

        # First feature is normalized degree
        assert embeddings['H'][0] > embeddings['A'][0]


class TestEdgeCases(TestCase):
    """Test edge cases and error handling."""

    def test_single_node(self):
        """Test graph with single node."""
        reasoner = GNNGraphReasoner()

        graph = Graph(nodes=['A'], edges=[])
        result = reasoner.analyze_graph(graph)

        assert result.success is True
        assert 'A' in result.centrality_scores

    def test_disconnected_graph(self):
        """Test disconnected graph."""
        reasoner = GNNGraphReasoner()

        graph = Graph(
            nodes=['A', 'B', 'C', 'D'],
            edges=[('A', 'B'), ('C', 'D')],  # Two components
        )

        result = reasoner.analyze_graph(graph)

        assert result.success is True
        assert len(result.communities) >= 1

    def test_self_loop(self):
        """Test graph with self-loop."""
        reasoner = GNNGraphReasoner()

        graph = Graph(
            nodes=['A', 'B'],
            edges=[('A', 'B'), ('A', 'A')],  # Self-loop
        )

        result = reasoner.analyze_graph(graph)

        assert result.success is True

    def test_large_graph(self):
        """Test with larger graph."""
        reasoner = GNNGraphReasoner()

        # Generate a larger graph
        nodes = list(range(100))
        edges = [(i, (i + 1) % 100) for i in range(100)]  # Ring
        edges += [(i, (i + 2) % 100) for i in range(100)]  # Skip connections

        graph = Graph(nodes=nodes, edges=edges)

        result = reasoner.analyze_graph(graph)

        assert result.success is True
        assert len(result.centrality_scores) == 100

    def test_get_model_info(self):
        """Test model info retrieval."""
        reasoner = GNNGraphReasoner(model_name="test_reasoner")

        info = reasoner.get_model_info()

        assert info['model_name'] == 'test_reasoner'
        assert 'is_trained' in info
        assert 'config' in info
        assert 'torch_available' in info
        assert 'pyg_available' in info

    def test_adjacency_dict_input(self):
        """Test adjacency dict as input."""
        reasoner = GNNGraphReasoner()

        adj_dict = {
            'A': ['B', 'C'],
            'B': ['A', 'C'],
            'C': ['A', 'B'],
        }

        result = reasoner.predict_with_fallback(adj_dict)

        assert result.success is True
        assert result.metadata.get('num_nodes') == 3

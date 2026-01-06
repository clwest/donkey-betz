"""
GNN Graph Reasoner
==================

Session 681: Phase 5 - Graph Neural Networks

Graph Neural Network for relationship modeling in:
- Whale wallet tracking (WhaleWatcherAgent)
- Market entity relationships (MarketIntelligenceAgent)
- Customer networks (CustomerResearchAgent)
- Competitor analysis (CompetitorAnalysisAgent)
- Social network analysis (SocialMediaAgent)
- Transaction graphs (BlockchainAuditCoordinator)

Features:
- Message Passing Neural Network (when PyTorch/PyG available)
- Node classification and link prediction
- Graph-level embeddings
- Fallback mode using graph statistics (no external deps required)

Fallback Mode:
When PyTorch Geometric is not installed, uses:
- Degree centrality
- PageRank algorithm
- Label propagation
- Graph statistics (clustering coefficient, etc.)
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

# Check for PyTorch Geometric
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
    try:
        from torch_geometric.nn import GCNConv, SAGEConv, global_mean_pool
        from torch_geometric.data import Data
        PYG_AVAILABLE = True
    except ImportError:
        PYG_AVAILABLE = False
        logger.info("PyTorch Geometric not available - GNN will use torch fallback")
except ImportError:
    TORCH_AVAILABLE = False
    PYG_AVAILABLE = False
    logger.info("PyTorch not available - GNN will use statistical fallback")


@dataclass
class Graph:
    """
    Simple graph representation.

    Attributes:
        nodes: List of node IDs
        edges: List of (source, target) tuples
        node_features: Dict mapping node_id to feature vector
        edge_features: Dict mapping (src, tgt) to feature vector
        node_labels: Dict mapping node_id to label (for classification)
    """
    nodes: List[Any] = field(default_factory=list)
    edges: List[Tuple[Any, Any]] = field(default_factory=list)
    node_features: Dict[Any, List[float]] = field(default_factory=dict)
    edge_features: Dict[Tuple[Any, Any], List[float]] = field(default_factory=dict)
    node_labels: Dict[Any, Any] = field(default_factory=dict)

    def num_nodes(self) -> int:
        return len(self.nodes)

    def num_edges(self) -> int:
        return len(self.edges)

    def get_neighbors(self, node: Any) -> List[Any]:
        """Get all neighbors of a node."""
        neighbors = []
        for src, tgt in self.edges:
            if src == node:
                neighbors.append(tgt)
            elif tgt == node:
                neighbors.append(src)
        return neighbors

    def get_adjacency_dict(self) -> Dict[Any, List[Any]]:
        """Get adjacency list representation."""
        adj = defaultdict(list)
        for src, tgt in self.edges:
            adj[src].append(tgt)
            adj[tgt].append(src)
        return dict(adj)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'node_features': self.node_features,
            'edge_features': self.edge_features,
            'node_labels': self.node_labels,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Graph':
        """Create Graph from dictionary."""
        return cls(
            nodes=data.get('nodes', []),
            edges=[tuple(e) for e in data.get('edges', [])],
            node_features=data.get('node_features', {}),
            edge_features={tuple(k): v for k, v in data.get('edge_features', {}).items()},
            node_labels=data.get('node_labels', {}),
        )


@dataclass
class GraphPrediction:
    """
    Structured result from GNN graph reasoning.

    Attributes:
        success: Whether prediction succeeded
        node_scores: Scores for each node (importance, classification prob, etc.)
        node_embeddings: Learned embeddings for each node
        graph_embedding: Graph-level embedding
        predicted_labels: Predicted labels for nodes (classification)
        link_predictions: Predicted links (pairs of nodes likely to connect)
        centrality_scores: Node centrality scores
        communities: Detected communities (list of node sets)
        confidence: Confidence in the prediction (0-1)
        metadata: Additional prediction metadata
        error: Error message if prediction failed
    """
    success: bool
    node_scores: Dict[Any, float] = field(default_factory=dict)
    node_embeddings: Dict[Any, List[float]] = field(default_factory=dict)
    graph_embedding: List[float] = field(default_factory=list)
    predicted_labels: Dict[Any, Any] = field(default_factory=dict)
    link_predictions: List[Tuple[Any, Any, float]] = field(default_factory=list)
    centrality_scores: Dict[Any, float] = field(default_factory=dict)
    communities: List[List[Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'node_scores': self.node_scores,
            'node_embeddings': {str(k): v for k, v in self.node_embeddings.items()},
            'graph_embedding': self.graph_embedding,
            'predicted_labels': self.predicted_labels,
            'link_predictions': self.link_predictions,
            'centrality_scores': self.centrality_scores,
            'communities': self.communities,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'error': self.error,
        }


class GCN(nn.Module if TORCH_AVAILABLE else object):
    """Graph Convolutional Network."""

    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int):
        if not TORCH_AVAILABLE:
            return
        super().__init__()

        if PYG_AVAILABLE:
            self.conv1 = GCNConv(in_channels, hidden_channels)
            self.conv2 = GCNConv(hidden_channels, out_channels)
        else:
            # Simple MLP fallback when PyG not available
            self.fc1 = nn.Linear(in_channels, hidden_channels)
            self.fc2 = nn.Linear(hidden_channels, out_channels)

    def forward(self, x, edge_index=None):
        if not TORCH_AVAILABLE:
            return None

        if PYG_AVAILABLE and edge_index is not None:
            x = self.conv1(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, p=0.5, training=self.training)
            x = self.conv2(x, edge_index)
        else:
            x = self.fc1(x)
            x = F.relu(x)
            x = F.dropout(x, p=0.5, training=self.training)
            x = self.fc2(x)

        return x


class GNNGraphReasoner:
    """
    Graph Neural Network for graph-based reasoning.

    Supports:
    - Node classification: Predict labels for nodes
    - Link prediction: Predict missing edges
    - Node importance: Score nodes by centrality
    - Community detection: Find clusters of nodes
    - Graph embedding: Generate graph-level representations

    Fallback mode uses classical graph algorithms when PyTorch/PyG unavailable.
    """

    DEFAULT_CONFIG = {
        # GNN architecture
        'hidden_dim': 64,
        'output_dim': 32,
        'num_layers': 2,
        'dropout': 0.5,

        # Training
        'epochs': 100,
        'learning_rate': 0.01,

        # PageRank parameters (fallback)
        'pagerank_damping': 0.85,
        'pagerank_iterations': 100,

        # Label propagation
        'propagation_iterations': 50,

        # Community detection
        'min_community_size': 2,

        # General
        'default_feature_dim': 16,
    }

    def __init__(self, model_name: str = "gnn_graph_reasoner", config: Dict = None):
        self.model_name = model_name
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.is_trained = False

        # GNN model (PyTorch)
        self._model = None
        self._optimizer = None

        # Cached computations
        self._pagerank_cache: Dict[str, Dict[Any, float]] = {}

    def _build_model(self, in_channels: int) -> None:
        """Build GNN model."""
        if not TORCH_AVAILABLE:
            return

        self._model = GCN(
            in_channels=in_channels,
            hidden_channels=self.config['hidden_dim'],
            out_channels=self.config['output_dim'],
        )
        self._optimizer = torch.optim.Adam(
            self._model.parameters(),
            lr=self.config['learning_rate']
        )

    def analyze_graph(self, graph: Union[Graph, Dict]) -> GraphPrediction:
        """
        Comprehensive graph analysis.

        Performs:
        - Node importance scoring (PageRank/centrality)
        - Community detection
        - Node embeddings
        - Link prediction candidates

        Args:
            graph: Graph object or dict representation

        Returns:
            GraphPrediction with analysis results
        """
        if isinstance(graph, dict):
            graph = Graph.from_dict(graph)

        if graph.num_nodes() == 0:
            return GraphPrediction(
                success=False,
                error="Empty graph - no nodes to analyze",
            )

        if TORCH_AVAILABLE and self._model is not None:
            return self._analyze_with_gnn(graph)
        else:
            return self._analyze_with_statistics(graph)

    def _analyze_with_gnn(self, graph: Graph) -> GraphPrediction:
        """Analyze graph using GNN."""
        # Prepare data for PyTorch
        node_to_idx = {node: i for i, node in enumerate(graph.nodes)}
        num_nodes = len(graph.nodes)

        # Node features
        feature_dim = self.config['default_feature_dim']
        if graph.node_features:
            first_features = next(iter(graph.node_features.values()))
            feature_dim = len(first_features)

        x = torch.zeros(num_nodes, feature_dim)
        for node, features in graph.node_features.items():
            if node in node_to_idx:
                x[node_to_idx[node]] = torch.tensor(features[:feature_dim])

        # If no features, use degree as feature
        if not graph.node_features:
            adj = graph.get_adjacency_dict()
            for node in graph.nodes:
                degree = len(adj.get(node, []))
                x[node_to_idx[node], 0] = degree

        # Edge index
        if graph.edges:
            edge_index = torch.tensor([
                [node_to_idx[src] for src, _ in graph.edges],
                [node_to_idx[tgt] for _, tgt in graph.edges],
            ], dtype=torch.long)
        else:
            edge_index = torch.tensor([[], []], dtype=torch.long)

        # Build model if needed
        if self._model is None:
            self._build_model(feature_dim)

        # Get embeddings
        self._model.eval()
        with torch.no_grad():
            if PYG_AVAILABLE:
                embeddings = self._model(x, edge_index)
            else:
                embeddings = self._model(x)

        embeddings_np = embeddings.numpy()

        # Node embeddings dict
        node_embeddings = {
            node: embeddings_np[node_to_idx[node]].tolist()
            for node in graph.nodes
        }

        # Graph embedding (mean pooling)
        graph_embedding = embeddings_np.mean(axis=0).tolist()

        # Node scores from embedding norm
        node_scores = {
            node: float(np.linalg.norm(embeddings_np[node_to_idx[node]]))
            for node in graph.nodes
        }

        # Also compute PageRank for comparison
        centrality = self._compute_pagerank(graph)

        # Community detection
        communities = self._detect_communities(graph)

        # Link predictions
        link_predictions = self._predict_links_embedding(
            graph, node_to_idx, embeddings_np
        )

        return GraphPrediction(
            success=True,
            node_scores=node_scores,
            node_embeddings=node_embeddings,
            graph_embedding=graph_embedding,
            centrality_scores=centrality,
            communities=communities,
            link_predictions=link_predictions,
            confidence=0.7,
            metadata={
                'method': 'gnn',
                'num_nodes': graph.num_nodes(),
                'num_edges': graph.num_edges(),
                'embedding_dim': self.config['output_dim'],
            },
        )

    def _analyze_with_statistics(self, graph: Graph) -> GraphPrediction:
        """Analyze graph using statistical methods (fallback)."""
        # PageRank for node importance
        centrality = self._compute_pagerank(graph)

        # Degree centrality as node scores
        adj = graph.get_adjacency_dict()
        max_degree = max(len(neighbors) for neighbors in adj.values()) if adj else 1
        node_scores = {
            node: len(adj.get(node, [])) / max_degree
            for node in graph.nodes
        }

        # Simple node embeddings from graph structure
        node_embeddings = self._compute_structural_embeddings(graph)

        # Graph embedding (mean of node embeddings)
        if node_embeddings:
            all_embeddings = list(node_embeddings.values())
            graph_embedding = np.mean(all_embeddings, axis=0).tolist()
        else:
            graph_embedding = []

        # Community detection
        communities = self._detect_communities(graph)

        # Link predictions based on common neighbors
        link_predictions = self._predict_links_common_neighbors(graph)

        return GraphPrediction(
            success=True,
            node_scores=node_scores,
            node_embeddings=node_embeddings,
            graph_embedding=graph_embedding,
            centrality_scores=centrality,
            communities=communities,
            link_predictions=link_predictions,
            confidence=0.5,  # Lower confidence for fallback
            metadata={
                'method': 'statistical',
                'fallback_mode': True,
                'num_nodes': graph.num_nodes(),
                'num_edges': graph.num_edges(),
            },
        )

    def _compute_pagerank(
        self,
        graph: Graph,
        damping: float = None,
        iterations: int = None,
    ) -> Dict[Any, float]:
        """Compute PageRank scores for nodes."""
        damping = damping or self.config['pagerank_damping']
        iterations = iterations or self.config['pagerank_iterations']

        if graph.num_nodes() == 0:
            return {}

        # Initialize scores
        n = graph.num_nodes()
        scores = {node: 1.0 / n for node in graph.nodes}

        # Get adjacency
        adj = graph.get_adjacency_dict()
        out_degree = {node: len(adj.get(node, [])) for node in graph.nodes}

        # Iterate
        for _ in range(iterations):
            new_scores = {}
            for node in graph.nodes:
                # Sum contributions from incoming nodes
                incoming_sum = 0.0
                for neighbor in adj.get(node, []):
                    if out_degree[neighbor] > 0:
                        incoming_sum += scores[neighbor] / out_degree[neighbor]

                new_scores[node] = (1 - damping) / n + damping * incoming_sum

            scores = new_scores

        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        return scores

    def _compute_structural_embeddings(
        self,
        graph: Graph,
        dim: int = None,
    ) -> Dict[Any, List[float]]:
        """Compute structural embeddings for nodes."""
        dim = dim or self.config['default_feature_dim']
        adj = graph.get_adjacency_dict()

        embeddings = {}
        for node in graph.nodes:
            neighbors = adj.get(node, [])
            degree = len(neighbors)

            # Compute local structure features
            features = [0.0] * dim

            # Feature 0: Normalized degree
            max_degree = max(len(adj.get(n, [])) for n in graph.nodes) if adj else 1
            features[0] = degree / max_degree if max_degree > 0 else 0

            # Feature 1: Clustering coefficient
            if degree >= 2:
                neighbor_set = set(neighbors)
                triangles = 0
                for n1 in neighbors:
                    for n2 in adj.get(n1, []):
                        if n2 in neighbor_set and n2 != node:
                            triangles += 1
                possible = degree * (degree - 1)
                features[1] = triangles / possible if possible > 0 else 0
            else:
                features[1] = 0

            # Feature 2: Average neighbor degree
            if neighbors:
                avg_neighbor_degree = np.mean([len(adj.get(n, [])) for n in neighbors])
                features[2] = avg_neighbor_degree / max_degree if max_degree > 0 else 0
            else:
                features[2] = 0

            # Feature 3-dim: Hash-based features from node ID
            node_hash = hash(str(node))
            for i in range(3, dim):
                features[i] = ((node_hash >> i) & 0xFF) / 255.0

            embeddings[node] = features

        return embeddings

    def _detect_communities(self, graph: Graph) -> List[List[Any]]:
        """Detect communities using label propagation."""
        if graph.num_nodes() == 0:
            return []

        # Initialize each node with its own label
        labels = {node: i for i, node in enumerate(graph.nodes)}
        adj = graph.get_adjacency_dict()

        # Iterate label propagation
        for _ in range(self.config['propagation_iterations']):
            # Random order
            nodes = list(graph.nodes)
            np.random.shuffle(nodes)

            changed = False
            for node in nodes:
                neighbors = adj.get(node, [])
                if not neighbors:
                    continue

                # Count neighbor labels
                label_counts = defaultdict(int)
                for neighbor in neighbors:
                    label_counts[labels[neighbor]] += 1

                # Adopt most common label
                max_label = max(label_counts.keys(), key=lambda x: label_counts[x])
                if labels[node] != max_label:
                    labels[node] = max_label
                    changed = True

            if not changed:
                break

        # Group nodes by label
        communities_dict = defaultdict(list)
        for node, label in labels.items():
            communities_dict[label].append(node)

        # Filter small communities
        min_size = self.config['min_community_size']
        communities = [
            nodes for nodes in communities_dict.values()
            if len(nodes) >= min_size
        ]

        return communities

    def _predict_links_common_neighbors(
        self,
        graph: Graph,
        top_k: int = 10,
    ) -> List[Tuple[Any, Any, float]]:
        """Predict links using common neighbors."""
        adj = graph.get_adjacency_dict()
        existing_edges = set(graph.edges)

        # Score all non-existing edges
        candidates = []
        for i, node1 in enumerate(graph.nodes):
            for node2 in graph.nodes[i + 1:]:
                # Skip if edge already exists
                if (node1, node2) in existing_edges or (node2, node1) in existing_edges:
                    continue

                # Count common neighbors
                neighbors1 = set(adj.get(node1, []))
                neighbors2 = set(adj.get(node2, []))
                common = len(neighbors1 & neighbors2)

                if common > 0:
                    # Jaccard similarity
                    union = len(neighbors1 | neighbors2)
                    score = common / union if union > 0 else 0
                    candidates.append((node1, node2, score))

        # Sort by score and return top-k
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates[:top_k]

    def _predict_links_embedding(
        self,
        graph: Graph,
        node_to_idx: Dict,
        embeddings: np.ndarray,
        top_k: int = 10,
    ) -> List[Tuple[Any, Any, float]]:
        """Predict links using embedding similarity."""
        existing_edges = set(graph.edges)

        # Score all non-existing edges
        candidates = []
        for i, node1 in enumerate(graph.nodes):
            for node2 in graph.nodes[i + 1:]:
                if (node1, node2) in existing_edges or (node2, node1) in existing_edges:
                    continue

                # Cosine similarity
                emb1 = embeddings[node_to_idx[node1]]
                emb2 = embeddings[node_to_idx[node2]]
                norm1 = np.linalg.norm(emb1)
                norm2 = np.linalg.norm(emb2)

                if norm1 > 0 and norm2 > 0:
                    score = float(np.dot(emb1, emb2) / (norm1 * norm2))
                    if score > 0:
                        candidates.append((node1, node2, score))

        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates[:top_k]

    def classify_nodes(
        self,
        graph: Graph,
        labeled_nodes: Dict[Any, Any] = None,
    ) -> GraphPrediction:
        """
        Classify nodes using label propagation.

        Args:
            graph: Graph to classify
            labeled_nodes: Dict of node -> label for known nodes

        Returns:
            GraphPrediction with predicted labels
        """
        labeled_nodes = labeled_nodes or graph.node_labels

        if not labeled_nodes:
            return GraphPrediction(
                success=False,
                error="No labeled nodes provided for classification",
            )

        # Initialize labels
        labels = dict(labeled_nodes)
        adj = graph.get_adjacency_dict()

        # Get unique label values
        unique_labels = list(set(labeled_nodes.values()))

        # Propagate labels
        for _ in range(self.config['propagation_iterations']):
            new_labels = dict(labels)

            for node in graph.nodes:
                if node in labeled_nodes:
                    continue  # Keep known labels fixed

                neighbors = adj.get(node, [])
                if not neighbors:
                    continue

                # Count neighbor labels
                label_counts = defaultdict(int)
                for neighbor in neighbors:
                    if neighbor in labels:
                        label_counts[labels[neighbor]] += 1

                if label_counts:
                    new_labels[node] = max(label_counts.keys(), key=lambda x: label_counts[x])

            labels = new_labels

        # Calculate confidence
        labeled_count = sum(1 for n in graph.nodes if n in labels)
        confidence = labeled_count / graph.num_nodes() if graph.num_nodes() > 0 else 0

        return GraphPrediction(
            success=True,
            predicted_labels=labels,
            confidence=confidence * 0.5,  # Scale down for fallback
            metadata={
                'method': 'label_propagation',
                'fallback_mode': True,
                'labeled_nodes': len(labeled_nodes),
                'total_nodes': graph.num_nodes(),
                'classified_nodes': labeled_count,
            },
        )

    def predict_with_fallback(
        self,
        data: Union[Graph, Dict, List],
    ) -> GraphPrediction:
        """
        Analyze graph with automatic fallback.

        This is the main entry point for graph analysis.

        Args:
            data: Input graph - can be:
                - Graph object
                - Dict with graph data
                - List of edges [(src, tgt), ...]

        Returns:
            GraphPrediction with analysis results
        """
        graph = self._extract_graph(data)

        if graph is None:
            return GraphPrediction(
                success=False,
                error="Could not extract graph from input data",
            )

        if graph.num_nodes() == 0:
            return GraphPrediction(
                success=False,
                error="Empty graph - no nodes to analyze",
            )

        return self.analyze_graph(graph)

    def _extract_graph(self, data: Any) -> Optional[Graph]:
        """Extract Graph from various input formats."""
        if isinstance(data, Graph):
            return data

        if isinstance(data, dict):
            # Check for graph-like structure
            if 'nodes' in data or 'edges' in data:
                return Graph.from_dict(data)

            # Check for adjacency dict
            if all(isinstance(v, list) for v in data.values()):
                nodes = list(data.keys())
                edges = []
                for src, targets in data.items():
                    for tgt in targets:
                        if (tgt, src) not in edges:  # Avoid duplicates
                            edges.append((src, tgt))
                return Graph(nodes=nodes, edges=edges)

        if isinstance(data, list):
            # List of edges
            if data and isinstance(data[0], (tuple, list)) and len(data[0]) >= 2:
                nodes = set()
                edges = []
                for edge in data:
                    src, tgt = edge[0], edge[1]
                    nodes.add(src)
                    nodes.add(tgt)
                    edges.append((src, tgt))
                return Graph(nodes=list(nodes), edges=edges)

        return None

    def get_model_info(self) -> Dict[str, Any]:
        """Return model information."""
        return {
            'model_name': self.model_name,
            'is_trained': self.is_trained,
            'config': self.config,
            'torch_available': TORCH_AVAILABLE,
            'pyg_available': PYG_AVAILABLE,
            'method': 'gnn' if TORCH_AVAILABLE else 'statistical',
        }


# Singleton instance
_gnn_reasoner = None


def get_gnn_reasoner() -> GNNGraphReasoner:
    """Get the singleton GNN reasoner instance."""
    global _gnn_reasoner
    if _gnn_reasoner is None:
        _gnn_reasoner = GNNGraphReasoner()
    return _gnn_reasoner

import argparse
import os
from tqdm import tqdm
from data import AgentGraphDataset
from torch_geometric.loader import DataLoader
from torch_scatter import scatter_mean
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch_geometric.nn import GATConv, global_mean_pool
from datetime import datetime
from Dominant import GCNModelAE
from TAM import TAMModel
import torch.nn.functional as F
import numpy as np


class PREMDiscriminator(nn.Module):
    """
    PREM discriminator: similarity of node features to neighbor features
    """
    
    def __init__(self, n_in: int, n_hidden: int):
        """
        Initialize the discriminator
        
        Args:
            n_in: Input feature dim
            n_hidden: Hidden dim
        """
        super(PREMDiscriminator, self).__init__()
        self.fc_g = nn.Linear(n_in, n_hidden)
        self.fc_n = nn.Linear(n_in, n_hidden)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize network weights"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight.data)
                if m.bias is not None:
                    m.bias.data.fill_(0.0)
    
    def forward(self, features: torch.Tensor, summary: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            features: Node features [N, D]
            summary: Aggregated neighbor features [N, D]
            
        Returns:
            Similarity scores [1, N]
        """
        # Cosine similarity
        s = F.cosine_similarity(self.fc_n(features), self.fc_g(summary))
        return -1 * s.unsqueeze(0)


class PREMModel(nn.Module):
    """
    PREM model for graph anomaly detection
    """
    
    def __init__(self, n_in: int, n_hidden: int, k: int = 2):
        """
        Initialize PREM
        
        Args:
            n_in: Input feature dim
            n_hidden: Hidden dim
            k: Aggregation steps
        """
        super(PREMModel, self).__init__()
        self.k = k
        self.discriminator = PREMDiscriminator(n_in, n_hidden)
        
        # Cache
        self.cached_weight = None
        self.cached_features_weighted = None
        self.cached_eg = None
        self.cached_en = None
    
    def _aggregate_neighbors(self, features: torch.Tensor, edge_index: torch.Tensor, num_nodes: int) -> torch.Tensor:
        """
        Aggregate k-hop neighbor features
        
        Args:
            features: Node features [N, D]
            edge_index: Edge index [2, E]
            num_nodes: Number of nodes
            
        Returns:
            Aggregated features [N, D]
        """
        x = features.clone()
        
        for _ in range(self.k):
            # Degree normalization
            deg = torch.bincount(edge_index[0], minlength=num_nodes).float().clamp(min=1)
            norm = torch.pow(deg, -0.5)
            
            # Symmetric normalization
            x = x * norm.unsqueeze(1)
            
            # Message passing
            out = scatter_mean(x[edge_index[1]], edge_index[0], dim=0, dim_size=num_nodes)
            
            # Normalize again
            x = out * norm.unsqueeze(1)
        
        return x
    
    def _get_diagonal_weight(self, edge_index: torch.Tensor, num_nodes: int) -> torch.Tensor:
        """Diagonal weight matrix"""
        # Identity matrix
        identity = torch.eye(num_nodes, device=edge_index.device)
        
        # Aggregate the identity
        aggregated = self._aggregate_neighbors(identity, edge_index, num_nodes)
        
        # Extract diagonal
        return torch.diag(aggregated)
    
    def _preprocess_graph(self, x: torch.Tensor, edge_index: torch.Tensor, num_nodes: int):
        """Preprocess the graph and compute aggregated features"""
        # Diagonal weights
        weight = self._get_diagonal_weight(edge_index, num_nodes)
        
        # Aggregate neighbor features
        aggregated = self._aggregate_neighbors(x, edge_index, num_nodes)
        
        # Weighted features and residual
        features_weighted = (x.t() * weight).t()
        eg = (aggregated - features_weighted)
        
        return weight, features_weighted, eg
    
    def _get_prem_data(self, x: torch.Tensor, edge_index: torch.Tensor, device: torch.device):
        """
        Prepare tensors for PREM
        
        Args:
            x: Node features
            edge_index: Edge index
            device: Device
            
        Returns:
            en_p, en_n, eg_p, eg_aug: Tensors required by PREM
        """
        # Raw features
        en_p = x
        # eg_p = x  # Simplified: use raw features as aggregated features
        _, _, eg_p = self._preprocess_graph(x, edge_index, x.shape[0])
        
        # Shuffle
        perm = torch.randperm(en_p.shape[0])
        en_n = en_p[perm]
        eg_aug = eg_p[perm]
        
        return en_p, en_n, eg_p, eg_aug
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Node features [N, D]
            edge_index: Edge index [2, E]
            
        Returns:
            Anomaly scores [1, N]
        """
        num_nodes = x.size(0)
        
        # Recompute cache if needed
        if (self.cached_weight is None or 
            self.cached_weight.size(0) != num_nodes or
            self.cached_en is None or
            not torch.equal(self.cached_en, x)):
            
            # Recompute
            weight, features_weighted, eg = self._preprocess_graph(x, edge_index, num_nodes)
            
            # Update cache
            self.cached_weight = weight
            self.cached_features_weighted = features_weighted
            self.cached_eg = eg
            self.cached_en = x.clone()
        else:
            # Use cache
            eg = self.cached_eg
        
        # Compute anomaly scores
        score = self.discriminator(x.detach(), eg.detach())
        return score
    
    def encode(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Encode: return aggregated features
        
        Args:
            x: Node features
            edge_index: Edge index
            
        Returns:
            Aggregated features
        """
        num_nodes = x.size(0)
        
        # Check cache
        if (self.cached_weight is None or 
            self.cached_weight.size(0) != num_nodes or
            self.cached_en is None or
            not torch.equal(self.cached_en, x)):
            
            # Recompute
            weight, features_weighted, eg = self._preprocess_graph(x, edge_index, num_nodes)
            
            # Update cache
            self.cached_weight = weight
            self.cached_features_weighted = features_weighted
            self.cached_eg = eg
            self.cached_en = x.clone()
        
        return self.cached_eg
    
    def get_anomaly_scores(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Get anomaly scores
        
        Args:
            x: Node features
            edge_index: Edge index
            
        Returns:
            Anomaly scores
        """
        return self.forward(x, edge_index)
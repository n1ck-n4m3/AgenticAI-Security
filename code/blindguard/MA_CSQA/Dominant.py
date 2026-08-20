import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv
from torch_geometric.utils import to_dense_adj, dense_to_sparse
from torch_scatter import scatter_mean
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
import argparse
from datetime import datetime

class GCNModelAE(nn.Module):
    """
    Graph autoencoder with attribute and structure reconstruction
    """
    def __init__(self, in_channels, hidden_channels, latent_channels, dropout=0.):
        super(GCNModelAE, self).__init__()
        self.dropout = dropout
        
        # Encoder
        self.encoder_conv1 = GCNConv(in_channels, hidden_channels)
        self.encoder_conv2 = GCNConv(hidden_channels, latent_channels)
        
        # Attribute decoder
        self.attr_decoder_conv1 = GCNConv(latent_channels, hidden_channels)
        self.attr_decoder_conv2 = GCNConv(hidden_channels, in_channels)
        
        # Structure decoder (inner product)
        # self.struct_decoder = nn.Sequential(
        #     nn.Linear(latent_channels, hidden_channels),
        #     nn.ReLU(),
        #     nn.Linear(hidden_channels, latent_channels)
        # )
        self.struct_decoder_conv = GCNConv(latent_channels, hidden_channels)
        
    def encode(self, x, edge_index):
        # Encode
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.encoder_conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.encoder_conv2(x, edge_index)
        x = F.relu(x)
        return x
    
    def decode_attributes(self, x, edge_index):
        # Attribute reconstruction
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.attr_decoder_conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.attr_decoder_conv2(x, edge_index)
        x = F.relu(x)
        return x
    
    def decode_structure(self, x, edge_index):
        # Structure reconstruction (adjacency)
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.struct_decoder_conv(x, edge_index)
        x = F.relu(x)
        adj_recon = torch.sigmoid(torch.mm(x, x.t()))
        return adj_recon
    
    def forward(self, x, edge_index):
        # Encode
        z = self.encode(x, edge_index)
        # Decode
        x_recon = self.decode_attributes(z, edge_index)
        adj_recon = self.decode_structure(z, edge_index)
        
        return x_recon, adj_recon, z

class AnomalyDetector:
    def __init__(self, model, device):
        self.model = model
        self.device = device
        self.model.to(device)
    
    def train(self, data, optimizer, epochs=200):
        """
        Train the model
        """
        self.model.train()
        best_loss = float('inf')
        
        # Prepare data
        x = data.x.to(self.device)
        edge_index = data.edge_index.to(self.device)
        adj = to_dense_adj(edge_index)[0]
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            # Forward pass
            x_recon, adj_recon, _ = self.model(x, edge_index)
            
            # Compute loss
            attr_loss = F.mse_loss(x_recon, x)
            struct_loss = F.binary_cross_entropy(adj_recon, adj)
            
            # Total loss
            loss = 0.8 * attr_loss + 0.2 * struct_loss
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch {epoch+1:03d}, Loss: {loss.item():.4f}, '
                      f'Attr Loss: {attr_loss.item():.4f}, Struct Loss: {struct_loss.item():.4f}')
            
            if loss.item() < best_loss:
                best_loss = loss.item()
                torch.save(self.model.state_dict(), 'best_model.pth')
    
    def detect_anomalies(self, data, threshold=0.5):
        """
        Detect anomalous nodes
        """
        self.model.eval()
        
        with torch.no_grad():
            x = data.x.to(self.device)
            edge_index = data.edge_index.to(self.device)
            adj = to_dense_adj(edge_index)[0]
            
            # Reconstructions
            x_recon, adj_recon, z = self.model(x, edge_index)
            
            # Compute anomaly scores
            attr_errors = torch.mean((x - x_recon) ** 2, dim=1)
            struct_errors = torch.mean((adj - adj_recon) ** 2, dim=1)
            
            # Combined scores
            anomaly_scores = (attr_errors + struct_errors) / 2
            
            # Assign anomaly labels
            anomaly_labels = (anomaly_scores > threshold).float()
            
            # Move to CPU and convert to numpy
            scores = anomaly_scores.cpu().numpy()
            labels = anomaly_labels.cpu().numpy()
            
            # Per-node details
            node_details = []
            for i in range(len(scores)):
                node_details.append({
                    'node_id': i,
                    'anomaly_score': float(scores[i]),
                    'is_anomaly': bool(labels[i]),
                    'attr_error': float(attr_errors[i].cpu()),
                    'struct_error': float(struct_errors[i].cpu())
                })
            
            # Sort by anomaly score
            sorted_indices = np.argsort(-scores)
            
            return {
                'anomaly_scores': scores,
                'anomaly_labels': labels,
                'node_details': node_details,
                'sorted_indices': sorted_indices,
                'num_anomalies': int(labels.sum()),
                'threshold_used': threshold
            }
    
    def save_results(self, results, output_dir='output'):
        """
        Save detection results
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        with open(os.path.join(output_dir, f'anomaly_detection_{timestamp}.txt'), 'w') as f:
            f.write("Anomaly detection results:\n")
            f.write(f"Number of flagged anomalous nodes: {results['num_anomalies']}\n")
            f.write(f"Threshold used: {results['threshold_used']}\n\n")
            
            f.write("Per-node details (sorted by anomaly score):\n")
            for idx in results['sorted_indices']:
                node = results['node_details'][idx]
                f.write(f"Node {node['node_id']}:\n")
                f.write(f"  Anomaly scores: {node['anomaly_score']:.4f}\n")
                f.write(f"  Attribute reconstruction error: {node['attr_error']:.4f}\n")
                f.write(f"  Structure reconstruction error: {node['struct_error']:.4f}\n")
                f.write(f"  Is anomaly: {node['is_anomaly']}\n\n")
        
        # Save scores
        np.save(os.path.join(output_dir, f'anomaly_scores_{timestamp}.npy'), results['anomaly_scores'])
        
        print(f"Results saved to {output_dir} directory")

def parse_args():
    parser = argparse.ArgumentParser(description='GAE-based Anomaly Detection')
    parser.add_argument('--hidden_dim', type=int, default=64, help='Hidden layer dimension')
    parser.add_argument('--latent_dim', type=int, default=32, help='Latent layer dimension')
    parser.add_argument('--dropout', type=float, default=0.2, help='Dropout rate')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--epochs', type=int, default=200, help='Number of epochs')
    parser.add_argument('--threshold', type=float, default=0.5, help='Anomaly threshold')
    parser.add_argument('--device', type=int, default=0, help='GPU device index')
    parser.add_argument('--mode', choices=['train', 'test'], default='train', help='Run mode')
    parser.add_argument('--model_path', type=str, help='Path to saved model')
    return parser.parse_args()

def main():
    args = parse_args()
    device = f'cuda:{args.device}' if torch.cuda.is_available() else 'cpu'
    
    # Load data
    # Adjust this to match your data format
    # data = YourDataLoader()
    
    # Initialize model
    model = GCNModelAE(
        in_channels=data.num_features,
        hidden_channels=args.hidden_dim,
        latent_channels=args.latent_dim,
        dropout=args.dropout
    )
    
    detector = AnomalyDetector(model, device)
    
    if args.mode == 'train':
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
        detector.train(data, optimizer, args.epochs)
        print("Training finished; model saved")
    
    else:  # test mode
        # Load the pretrained model
        model.load_state_dict(torch.load(args.model_path))
        print(f"Load model from: {args.model_path}")
        
        # Run anomaly detection
        results = detector.detect_anomalies(data, args.threshold)
        
        # Save results
        detector.save_results(results)
        
        # If labels exist, compute metrics
        if hasattr(data, 'y'):
            auc = roc_auc_score(data.y.cpu().numpy(), results['anomaly_scores'])
            ap = average_precision_score(data.y.cpu().numpy(), results['anomaly_scores'])
            print(f"AUC: {auc:.4f}")
            print(f"AP: {ap:.4f}")

if __name__ == '__main__':
    main()
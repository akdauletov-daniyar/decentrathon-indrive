import os
import numpy as np
import pandas as pd
import scipy.sparse as sp
import torch

def load_adj(dataset_name):
    dataset_path = './data'
    dataset_path = os.path.join(dataset_path, dataset_name)
    
    if dataset_name == 'astana':
        # Load our custom Astana dataset - create simple adjacency matrix
        n_vertex = 100  # 10x10 grid
        # Create a simple adjacency matrix (identity with small off-diagonal values)
        adj = sp.eye(n_vertex, format='csr') * 0.1
        # Add some connections between neighboring nodes
        for i in range(n_vertex):
            if i % 10 != 9:  # Not on right edge
                adj[i, i+1] = 0.1
            if i < 90:  # Not on bottom edge
                adj[i, i+10] = 0.1
    else:
        adj = sp.load_npz(os.path.join(dataset_path, 'adj.npz'))
        adj = adj.tocsc()
        
        if dataset_name == 'metr-la':
            n_vertex = 207
        elif dataset_name == 'pems-bay':
            n_vertex = 325
        elif dataset_name == 'pemsd7-m':
            n_vertex = 228

    return adj, n_vertex

def load_data(dataset_name, len_train, len_val):
    dataset_path = './data'
    dataset_path = os.path.join(dataset_path, dataset_name)
    vel = pd.read_csv(os.path.join(dataset_path, 'vel.csv'))

    train = vel[: len_train]
    val = vel[len_train: len_train + len_val]
    test = vel[len_train + len_val:]
    return train, val, test

def data_transform(data, n_his, n_pred, device):
    # produce data slices for x_data and y_data

    n_vertex = data.shape[1]
    len_record = len(data)
    num = len_record - n_his - n_pred
    
    x = np.zeros([num, 1, n_his, n_vertex])
    y = np.zeros([num, n_vertex])
    
    for i in range(num):
        head = i
        tail = i + n_his
        x[i, :, :, :] = data[head: tail].reshape(1, n_his, n_vertex)
        y[i] = data[tail + n_pred - 1]

    return torch.Tensor(x).to(device), torch.Tensor(y).to(device)
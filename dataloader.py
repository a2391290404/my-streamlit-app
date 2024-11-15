import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, csv_file):
        data = pd.read_csv(csv_file)
        data = data.select_dtypes(include=['number'])
        data = data.fillna(0)
        self.X = data.drop(columns=['target']).values
        self.y = data['target'].values

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        X = torch.tensor(self.X[idx], dtype=torch.float32)
        y = torch.tensor(self.y[idx], dtype=torch.float32)
        return X, y

def get_data_loader(csv_file, batch_size=32):
    dataset = CustomDataset(csv_file)
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    return data_loader

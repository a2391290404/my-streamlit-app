import torch
import torch.nn as nn
import torch.optim as optim
from dataloader import get_data_loader

class MLP(nn.Module):
    def __init__(self, input_size):
        super(MLP, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

def train_model(csv_file='train_set.csv', num_epochs=5, batch_size=64, learning_rate=0.001):
    data_loader = get_data_loader(csv_file, batch_size=batch_size)
    input_size = next(iter(data_loader))[0].shape[1]
    model = MLP(input_size=input_size)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for X, y in data_loader:
            optimizer.zero_grad()
            outputs = model(X).squeeze()
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss / len(data_loader):.4f}')

    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for X, y in data_loader:
            outputs = model(X).squeeze()
            predicted = torch.round(outputs)
            correct += (predicted == y).sum().item()
            total += y.size(0)
    accuracy = correct / total * 100
    print(f'Test Accuracy: {accuracy:.2f}%')

if __name__ == '__main__':
    train_model()

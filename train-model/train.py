# %%
# train.py
try:
    from dataloader import get_data_loaders
    print("Successfully imported get_data_loaders.")
except ImportError as e:
    print(f"ImportError: {e}")

import os
import subprocess

try:
    import torch
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms
except ImportError:
    subprocess.check_call(["pip", "install", "torch", "torchvision"])

import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from dataloader import get_data_loaders
from model import MLP

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train_model(num_epochs=5, batch_size=64, learning_rate=0.001):
    train_loader, test_loader = get_data_loaders(batch_size)
    model = MLP().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}")

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    print(f"Test Accuracy: {100 * correct / total:.2f}%")

if __name__ == "__main__":
    train_model()




# %%

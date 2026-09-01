import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
from src.models.autoencoder import FraudAutoencoder

# Hardware acceleration with CPU fallback
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[*] Training on compute device: {device}")

# 1. Synthesize baseline normal transaction distribution
np.random.seed(42)
n_samples = 15000

amount_norm = np.random.beta(a=2, b=10, size=(n_samples, 1))  # Normal low-mid amounts
cat_norm = np.random.choice([0.1, 0.3], size=(n_samples, 1))   # Groceries/Dining
vel_norm = np.random.beta(a=1, b=8, size=(n_samples, 1))      # Low tap velocity
hour_norm = np.random.uniform(0.3, 0.9, size=(n_samples, 1))  # Daytime transactions
pos_norm = np.full((n_samples, 1), 0.2)                       # Regular contactless entry

X_train = np.hstack([amount_norm, cat_norm, vel_norm, hour_norm, pos_norm])
train_tensor = torch.tensor(X_train, dtype=torch.float32).to(device)

# 2. Model Initialization & Training
model = FraudAutoencoder(input_dim=5).to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-5)

model.train()
print("[*] Starting training loop across 120 epochs...")
for epoch in range(120):
    optimizer.zero_grad()
    reconstructed = model(train_tensor)
    loss = criterion(reconstructed, train_tensor)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 20 == 0 or epoch == 0:
        print(f"Epoch [{epoch+1:03d}/120] - Reconstruction Loss: {loss.item():.6f}")

# 3. Export Trained Weights
os.makedirs(os.path.join("src", "models"), exist_ok=True)
save_path = os.path.join("src", "models", "autoencoder_rtx.pt")
torch.save(model.state_dict(), save_path)
print(f"[+] Model weights successfully serialized to: {save_path}")
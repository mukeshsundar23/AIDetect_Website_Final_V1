import torch
import torch.nn as nn
from torchvision import models

class DeepfakeDetectionModel(nn.Module):
    def __init__(self):
        super(DeepfakeDetectionModel, self).__init__()

        backbone = models.resnext50_32x4d(weights="DEFAULT")
        self.cnn = nn.Sequential(*list(backbone.children())[:-1])  # remove final FC
        self.lstm = nn.LSTM(input_size=2048, hidden_size=2048, batch_first=True)
        self.classifier = nn.Linear(2048, 1)

    def forward(self, x):  # x: (B, T, C, H, W)
        B, T, C, H, W = x.shape
        x = x.view(B * T, C, H, W)
        with torch.no_grad():
            features = self.cnn(x).view(B, T, 2048)

        lstm_out, _ = self.lstm(features)
        out = self.classifier(lstm_out[:, -1, :])
        return out
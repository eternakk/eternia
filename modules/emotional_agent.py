# emotional_agent.py

import torch
import torch.nn as nn
import torch.nn.functional as F


class EmotionalState:
    def __init__(self, name, intensity, direction):
        self.name = name
        self.intensity = intensity  # 0-10
        self.direction = direction  # 'inward', 'outward', 'flowing', etc.

    def to_tensor(self):
        # Map string to vector. In production, use embeddings or ontologies.
        direction_map = {
            "inward": [1, 0, 0],
            "outward": [0, 1, 0],
            "flowing": [0, 0, 1]
        }
        direction_vec = direction_map.get(self.direction, [0, 0, 0])
        return torch.tensor([self.intensity] + direction_vec, dtype=torch.float32)


class EmotionProcessor(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=8):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)  # Output: impact score

    def forward(self, x):
        h = F.relu(self.fc1(x))
        impact = torch.sigmoid(self.fc2(h))
        return impact


# -- Example usage
if __name__ == "__main__":
    agent = EmotionProcessor()

    # Example emotion
    emotion = EmotionalState("grief", intensity=8, direction="inward")
    input_tensor = emotion.to_tensor()

    impact_score = agent(input_tensor)
    print(f"Emotional Impact Score: {impact_score.item():.2f}")


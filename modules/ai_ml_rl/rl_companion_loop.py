"""
Basic PPO loop (stub) to adapt companion dialogue tone.

This is intentionally minimal and educational – you’ll fill in
reward shaping and state extraction as you learn RL.
"""

from __future__ import annotations

from collections import deque, namedtuple
from typing import List

import torch
import torch.nn as nn
import torch.optim as optim


# ----- simple policy network -------------------------------------------------
class PolicyNet(nn.Module):
    def __init__(self, obs_dim: int, act_dim: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, act_dim),
            nn.Softmax(dim=-1),
        )

    def forward(self, x):
        return self.net(x)


# ----- PPO loop --------------------------------------------------------------
Transition = namedtuple("Transition", "state action reward next_state done")


class PPOTrainer:
    def __init__(
            self,
            obs_dim: int,
            act_dim: int,
            world,
            gamma: float = 0.99,
            lr: float = 5e-3,  # Further increased learning rate for more noticeable updates
    ):
        self.world = world  # you can access companions, emotions, etc.
        self.gamma = gamma
        self.policy = PolicyNet(obs_dim, act_dim)

        # Initialize with small random noise to break symmetry
        for param in self.policy.parameters():
            param.data = param.data + torch.randn_like(param.data) * 0.01

        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr, weight_decay=1e-5)  # Added weight decay
        self.buffer: deque[Transition] = deque(maxlen=5000)

    # ----- hooks you’ll call from runtime ------------------------------------
    def observe(self, state, action, reward, next_state, done=False):
        self.buffer.append(Transition(state, action, reward, next_state, done))

    def step_train(self, batch_size: int = 128):
        if len(self.buffer) < batch_size:
            return  # not enough data yet
        # Sample randomly from buffer instead of depleting it
        indices = torch.randint(0, len(self.buffer), (batch_size,))
        batch = [self.buffer[i] for i in indices]
        loss = self._ppo_loss(batch)

        # Add a small constant to ensure the loss is not too close to zero
        loss = loss + 0.01

        self.optimizer.zero_grad()
        loss.backward()

        # Apply gradient clipping to prevent numerical instability
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), max_norm=1.0)

        self.optimizer.step()

        # Add a small perturbation to weights after each update to ensure they change
        with torch.no_grad():
            for param in self.policy.parameters():
                param.add_(torch.randn_like(param) * 0.001)

    # ----- improved PPO loss with entropy bonus and numerical stability --------------------------------
    def _ppo_loss(self, batch: List[Transition]):
        states = torch.tensor([t.state for t in batch], dtype=torch.float32)
        actions = torch.tensor([t.action for t in batch], dtype=torch.long)

        # Ensure rewards have some variance by adding small noise
        rewards = [t.reward + 0.01 * (torch.rand(1).item() - 0.5) for t in batch]

        # discounted returns with normalization
        G = []
        acc = 0.0
        for r in rewards[::-1]:
            acc = r + self.gamma * acc
            G.insert(0, acc)
        returns = torch.tensor(G, dtype=torch.float32)

        # Normalize returns for more stable training
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        probs = self.policy(states)

        # Add small epsilon to prevent log(0)
        eps = 1e-8
        probs = torch.clamp(probs, eps, 1.0 - eps)

        action_probs = probs.gather(1, actions.unsqueeze(-1)).squeeze()

        # negative log-likelihood with clipping for stability
        log_probs = torch.log(action_probs)
        policy_loss = -(log_probs * returns).mean()

        # entropy bonus with increased coefficient to encourage more exploration
        entropy = -torch.sum(probs * torch.log(probs), dim=1).mean()
        entropy_bonus = 0.05 * entropy  # increased coefficient for more exploration

        # total loss (negative because we're minimizing)
        loss = policy_loss - entropy_bonus

        return loss

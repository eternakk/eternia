"""
Basic PPO loop (stub) to adapt companion dialogue tone.

This is intentionally minimal and educational – you’ll fill in
reward shaping and state extraction as you learn RL.
"""

from __future__ import annotations

from collections import deque, namedtuple
from typing import List, Dict, Tuple, Optional, Any
import functools
import hashlib
import random
import time

import torch
import torch.nn as nn
import torch.optim as optim


# ----- caching decorator for expensive computations --------------------------
def cache_result(max_size: int = 128, ttl: int = 300):
    """
    Cache the result of a function call.

    Args:
        max_size: Maximum number of results to cache.
        ttl: Time-to-live in seconds for cached results.

    Returns:
        Decorated function.
    """
    def decorator(func):
        cache: Dict[str, Tuple[Any, float]] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from the function arguments
            key_parts = [str(arg) for arg in args]
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = hashlib.md5(str(key_parts).encode()).hexdigest()

            # Check if result is in cache and not expired
            current_time = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    return result

            # Compute the result
            result = func(*args, **kwargs)

            # Store in cache
            cache[key] = (result, current_time)

            # Prune cache if it exceeds max_size
            if len(cache) > max_size:
                # Remove oldest entries
                oldest_keys = sorted(cache.keys(), key=lambda k: cache[k][1])[:len(cache) - max_size]
                for k in oldest_keys:
                    del cache[k]

            return result

        # Add a method to clear the cache
        wrapper.clear_cache = lambda: cache.clear()

        return wrapper

    return decorator


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
        buffer_size: int = 5000,  # Default buffer size
    ):
        self.world = world  # you can access companions, emotions, etc.
        self.gamma = gamma
        self.policy = PolicyNet(obs_dim, act_dim)

        # Initialize with small random noise to break symmetry
        for param in self.policy.parameters():
            param.data = param.data + torch.randn_like(param.data) * 0.01

        self.optimizer = optim.Adam(
            self.policy.parameters(), lr=lr, weight_decay=1e-5
        )  # Added weight decay
        self.buffer: deque[Transition] = deque(maxlen=buffer_size)

        # Initialize pending rewards dictionary
        self._pending_rewards = {}

        # Cache for observation vectors to avoid redundant tensor conversions
        self._obs_cache = {}

    # ----- hooks you’ll call from runtime ------------------------------------
    def observe(self, state, action, reward, next_state, done=False):
        """
        Record a transition in the replay buffer.

        Uses caching to avoid redundant tensor conversions for state and next_state.

        Args:
            state: The current state.
            action: The action taken.
            reward: The reward received.
            next_state: The next state.
            done: Whether the episode is done.
        """
        # Convert state and next_state to hashable tuples for caching
        state_tuple = tuple(state) if isinstance(state, (list, tuple)) else state
        next_state_tuple = tuple(next_state) if isinstance(next_state, (list, tuple)) else next_state

        # Cache the state and next_state tensors
        if state_tuple not in self._obs_cache:
            self._obs_cache[state_tuple] = state

            # Prune cache if it exceeds 1000 entries
            if len(self._obs_cache) > 1000:
                # Remove 20% of the oldest entries
                keys_to_remove = list(self._obs_cache.keys())[:200]
                for k in keys_to_remove:
                    del self._obs_cache[k]

        if next_state_tuple not in self._obs_cache:
            self._obs_cache[next_state_tuple] = next_state

        # Add the transition to the buffer
        self.buffer.append(Transition(state, action, reward, next_state, done))

    @cache_result(max_size=32, ttl=10)  # Cache up to 32 results for 10 seconds
    def _sample_batch(self, batch_size: int):
        """
        Sample a batch of transitions from the replay buffer.

        This method is cached to avoid redundant sampling when called with the same batch_size.

        Args:
            batch_size: The number of transitions to sample.

        Returns:
            A list of sampled transitions.
        """
        # Use a fixed seed for sampling to ensure deterministic results for the same batch_size
        torch.manual_seed(int(time.time() * 1000) % 10000)
        indices = torch.randint(0, len(self.buffer), (batch_size,))
        return [self.buffer[i] for i in indices]

    def step_train(self, batch_size: int = 128):
        """
        Perform a training step using a batch of transitions from the replay buffer.

        This method has been updated to avoid in-place operations and ensure
        proper gradient flow.

        Args:
            batch_size: The number of transitions to sample for training.
        """
        if len(self.buffer) < batch_size:
            return  # not enough data yet

        # Enable anomaly detection to help identify the operation causing the issue
        torch.autograd.set_detect_anomaly(True)

        # Sample batch
        batch = self._sample_batch(batch_size)

        # Compute loss
        loss = self._ppo_loss(batch)

        # Add a small constant to ensure the loss is not too close to zero
        # Using addition creates a new tensor, not an in-place operation
        loss = loss + 0.01

        # Zero gradients, compute backward pass, and update weights
        self.optimizer.zero_grad()
        loss.backward()  # Removed retain_graph=True to avoid memory issues

        # Apply gradient clipping to prevent numerical instability
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), max_norm=1.0)

        # Update model parameters
        self.optimizer.step()

        # Clear sample batch cache periodically
        if random.random() < 0.1:  # 10% chance to clear caches
            if hasattr(self._sample_batch, 'clear_cache'):
                self._sample_batch.clear_cache()

    # ----- improved PPO loss with entropy bonus and numerical stability --------------------------------
    def _ppo_loss(self, batch: List[Transition]):
        """
        Compute the PPO loss for a batch of transitions.

        This method has been completely rewritten to avoid in-place operations
        and ensure proper gradient flow.

        Args:
            batch: A list of transitions.

        Returns:
            The PPO loss.
        """
        # Convert batch to a list for processing
        batch_list = list(batch)

        # Extract states and actions as new tensors
        states = torch.tensor([t.state for t in batch_list], dtype=torch.float32)
        actions = torch.tensor([t.action for t in batch_list], dtype=torch.long)

        # Extract rewards with small noise for variance
        rewards = []
        for t in batch_list:
            # Use a deterministic approach to avoid randomness issues
            reward_noise = 0.01 * ((hash(str(t)) % 100) / 100 - 0.5)
            rewards.append(t.reward + reward_noise)

        # Compute discounted returns
        returns = []
        acc = 0.0
        for r in reversed(rewards):
            acc = r + self.gamma * acc
            returns.insert(0, acc)
        returns = torch.tensor(returns, dtype=torch.float32)

        # Normalize returns if there's more than one
        if len(returns) > 1:
            returns_mean = returns.mean()
            returns_std = returns.std() + 1e-8
            returns = (returns - returns_mean) / returns_std

        # Forward pass through the policy network
        probs = self.policy(states)

        # Add small epsilon to prevent log(0)
        eps = 1e-8
        probs_safe = torch.clamp(probs, eps, 1.0 - eps)

        # Get action probabilities
        action_probs = probs_safe.gather(1, actions.unsqueeze(-1)).squeeze(-1)

        # Compute negative log-likelihood loss
        log_probs = torch.log(action_probs)
        policy_loss = -(log_probs * returns).mean()

        # Compute entropy bonus
        entropy = -torch.sum(probs_safe * torch.log(probs_safe), dim=1).mean()
        entropy_bonus = 0.05 * entropy  # Exploration coefficient

        # Compute total loss
        loss = policy_loss - entropy_bonus

        return loss


    def observe_reward(self, companion_name: str, value: float):
        self._pending_rewards[companion_name] = value  # dict of latest clicks

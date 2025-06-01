"""
Test script to verify that the PPOTrainer class works correctly with the buffer_size parameter.
"""

import torch
from modules.ai_ml_rl.rl_companion_loop import PPOTrainer

def test_ppo_trainer():
    """Test that the PPOTrainer class works correctly with the buffer_size parameter."""
    print("Testing PPOTrainer with buffer_size parameter...")
    
    # Create a PPOTrainer instance with a buffer_size parameter
    trainer = PPOTrainer(
        obs_dim=10,
        act_dim=5,
        world=None,  # Not needed for this test
        buffer_size=1000,  # Should be accepted now
    )
    
    # Check that the buffer has the correct maxlen
    assert trainer.buffer.maxlen == 1000, f"Expected buffer.maxlen to be 1000, got {trainer.buffer.maxlen}"
    
    # Test adding items to the buffer
    for i in range(10):
        state = [i] * 10
        action = i % 5
        reward = float(i)
        next_state = [i + 1] * 10
        trainer.observe(state, action, reward, next_state)
    
    # Check that the buffer has the correct number of items
    assert len(trainer.buffer) == 10, f"Expected buffer to have 10 items, got {len(trainer.buffer)}"
    
    print("All tests passed!")

if __name__ == "__main__":
    test_ppo_trainer()
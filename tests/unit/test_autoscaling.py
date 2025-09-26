import time
from modules.autoscaling import AutoScaler, ScaleUpEvent, ScaleDownEvent
from modules.utilities.event_bus import event_bus


def test_autoscaler_scales_up_and_down():
    events: list = []

    def on_up(evt: ScaleUpEvent):
        events.append(("up", evt.desired_replicas))

    def on_down(evt: ScaleDownEvent):
        events.append(("down", evt.desired_replicas))

    # Subscribe temporary handlers
    event_bus.subscribe(ScaleUpEvent, on_up)
    event_bus.subscribe(ScaleDownEvent, on_down)

    try:
        scaler = AutoScaler(min_replicas=1, max_replicas=3, scale_up_threshold=0.8, scale_down_threshold=0.2, cooldown_seconds=0, initial_replicas=1)

        # High load -> scale up
        decision = scaler.evaluate(0.9)
        assert decision == "up"
        assert scaler.current_replicas == 2

        # High load again -> scale up to max
        decision = scaler.evaluate(0.95)
        assert decision == "up"
        assert scaler.current_replicas == 3

        # Below threshold -> scale down
        decision = scaler.evaluate(0.1)
        assert decision == "down"
        assert scaler.current_replicas == 2

        # No change in mid range
        decision = scaler.evaluate(0.5)
        assert decision is None

        # Verify events captured
        assert events[0] == ("up", 2)
        assert events[1] == ("up", 3)
        assert events[2] == ("down", 2)
    finally:
        # Cleanup handlers
        event_bus.unsubscribe(ScaleUpEvent, on_up)
        event_bus.unsubscribe(ScaleDownEvent, on_down)

import pytest
from modules.utilities.event_bus import event_bus, Event


class ChaosEvent(Event):
    def __init__(self, payload: str):
        self.payload = payload


def test_event_bus_resilience_with_faulty_handler():
    calls = []

    def faulty_handler(evt: ChaosEvent):
        raise RuntimeError("Injected failure")

    def healthy_handler(evt: ChaosEvent):
        calls.append(evt.payload)

    event_bus.subscribe(ChaosEvent, faulty_handler)
    event_bus.subscribe(ChaosEvent, healthy_handler)

    try:
        # Publish should not raise despite faulty handler; errors are logged internally
        event_bus.publish(ChaosEvent("ok"))
        # Healthy handler should still have been called
        assert calls == ["ok"]
    finally:
        event_bus.unsubscribe(ChaosEvent, faulty_handler)
        event_bus.unsubscribe(ChaosEvent, healthy_handler)

from collections import defaultdict
from typing import Callable, Dict, List, Any

EventHandler = Callable[[Any], None]


class DomainEvents:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)

    def register(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def publish(self, event_name: str, payload: Any) -> None:
        for handler in self._handlers[event_name]:
            handler(payload)


domain_events = DomainEvents()


# Example usage: log when a product is loaded (for metrics)
def on_product_read(event):
    # Push to metrics / logs, etc.
    pass


domain_events.register("product_read", on_product_read)

from src.notifier import InMemoryNotifier, StdoutNotifier


def map_notifier(notifier_type: str | None = None) -> InMemoryNotifier | StdoutNotifier:
    if notifier_type == "IN_MEMORY":
        return InMemoryNotifier()
    elif notifier_type == "STDOUT":
        return StdoutNotifier()
    else:
        raise ValueError(f"Unknown notifier type: {notifier_type}")

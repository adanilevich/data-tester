from .demo.demo_backend_factory import DemoBackendFactory
from .dummy.dummy_backend_factory import DummyBackendFactory


def map_platform(platform_type: str) -> DemoBackendFactory | DummyBackendFactory:
    if platform_type == "DEMO":
        return DemoBackendFactory()
    elif platform_type == "DUMMY":
        return DummyBackendFactory()
    else:
        raise ValueError(f"Unknown data platform type: {platform_type}")

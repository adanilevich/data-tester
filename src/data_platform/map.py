from src.data_platform import DemoDataPlatformFactory, DummyPlatformFactory


def map_platform(platform_type: str) -> DemoDataPlatformFactory | DummyPlatformFactory:
    if platform_type == "DEMO":
        return DemoDataPlatformFactory()
    elif platform_type == "DUMMY":
        return DummyPlatformFactory()
    else:
        raise ValueError(f"Unknown data platform type: {platform_type}")

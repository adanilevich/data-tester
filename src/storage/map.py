from src.storage import FileStorage, DictStorage, IStorage


def map_storage(storage_engine: str | None = None) -> IStorage:
    if storage_engine == "DICT":
        return DictStorage()
    elif storage_engine in ["LOCAL", "GCS", "MEMORY"]:
        return FileStorage()
    else:
        raise ValueError(f"Unknown storage engine: {storage_engine}")

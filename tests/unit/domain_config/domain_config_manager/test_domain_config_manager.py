import pytest
from pathlib import Path
from src.domain_config.adapters import FileStorageError, FileStorage
from gcsfs import GCSFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore


PATH = Path(__file__).parent.absolute
int_ = 1234


class TestFileStorage:

    local = LocalFileSystem()
    fs = FileStorage()
    files = [
        ("first.txt", "content", "string"),
        ("second.bytes", int_.to_bytes(), "bytes"),
        ("/subfolder/third.txt", "new content", "string"),
    ]

    @pytest.fixture
    def setup_local_files():
        
        for filepath, content, content_type in self.files


    def test_correctly_setting_file_systems(self):

        assert isinstance(self.fs.protocols["local:"], LocalFileSystem)
        assert isinstance(self.fs.protocols["gs://"], GCSFileSystem)

    @pytest.mark.parametrize("protocol,error", (
        ("local:", False),
        ("http", True)
    ))
    def test_unknown_protocols_lead_to_errors(self, protocol, error):
        if error:
            with pytest.raises(FileStorageError):
                _ = self.fs._fs(protocol)
        else:
            assert isinstance(self.fs._fs(protocol), LocalFileSystem | GCSFileSystem)

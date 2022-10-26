
import logging
import shutil

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Generator

import pytest

import helpers


_log = logging.getLogger('fair-crcc-get-data.tests')


@pytest.fixture
def s3_connection() -> Dict[str, Any]:
    return dict(
        access_key_id="crc-user",
        secret_access_key="crc-user-s3cr3t",
        host="http://localhost:9000",
        verify=False)


@pytest.fixture
def run_dir() -> Generator[Path, None, None]:
    with TemporaryDirectory(prefix="wf_test_dir") as dirname:
        yield Path(dirname)


@pytest.fixture
def recipient_key(run_dir: Path) -> Path:
    key_file_path = (Path(__file__).parent / "recipient.private_key").absolute()
    dest_path = run_dir / key_file_path.name
    shutil.copy(key_file_path, dest_path)
    return dest_path


@pytest.fixture
def destination_local_path() -> Generator[Path, None, None]:
    # destination_local_path is the local directory to which the workflow destination
    # is mapped, both through s3 and local storage.
    d = helpers.destination_local_path()
    d.mkdir(parents=True, exist_ok=False)
    try:
        yield d
    finally:
        #_log.warning("Not removing destination directory %s", d)
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def config_template(recipient_key: Path, s3_connection: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'recipient_key': str(recipient_key),
        'source': { 'type': 'S3',
             'root_path': 'test-bucket/fake-repo/',
             'connection': deepcopy(s3_connection)
        },
        'destination': {
            'type': 'S3',
            'root_path': str(helpers.destination_root_path()),
            'connection': deepcopy(s3_connection)
        }
    }

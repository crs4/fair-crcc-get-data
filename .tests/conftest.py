
import logging
import os
import shutil
import subprocess as sp
import yaml

from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Any, Dict, Generator

import pytest

import helpers


_log = logging.getLogger('fair-crcc-get-data.tests')


@pytest.fixture(scope='session')
def minio() -> Generator[Dict[str, Any], None, None]:
    docker_compose_exec = shutil.which("docker-compose")
    if not docker_compose_exec:
        raise RuntimeError("Could not find docker-compose executable in PATH")

    connection_info = dict(
        access_key_id="crc-user",
        secret_access_key="crc-user-s3cr3t",
        host="http://localhost:9000",
        verify=False)

    minio_storage_dir = helpers.local_object_space()
    docker_compose = helpers.minio_create_docker_compose_def(connection_info, minio_storage_dir)

    with NamedTemporaryFile(mode="w", prefix="wf_test_docker-compose", suffix=".yml") as dc_file:
        yaml.safe_dump(docker_compose, dc_file)
        dc_file.flush()

        if _log.isEnabledFor(logging.DEBUG):
            with open(dc_file.name) as f:
                _log.debug("Minio docker-compose file:\n%s", f.read())

        # Ensure the storage
        minio_storage_dir.mkdir(parents=True, exist_ok=True)
        cmd = [docker_compose_exec, "-f", dc_file.name, "up", "-d"]
        _log.info("Launching minio docker-compose")
        sp.check_call(cmd)

        try:
            _log.info("Waiting for minio to start...")
            if not helpers.minio_wait(connection_info['host'], num_retries=10, sleep_time=5):
                raise RuntimeError("Minio did not come up. Aborting")

            yield connection_info
        finally:
            try:
                # bring down the docker-compose
                _log.info("Bringing down minio...")
                sp.check_call([docker_compose_exec, "-f", dc_file.name, "down", "-v"])
                _log.info("minio shut down.")
            except sp.CalledProcessError as e:
                _log.error("Exception raised while trying to bring down minio docker-compose")
                _log.exception(e)


@pytest.fixture
def s3_connection(minio) -> Dict[str, Any]:
    return deepcopy(minio)


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

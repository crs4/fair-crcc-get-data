
import logging
import os
import shutil
import subprocess as sp
import time

from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Any, Dict
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError

import yaml


_log = logging.getLogger('fair-crcc-get-data.tests')

# module-level variable for a TemporaryDirectory used as a Singularity image cache.
# On program exit the directory is cleaned up automatically.
_img_cache = None


def get_img_cache() -> Path:
    global _img_cache
    if _img_cache is None:
        _img_cache = TemporaryDirectory(prefix="wf_image_cache")
    return Path(_img_cache.name)


def repo_root() -> Path:
    # This should be REPO/.tests/helpers.py. We thus get the
    # project root path by returning the parent of the parent.
    return Path(__file__).parent.parent.absolute()


def local_object_space() -> Path:
    return repo_root() / '.tests/integration/minio-space/'


def destination_root_path() -> Path:
    return Path('test-bucket/destination')


def destination_local_path() -> Path:
    return local_object_space() / destination_root_path()


def fake_repo_root_path() -> Path:
    return Path('test-bucket/fake-repo/')


def fake_repo_local_path() -> Path:
    return local_object_space() / fake_repo_root_path()


def run_workflow(wf_config: Dict[str, Any], run_directory: Path) -> None:
    standard_options = [
        "--cores",
        "--show-failed-logs",
        "--use-singularity",
        "--singularity-prefix", str(get_img_cache()),
        "--snakefile", str(Path(repo_root(), "workflow/Snakefile").absolute()),
    ]
    snakemake_exec = shutil.which("snakemake")
    if not snakemake_exec:
        raise RuntimeError("Could not find snakemake executable in PATH")

    with NamedTemporaryFile(mode="w", prefix="test_workflow_cfg") as cfg_file:
        yaml.safe_dump(wf_config, cfg_file)
        cfg_file.flush()

        cmd = [
            snakemake_exec,
            "--configfile", cfg_file.name
        ] + standard_options

        if _log.isEnabledFor(logging.DEBUG):
            _log.debug("About to run snakemake in directory %s", run_directory)
            _log.debug("Directory contents: %s", os.listdir(run_directory))
            _log.debug("config file path: %s", cfg_file.name)
            with open(cfg_file.name) as f:
                _log.debug("config file contents: \n%s", f.read())

        try:
            sp.check_call(cmd, cwd=run_directory)
        except sp.CalledProcessError:
            _log.debug("Workflow work directory contents: %s", os.listdir(run_directory))
            for item in (run_directory / 'logs').glob('**/*'):
                if item.is_file():
                    _log.error("======== Log file: %s = = = = = =", item)
                    with open(item) as logfile:
                        _log.error(logfile.read() or "<file was empty>")
            raise


def minio_create_docker_compose_def(connection_info: Dict[str, Any], minio_storage_dir: Path) -> Dict[str, Any]:
    docker_compose = {
        'version': '3',
        'services': {
            'minio': {
                # This is the latest minio RELEASE of minio allowing us to access S3 data
                # directly through the underlying file system (which is mounted in the
                # container). The minio discontinued that feature in June 2022.  If an upgrade
                # is forced in the future, we can either reimplement the tests to treat the
                # file system storage space as opaque or replace minio with other options.
                'image': 'minio/minio:RELEASE.2022-05-26T05-48-41Z.fips',
                'ports': ['9000:9000', '9001:9001'],
                'environment': [
                    "MINIO_BROWSER=on",
                    "MINIO_HTTP_TRACE=/dev/stderr",
                    f"MINIO_ROOT_USER={connection_info['access_key_id']}",
                    f"MINIO_ROOT_PASSWORD={connection_info['secret_access_key']}",
                    f"AWS_ACCESS_KEY_ID={connection_info['access_key_id']}",
                    f"AWS_SECRET_ACCESS_KEY={connection_info['secret_access_key']}",
                    "AWS_DEFAULT_REGION=",
                    f"AWS_S3_ENDPOINT={urlparse(connection_info['host']).netloc}",
                    f"STORAGE_BUCKET={destination_root_path().parts[0]}"
                ],
                'entrypoint': [
                    '/bin/sh',
                    '-c',
                    'exec /usr/bin/docker-entrypoint.sh minio server --console-address :9001 /data'],
                'volumes': [str(minio_storage_dir.absolute()) + ':/data/'],
                'healthcheck': {'test': ['CMD',
                                         'curl',
                                         '-f',
                                         f"{connection_info['host']}/minio/health/live"],
                                'interval': '30s',
                                'timeout': '20s',
                                'retries': 3},
                'user': f"{os.geteuid()}:{os.getegid()}"
            }
        }
    }
    return docker_compose


def minio_wait(minio_url: str, num_retries: int=10, sleep_time: int=5) -> bool:
    if num_retries <= 0:
        raise ValueError(f"num_retries must be > 0 (got {num_retries})")
    if sleep_time <= 0:
        raise ValueError(f"sleep_time must be > 0 (got {sleep_time})")

    minio_check_url = f"{minio_url}/minio/health/live"
    for i in range(num_retries):
        try:
            with urlopen(minio_check_url) as response:
                if 200 <= response.status < 300:
                    _log.info("Minio seems ok!")
                    return True
        except (URLError, ConnectionError) as e:
            _log.debug("Attempting to connect to minio generated %s", e)
        _log.debug("Minio isn't answering yet")
        if i < num_retries - 1:
            time.sleep(sleep_time)
    return False

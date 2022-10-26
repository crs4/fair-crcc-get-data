
import logging
import os
import shutil
import subprocess as sp

from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Any, Dict

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
        "--verbose",
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

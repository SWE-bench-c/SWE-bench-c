from swebench.harness.constants import DEFAULT_GIT_HOST
from swebench.harness.dockerfiles.javascript import (
    _DOCKERFILE_BASE_JS,
    _DOCKERFILE_ENV_JS,
    _DOCKERFILE_INSTANCE_JS,
)

from swebench.harness.dockerfiles.python import (
    _DOCKERFILE_BASE_PY,
    _DOCKERFILE_ENV_PY,
    _DOCKERFILE_INSTANCE_PY,
)
from swebench.harness.dockerfiles import c

_DOCKERFILE_BASE = {
    "py": _DOCKERFILE_BASE_PY,
    "js": _DOCKERFILE_BASE_JS,
    "c": c._DOCKERFILE_BASE_C,
}

_DOCKERFILE_ENV = {
    "py": _DOCKERFILE_ENV_PY,
    "js": _DOCKERFILE_ENV_JS,
    "c": c._DOCKERFILE_ENV_C,
}

_DOCKERFILE_INSTANCE = {
    "py": _DOCKERFILE_INSTANCE_PY,
    "js": _DOCKERFILE_INSTANCE_JS,
    "c": c._DOCKERFILE_INSTANCE_C,
}

def get_dockerfile_base(platform, arch, language):
    if arch == "arm64":
        conda_arch = "aarch64"
    else:
        conda_arch = arch
    return _DOCKERFILE_BASE[language].format(
        platform=platform,
        conda_arch=conda_arch
    )


def get_dockerfile_env(platform, arch, language, repo, **kwargs):
    repo_link = f"{DEFAULT_GIT_HOST}/{repo}.git"
    return _DOCKERFILE_ENV[language].format(
        platform=platform,
        arch=arch,
        repo_link=repo_link,
        **kwargs
    )


def get_dockerfile_instance(platform, language, env_image_name):
    return _DOCKERFILE_INSTANCE[language].format(
        platform=platform,
        env_image_name=env_image_name
    )

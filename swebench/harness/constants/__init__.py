from swebench.harness.constants.constants import *
from swebench.harness.constants.javascript import *
from swebench.harness.constants.python import *
from swebench.harness.constants import c

MAP_REPO_VERSION_TO_SPECS = {
    **MAP_REPO_VERSION_TO_SPECS_JS,
    **MAP_REPO_VERSION_TO_SPECS_PY,
    **c.MAP_REPO_VERSION_TO_SPECS_C
}

MAP_REPO_TO_INSTALL = {
    **MAP_REPO_TO_INSTALL_JS,
    **MAP_REPO_TO_INSTALL_PY,
    **c.MAP_REPO_TO_INSTALL_C,
}

MAP_REPO_TO_EXT = {
    **{k: "js" for k in MAP_REPO_VERSION_TO_SPECS_JS.keys()},
    **{k: "py" for k in MAP_REPO_VERSION_TO_SPECS_PY.keys()},
    **{k: "c" for k in c.MAP_REPO_VERSION_TO_SPECS_C.keys()},
}

LATEST = "latest"
USE_X86 = USE_X86_PY
DEFAULT_GIT_HOST = "https://github.com"

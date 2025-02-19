SPECS_JQ = {
    k: {
        "test_cmd": "make -j$(nproc)  && make -j $(nproc) check -s",
    }
    for k in ["jq-1.7rc2", "jq-1.7rc1", "jq-1.6rc1", "jq-1.5rc2", "jq-1.5rc1", "jq-1.3"]
}

INSTALL_JQ = "git submodule update --init \
        && autoreconf -i \
        && ./configure --with-oniguruma=builtin"


MAP_REPO_VERSION_TO_SPECS_C = {
    "jqlang/jq": SPECS_JQ,
}

MAP_REPO_TO_INSTALL_C = {
    "jqlang/jq": INSTALL_JQ,
}



SPECS_JQ1 = {
    version: {
        "test_cmd": "autoreconf -i \
            && ./configure --with-oniguruma=builtin && make -j$(nproc)  && make -j $(nproc) check -s",
        "apt-pkgs": ["bison", "flex", "libtool","libonig-dev"],
    }
    for version in ["jq-1.7rc2", "jq-1.7rc1", "jq-1.6rc1"]
}

SPECS_JQ2 = {
    version: {
        "test_cmd": "autoreconf -i \
            && ./configure --with-oniguruma=builtin && make -j$(nproc)  && make -j $(nproc) check -s",
        "apt-pkgs": ["bison", "flex", "libtool","libonig-dev"],
    }
    for version in ["jq-1.6rc1"]
}


SPECS_JQ3 = {
    version: {
        "test_cmd": "autoreconf -i \
            && ./configure && make -j$(nproc)  && make -j $(nproc) check -s",
        "apt-pkgs": ["bison", "flex", "libtool","libonig-dev"],
    }
    for version in [ "jq-1.5rc1", "jq-1.5rc2", "jq-1.3"]
}

SPECS_ZSTD = {
    version: {
        "test_cmd": "make -k --trace -j$(nproc) test",
        "apt-pkgs": [],
    }
    for version in ["zstd-0.4.2"]
}

INSTALL_JQ = "git submodule update --init "


MAP_REPO_VERSION_TO_SPECS_C = {
    "jqlang/jq": {**SPECS_JQ1, **SPECS_JQ2, **SPECS_JQ3},
    "facebook/zstd": SPECS_ZSTD,
}

MAP_REPO_TO_INSTALL_C = {
    "jqlang/jq": INSTALL_JQ,
}

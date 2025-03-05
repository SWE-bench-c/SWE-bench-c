SPECS_JQ1 = {
    version: {
        "test_cmd": "autoreconf -i \
            && ./configure --with-oniguruma=builtin && make -j${TEST_MAKE_THREADS}  && make -j${TEST_MAKE_THREADS}  check -s",
        "apt-pkgs": ["bison", "flex", "libtool", "libonig-dev"],
    }
    for version in ["jq-1.7rc2", "jq-1.7rc1", "jq-1.6rc1"]
}

SPECS_JQ2 = {
    version: {
        "test_cmd": "autoreconf -i \
            && ./configure --with-oniguruma=builtin && make -j${TEST_MAKE_THREADS}  && make -j${TEST_MAKE_THREADS}  check -s",
        "apt-pkgs": ["bison", "flex", "libtool", "libonig-dev"],
    }
    for version in ["jq-1.6rc1"]
}


SPECS_JQ3 = {
    version: {
        "test_cmd": "autoreconf -i \
            && ./configure && make -j${TEST_MAKE_THREADS}  && make -j${TEST_MAKE_THREADS} check -s",
        "apt-pkgs": ["bison", "flex", "libtool", "libonig-dev"],
    }
    for version in ["jq-1.5rc1", "jq-1.5rc2", "jq-1.3"]
}

SPECS_ZSTD = {
    "playtest": {
        "test_cmd": "make -j4 zstd \
                && cd tests \
                && make -j4 datagen \
                && ZSTD=../programs/zstd ./playTests.sh \
                && echo 'playtest result => pass' \
                || echo 'playtest result => fail'; \
                cd ..",
        "apt-pkgs": ["file", "python3"],
    },
    "fuzztest": {
        "test_cmd": "make -j4 zstd \
                && cd tests \
                && make -j4 fuzztest \
                && echo 'fuzztest result => pass' \
                || echo 'fuzztest result => fail'; \
                cd ..",
        "apt-pkgs": ["file"],
    },
    "cli_tests": {
        "test_cmd": "make -j4 zstd \
                && cd tests \
                && make -j4 test-cli-tests \
                && echo 'cli_tests result => pass' \
                || echo 'cli_tests result => fail'; \
                cd ..",
        "apt-pkgs": ["file"],
    },
    "regressiontest": {
        "test_cmd": "make -j4 zstd \
                && cd tests \
                && make -j4 regressiontest \
                && echo 'regressiontest result => pass' \
                || echo 'regressiontest result => fail'; \
                cd ..",
        "apt-pkgs": ["file"],
    },
    "grep_test": {
        "test_cmd": "make -j4 zstd \
                && cd tests \
                && make -j4 test-zstdgrep \
                && echo 'grep_test result => pass' \
                || echo 'grep_test result => fail'; \
                cd ..",
        "apt-pkgs": ["file"],
    },
    "zstream_tests": {
        "test_cmd": "make -j4 zstd \
                && cd tests \
                && make -j4 test-zstream \
                && echo 'zstream_tests result => pass' \
                || echo 'zstream_tests result => fail'; \
                cd ..",
        "apt-pkgs": ["file"],
    },
    "zstd-0.4.2": {
        "test_cmd": "make -k -j4 --trace check",
        "apt-pkgs": ["file"],
    },
}

INSTALL_JQ = "git submodule update --init "


MAP_REPO_VERSION_TO_SPECS_C = {
    "jqlang/jq": {**SPECS_JQ1, **SPECS_JQ2, **SPECS_JQ3},
    "facebook/zstd": SPECS_ZSTD,
}

MAP_REPO_TO_INSTALL_C = {
    "jqlang/jq": INSTALL_JQ,
}

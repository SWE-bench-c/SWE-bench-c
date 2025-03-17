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
        "test_cmd": """( \\
                make -j${TEST_MAKE_THREADS} zstd \\
                && cd tests \\
                && make -j${TEST_MAKE_THREADS} datagen \\
                && ZSTD=../programs/zstd ./playTests.sh \\
                && echo 'playtest result => pass' \\
                || echo 'playtest result => fail' \\
                ) #""",
        "apt-pkgs": ["file", "python3"],
    },
    "fuzztest": {
        "test_cmd": """(
                make -j${TEST_MAKE_THREADS} zstd \\
                && cd tests \\
                && make -j${TEST_MAKE_THREADS} fuzztest \\
                && echo 'fuzztest result => pass' \\
                || echo 'fuzztest result => fail' \\
                ) #""",
        "apt-pkgs": ["file"],
    },
    "cli_tests": {
        "test_cmd": """(
                make -j${TEST_MAKE_THREADS} zstd \\
                && cd tests \\
                && make -j${TEST_MAKE_THREADS} test-cli-tests \\
                && echo 'cli_tests result => pass' \\
                || echo 'cli_tests result => fail'
                ) #""",
        "apt-pkgs": ["file", "python3"],
    },
    "regressiontest": {
        "test_cmd": """(
                make -j${TEST_MAKE_THREADS} zstd \\
                && make install \\
                && cd tests/regression \\
                && make clean \\
                && make -j${TEST_MAKE_THREADS} test \\
                && ./test --cache data-cache --zstd ../../zstd --output new-results.csv --diff results.csv \\
                && echo 'regressiontest result => pass' \\
                || echo 'regressiontest result => fail'
                ) #""",
        "apt-pkgs": ["file", "libcurl4-openssl-dev"],
    },
    "grep_test": {
        "test_cmd": """( \\
                make -j${TEST_MAKE_THREADS} zstd \\
                && cd tests \\
                && make -j${TEST_MAKE_THREADS} test-zstdgrep \\
                && echo 'grep_test result => pass' \\
                || echo 'grep_test result => fail' \\
                ) #""",
        "apt-pkgs": ["file"],
    },
    "zstream_tests": {
        "test_cmd": """(make -j${TEST_MAKE_THREADS} zstd \\
                && cd tests \\
                && make -j${TEST_MAKE_THREADS} test-zstream \\
                && echo 'zstream_tests result => pass' \\
                || echo 'zstream_tests result => fail'
                ) #""",
        "apt-pkgs": ["file"],
    },
    "zstd-0.4.2": {
        "test_cmd": "make -k -j${TEST_MAKE_THREADS} --trace check",
        "apt-pkgs": ["file"],
    },
}

SPECS_REDIS = {
    version: {
        "test_cmd": """(
            make distclean \\
            && make -j${TEST_MAKE_THREADS} BUILD_TLS=yes \\
            && ./utils/gen-test-certs.sh > /dev/null \\
            && ./runtest --durable --tls | ansi2txt
        ) #""",
        "apt-pkgs": ["libssl-dev", "pkg-config", "tcl", "tcl-tls", "procps", "colorized-logs"],
    }
    for version in [
        "8.0-m04-int",
        "3.2.13",
        "6.0.20",
        "6.2.17",
        "5.0.14",
        "7.2.7",
        "3.0.7",
        "2.4.18",
    ]
}

INSTALL_JQ = "git submodule update --init "


MAP_REPO_VERSION_TO_SPECS_C = {
    "jqlang/jq": {**SPECS_JQ1, **SPECS_JQ2, **SPECS_JQ3},
    "facebook/zstd": SPECS_ZSTD,
    "redis/redis": SPECS_REDIS,
}

MAP_REPO_TO_INSTALL_C = {
    "jqlang/jq": INSTALL_JQ,
}

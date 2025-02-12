SPECS_JQ = {
    k: {
        # TODO: Add test command
        # "test_cmd": TEST_PYTEST,
    }
    for k in ["jq-1.7rc2", "jq-1.7rc1", "jq-1.6rc1", "jq-1.5rc2", "jq-1.5rc1", "jq-1.3"]
}

MAP_REPO_VERSION_TO_SPECS_C = {
    "jqlang/jq": SPECS_JQ,
}

MAP_REPO_TO_INSTALL_C = {}

import re

from swebench.harness.constants import TestStatus
from swebench.harness.test_spec.test_spec import TestSpec


def parse_log_jq(log: str, test_spec: TestSpec) -> dict[str, str]:
    """
    Parser for test logs generated from jq tests

    Args:
        log (str): log content
    Returns:
        dict: test case to test status mapping
    """

    # unused variable ignore
    del test_spec

    test_result_pattern = r"^(?P<result>\w+):\s*(?P<test>\S+)$"
    results = map(lambda line: re.search(test_result_pattern, line), log.splitlines())
    test_status_map = {}
    for match in results:
        if match is None:
            continue
        test_name = match.group("test")
        test_status = match.group("result")
        match test_status:
            case "PASS":
                status = TestStatus.PASSED.value
            case "FAIL":
                status = TestStatus.FAILED.value
            case "SKIP":
                status = TestStatus.SKIPPED.value
            case "XFAIL":
                status = TestStatus.XFAIL.value
            case "ERROR":
                status = TestStatus.ERROR.value
            case _:
                raise Exception(
                    f"Unexpected status: {test_status} found for test {test_name}"
                )
        test_status_map[test_name] = status
    return test_status_map


MAP_REPO_TO_PARSER_C = {
    "jqlang/jq": parse_log_jq,
}

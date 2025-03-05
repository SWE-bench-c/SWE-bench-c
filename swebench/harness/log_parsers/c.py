import re

from swebench.harness.constants import TestStatus
from swebench.harness.test_spec.test_spec import TestSpec


def parse_log_zstd(log: str, test_spec: TestSpec) -> dict[str, str]:
    """
    Parser for test logs generated from jq tests

    Args:
        log (str): log content
    Returns:
        dict: test case to test status mapping
    """
    test_status_map = {}
    if test_spec.version == "playtest":
        test_result_pattern = r"playtest result => (?P<result>\w+)"
        search_result = re.search(test_result_pattern, log)
        if search_result is None:
            test_status_map["playtest"] = TestStatus.FAILED.value
        else:
            if search_result.group('result') == "pass":
                test_status_map["playtest"] = TestStatus.PASSED.value
            else:
                test_status_map["playtest"] = TestStatus.FAILED.value
    elif test_spec.version == "fuzztest":
        test_result_pattern = r"fuzztest result => (?P<result>\w+)"
        search_result = re.search(test_result_pattern, log)
        if search_result is None:
            test_status_map["fuzztest"] = TestStatus.FAILED.value
        else:
            if search_result.group('result') == "pass":
                test_status_map["fuzztest"] = TestStatus.PASSED.value
            else:
                test_status_map["fuzztest"] = TestStatus.FAILED.value

    else:
        # unused variable ignore
        failed_test_trace_pattern = r"make(\[\d+\])?: \*+ \[(?P<makefile>\w+):(?P<line_no>\d+): (?P<test_name>\S+)]"
        failed_test_re = map(lambda line: re.search(failed_test_trace_pattern, line), log.splitlines())
        for match in failed_test_re:
            if match is None:
                continue
            test_name = match.group("test_name")
            test_status_map[test_name] = TestStatus.FAILED.value

        failed_tests = set(test_status_map.keys())
        success_test_trace_pattern = r"[^:]+:\d: update target '(?P<recipe>[^']+)' due to: .*"

        for match_line in  re.finditer(success_test_trace_pattern, log):
            test_name = match_line.group('recipe')
            if test_name not in failed_tests:
                test_status_map[test_name]= TestStatus.PASSED.value

    return test_status_map


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
    "facebook/zstd": parse_log_zstd,
}

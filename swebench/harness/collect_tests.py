import argparse
import logging
import json
from pathlib import Path

from swebench.harness.constants.constants import TestStatus
from .log_parsers import MAP_REPO_TO_PARSER

from typing import Any, Dict, List, Optional, Set, Tuple


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    if path.suffix == "jsonl":
        with open(path) as f:
            dataset = [json.loads(line) for line in f]
    else:
        # don't know whats the file type is, it should be json, so assuming json
        with open(path) as f:
            dataset = json.load(f)
    return dataset


def get_tests_with_status(pass_logs_dir: Path, fail_logs_dir, instance: Dict[str, Any])->Optional[Tuple[List[str], List[str]]]:
    """read test_output.txt and extract tests, append these tests to instance

    Args:
        logs_dir: logs directory path
        instance: test instance info from dataset
    """
    test_pass_log_path: Path = pass_logs_dir / instance["instance_id"] / "test_output.txt"
    test_fail_log_path: Path = fail_logs_dir / instance["instance_id"] / "test_output.txt"
    try:
        pass_logs = test_pass_log_path.read_text()
    except FileNotFoundError as e:
        logging.error(f"Failed to read pass logs from file: {test_pass_log_path} {e}, skipping")
        return

    try:
        fail_logs = test_fail_log_path.read_text()
    except FileNotFoundError as e:
        logging.error(f"Failed to read fail logs from file: {test_fail_log_path} {e}, skipping")
        return

    repo = instance["repo"]
    parser = MAP_REPO_TO_PARSER[repo]
    pass_tests = parser(pass_logs, None)
    fail_tests = parser(fail_logs, None)
    print(f"instance: {instance['instance_id']}, pass_to_pass: {pass_tests}, FAIL_TO_PASS: {fail_tests}")
    pass_to_pass: Set[str] = {test_name for test_name, status in pass_tests.items() if status == TestStatus.PASSED.value if fail_tests.get(test_name) == TestStatus.PASSED.value }
    fail_to_pass: Set[str] = {test_name for test_name, status in fail_tests.items() if status == TestStatus.FAILED.value if pass_tests.get(test_name) == TestStatus.PASSED.value}
    return (list(pass_to_pass), list(fail_to_pass))


def main(
    model: str,
    pass_run_id: str,
    fail_run_id: str,
    dataset_path: Path,
    output: Path,
    logs_base_path: Path,
):
    logging.basicConfig(
        level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    dataset = load_dataset(dataset_path)
    pass_logs_dir = logs_base_path / pass_run_id / model
    fail_logs_dir = logs_base_path / fail_run_id / model

    for instance in dataset:
        try:
            (pass_to_pass, fail_to_pass) = get_tests_with_status(pass_logs_dir, fail_logs_dir, instance)
        except TypeError:
            pass
        else:
            instance["PASS_TO_PASS"] = list(pass_to_pass)
            instance["FAIL_TO_PASS"] = list(fail_to_pass)

    with open(output, "w") as f:
        json.dump(dataset, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""collect all the tests from already ran test outputs and adds to dataset

        To get the results first run the test with gold predictions, then run the same tests with dummy predictions(which doesn't solves the issue).
        Then run this script to get PASS_TO_PASS and FAIL_TO_PASS tests
        """
    )
    parser.add_argument("model", help="model name of tests")
    parser.add_argument("pass_run_id", help="run id used by previous harness test with gold predictions")
    parser.add_argument("fail_run_id", help="run id used by previous harness test with dummy predictions")
    parser.add_argument("dataset", help="path to dataset")
    parser.add_argument("output", help="path to output dataset")
    parser.add_argument(
        "--eval_path",
        help="location where evaluation logs can be found",
        default="./logs/run_evaluation",
    )

    args = parser.parse_args()

    main(
        args.model,
        args.pass_run_id,
        args.fail_run_id,
        Path(args.dataset),
        Path(args.output),
        Path(args.eval_path),
    )

import argparse
import logging
import json
from pathlib import Path

from swebench.harness.constants.constants import TestStatus
from .log_parsers import MAP_REPO_TO_PARSER

from typing import Any, Dict, List, Set


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    if path.suffix == "jsonl":
        with open(path) as f:
            dataset = [json.loads(line) for line in f]
    else:
        # don't know whats the file type is, it should be json, so assuming json
        with open(path) as f:
            dataset = json.load(f)
    return dataset


def get_tests_with_status(logs_dir: Path, instance: Dict[str, Any]):
    """read test_output.txt and extract tests, append these tests to instance

    Args:
        logs_dir: logs directory path
        instance: test instance info from dataset
    """
    test_log_path: Path = logs_dir / instance["instance_id"] / "test_output.txt"
    try:
        logs = test_log_path.read_text()
    except FileNotFoundError as e:
        logging.error(f"Failed to read from file: {test_log_path}: {e}, skipping")
        return

    repo = instance["repo"]
    parser = MAP_REPO_TO_PARSER[repo]
    tests = parser(logs, None)
    pass_to_pass: Set[str] = set(instance.get("PASS_TO_PASS", []))
    fail_to_pass: Set[str] = set(instance.get("FAIL_TO_PASS", []))
    for test, status in tests.items():
        if status == TestStatus.PASSED.value and test not in fail_to_pass:
            pass_to_pass.add(test)
        else:
            fail_to_pass.add(test)
    instance["PASS_TO_PASS"] = list(pass_to_pass)
    instance["FAIL_TO_PASS"] = list(fail_to_pass)


def main(
    model: str, run_id: str, dataset_path: Path, output: Path, logs_base_path: Path
):
    logging.basicConfig(
        level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    dataset = load_dataset(dataset_path)
    logs_dir = logs_base_path / run_id / model

    for instance in dataset:
        get_tests_with_status(logs_dir, instance)

    with open(output, 'w') as f:
        json.dump(dataset, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="collect all the tests from already ran test outputs and adds to dataset"
    )
    parser.add_argument("model", help="model name of tests")
    parser.add_argument("run_id", help="run id used by previous harness test")
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
        args.run_id,
        Path(args.dataset),
        Path(args.output),
        Path(args.eval_path),
    )

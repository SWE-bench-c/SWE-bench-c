import argparse
import glob
import json
import logging
import os
import re
import subprocess

from multiprocessing import Pool
from typing import Optional

from swebench.versioning.utils import get_instances, split_instances

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def is_this_valid_release_tag(tag: str) -> bool:
    """checks whether given release tag looks atleast like release tag"""
    search_result = re.search(r"\d+\.\d*", tag)
    return search_result is not None


def get_version(instance)->Optional[str]:
    """
    Args:
        instance (dict): Instance to find version for
        path_repo (str): Path to repo to build
    Returns:
        str: Version text, if found
    """
    repo = instance["repo"]
    out_check = subprocess.run(
        f"git tag --no-contains {instance['base_commit']}",
        shell=True,
        capture_output=True,
    )
    if out_check.returncode != 0:
        logger.error(f"couldn't get tags for repo {repo}: {out_check.stderr}")
        return None
    try:
        release_tag = next(
            filter(
                lambda t: is_this_valid_release_tag(t),
                reversed(out_check.stdout.decode().splitlines()),
            )
        )

    except StopIteration:
        logger.error(
            f"couldn't get tags for repo {repo}: there are no tags or there are no valid tags"
        )
        return None
    return release_tag



def get_versions_from_build(data: dict):
    """
    Logic for looking up versions by building the repo at the instance's base
    commit and looking for the version according to repo-specific paths.

    Args:
        data (dict): Dictionary of data for building a repo for any task instance
            in a given list.
    """
    data_tasks, path_repo, save_path = (
        data["data_tasks"],
        data["path_repo"],
        data["save_path"],
    )
    # Change directory to repo testbed
    cwd = os.getcwd()
    os.chdir(path_repo)

    for instance in data_tasks[::-1]:
        # Reset repo to base commit
        subprocess.run(
            "git restore .", check=True, shell=True, stdout=subprocess.DEVNULL
        )
        subprocess.run(
            "git reset HEAD .", check=True, shell=True, stdout=subprocess.DEVNULL
        )
        subprocess.run(
            "git clean -fd", shell=True, check=True, stdout=subprocess.DEVNULL
        )
        out_check = subprocess.run(
            f"git -c advice.detachedHead=false checkout {instance['base_commit']}",
            shell=True,
            stdout=subprocess.DEVNULL,
        )
        if out_check.returncode != 0:
            logger.error(f"[{instance['instance_id']}] Checkout failed")
            continue

        # Look up version according to repo-specific paths
        version = get_version(instance)
        instance["version"] = version
        logger.info(f"For instance {instance['instance_id']}, version is {version}")

    # Save results
    with open(save_path, "w") as f:
        json.dump(data_tasks, fp=f)
    os.chdir(cwd)


def get_versions_from_web(data: dict):
    """
    Logic for looking up versions by searching GitHub at the instance's base
    commit and looking for the version according to repo-specific paths.

    Args:
        data (dict): Dictionary of data for searching GitHub for any task instance
            in a given list.
    """
    data_tasks, save_path = data["data_tasks"], data["save_path"]
    version_not_found = data["not_found_list"]
    for instance in data_tasks:
        version = get_version(instance)
        if version is not None:
            instance["version"] = version
            logger.info(f"For instance {instance['instance_id']}, version is {version}")
        elif version_not_found is not None:
            logger.info(f"[{instance['instance_id']}]: version not found")
            version_not_found.append(instance)
    with open(save_path, "w") as f:
        json.dump(data_tasks, fp=f)


def merge_results(instances_path: str, repo_prefix: str, output_dir: Optional[str] = None) -> int:
    """
    Helper function for merging JSON result files generated from multiple threads.

    Args:
        instances_path (str): Path to original task instances without versions
        repo_prefix (str): Prefix of result files (repo name)
        output_dir (str): Path to save merged results to
    Returns:
        int: Number of instances in merged results
    """
    # Merge values from result JSON files into a single list
    merged = []
    for task_with_version_path in glob.glob(f"{repo_prefix}_versions_*.json"):
        with open(task_with_version_path) as f:
            task_with_version = json.load(f)
            merged.extend(task_with_version)
        os.remove(task_with_version_path)

    # Save merged results to original task instances file's path with `_versions` suffix
    old_path_file = instances_path.split("/")[-1]
    instances_path_new = f"{old_path_file.split('.')[0]}_versions.json"
    if output_dir is not None:
        instances_path_new = os.path.join(output_dir, instances_path_new)
    with open(f"{instances_path_new}", "w") as f:
        json.dump(merged, fp=f)
    logger.info(
        f"Saved merged results to {instances_path_new} ({len(merged)} instances)"
    )
    return len(merged)


def main(args):
    """
    Main function for looking up versions for task instances.
    """
    # Get task instances + split into groups for each thread
    data_tasks = get_instances(args.instances_path)
    data_task_lists = split_instances(data_tasks, args.num_workers)

    repo_prefix = data_tasks[0]["repo"].replace("/", "__")

    logger.info(
        f"Getting versions for {len(data_tasks)} instances for {data_tasks[0]['repo']}"
    )
    logger.info(
        f"Split instances into {len(data_task_lists)} groups with lengths {[len(x) for x in data_task_lists]}"
    )

    assert all([x in args for x in ["testbed"]])

    cwd = os.getcwd()
    os.chdir(args.testbed)
    for x in range(0, args.num_workers):
        # Clone git repo per thread
        testbed_repo_name = f"{repo_prefix}__{x}"
        if not os.path.exists(testbed_repo_name):
            logger.info(
                f"Creating clone of {data_tasks[0]['repo']} at {testbed_repo_name}"
            )
            cmd_clone = f"git clone git@github.com:c-bench/{repo_prefix} {testbed_repo_name}"
            subprocess.run(cmd_clone, shell=True, check=True, stdout=subprocess.DEVNULL)
        else:
            logger.info(
                f"Repo for {data_tasks[0]['repo']} exists: {testbed_repo_name}; skipping..."
            )
    os.chdir(cwd)

    # Create pool tasks
    pool_tasks = []
    for i in range(0, args.num_workers):
        testbed_repo_name = f"{repo_prefix}__{i}"
        pool_tasks.append(
            {
                "data_tasks": data_task_lists[i],
                "path_repo": os.path.join(args.testbed, testbed_repo_name),
                "save_path": os.path.join(cwd, f"{repo_prefix}_versions_{i}.json"),
            }
        )

    # Parallelized call
    pool = Pool(processes=args.num_workers)
    pool.map(get_versions_from_build, pool_tasks)
    pool.close()
    pool.join()

    # Check that correct number of instances were versioned
    assert (
        len(data_tasks)
        == merge_results(args.instances_path, repo_prefix, args.output_dir)
    )

    # Remove testbed repo and conda environments
    if args.cleanup:
        cwd = os.getcwd()
        os.chdir(args.testbed)
        for x in range(0, args.num_workers):
            # Remove git repo
            testbed_repo_name = f"{repo_prefix}__{x}"
            subprocess.run(f"rm -rf {testbed_repo_name}", shell=True, check=True)

        os.chdir(cwd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--instances_path",
        required=True,
        type=str,
        default=None,
        help="Path to task instances",
    )
    parser.add_argument(
        "--num_workers", type=int, default=1, help="Number of threads to use"
    )
    parser.add_argument(
        "--output_dir", type=str, default=None, help="Path to save results"
    )
    parser.add_argument(
        "--testbed", type=str, default=None, help="Path to testbed repo"
    )
    parser.add_argument("--cleanup", action="store_true", help="Remove testbed repo and conda environments")
    args = parser.parse_args()
    main(args)

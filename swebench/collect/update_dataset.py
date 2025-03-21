#!/usr/bin/env python3
"""
Script to update a dataset with additional columns extracted from patches and problem statements.
"""

import argparse
from copy import deepcopy
import os
from typing import Tuple, Optional

import tiktoken

from datasets import load_dataset, arrow_dataset
from datasets.arrow_dataset import Dataset

from unidiff import PatchSet


def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """
    Count the number of tokens in a text using tiktoken.

    Args:
        text: The text to tokenize
        model: The tokenizer model to use

    Returns:
        Number of tokens in the text
    """
    if not text:
        return 0

    encoder = tiktoken.get_encoding(model)
    return len(encoder.encode(text))


def extract_patch_info(patch_text: str) -> Tuple[int, int, int, int]:
    """
    Extract information from a git patch.

    Args:
        patch_text: The git patch text

    Returns:
        Tuple containing (lines_edited, files_edited, files_added, files_removed)
    """
    if not patch_text:
        return 0, 0, 0, 0

    try:
        patch_set = PatchSet(patch_text)

        # Count total lines edited
        lines_edited = 0
        files_added = 0
        files_removed = 0
        files_edited = set()

        for patched_file in patch_set:
            files_edited.add(patched_file.path)
            if patched_file.is_added_file:
                files_added +=1
            elif patched_file.is_removed_file:
                files_removed +=1
            for hunk in patched_file:
                lines_edited += hunk.added + hunk.removed

        return lines_edited, len(files_edited), files_added, files_removed
    except Exception as e:
        print(f"Error parsing patch: {e}")
        return 0, 0, 0, 0


def update_dataset(
    dataset_path: str,
    output_path: Optional[str] = None,
    override: bool = False,
    split="test",
) -> None:
    """
    Update dataset with additional columns:
    - lines_edited: number of lines edited in the patch
    - files_edited: list of files edited in the patch
    - problem_statement_tokens: number of tokens in the problem statement

    Args:
        dataset_path: Path to local dataset file or Hugging Face dataset ID
        output_path: Path to save the updated dataset (defaults to input path)
        override: Whether to override existing columns without confirmation
    """
    # Load dataset
    try:
        if os.path.exists(dataset_path):
            # Local dataset
            print(f"Loading local dataset from {dataset_path}")
            dataset = load_dataset(dataset_path, split=split)
        else:
            # Hugging Face dataset
            print(f"Loading dataset from Hugging Face: {dataset_path}")
            dataset = load_dataset(dataset_path, split=split)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Check if columns already exist
    new_columns = ["lines_edited", "files_edited", "problem_statement_tokens"]
    existing_columns = [col for col in new_columns if col in dataset.column_names]

    if existing_columns and not override:
        print(f"The following columns already exist: {existing_columns}")
        response = input("Do you want to override these columns? (y/n): ")
        if response.lower() != "y":
            print("Operation cancelled.")
            return

    # Extract information from patches and problem statements
    lines_edited_list = []
    files_edited_list = []
    files_created_list = []
    files_removed_list = []
    problem_statement_tokens_list = []

    total_examples = len(dataset)
    print(f"Processing {total_examples} examples...")

    for i, row in enumerate(dataset):
        print(f"Processing example {i + 1}/{total_examples}...", end='\r')
        # Extract patch information
        patch = row.get("patch", "")
        lines, files_touched, files_added, files_removed = extract_patch_info(patch)
        lines_edited_list.append(lines)
        files_edited_list.append(files_touched)
        files_created_list.append( files_added)
        files_removed_list.append( files_removed)

        # Count tokens in problem statement
        problem_statement = row.get("problem_statement", "")
        tokens = count_tokens(problem_statement)
        problem_statement_tokens_list.append(tokens)
    # Add new columns to dataset
    dataset = dataset.add_column("lines_edited", lines_edited_list)
    dataset = dataset.add_column("files_edited", files_edited_list)
    dataset = dataset.add_column("files_added", files_created_list)
    dataset = dataset.add_column("files_removed", files_removed_list)
    dataset = dataset.add_column(
        "problem_statement_tokens", problem_statement_tokens_list
    )

    # Save updated dataset
    if output_path is None:
        output_path = dataset_path

    print(f"Saving updated dataset to {output_path}")

    # Determine format based on extension
    if output_path.endswith(".json"):
        dataset.to_json(output_path)
    elif output_path.endswith(".csv"):
        dataset.to_csv(output_path)
    elif output_path.endswith(".parquet"):
        dataset.to_parquet(output_path)
    else:
        # Default to json
        dataset.to_json(output_path)

    print(f"Dataset updated and saved to {output_path}")
    print(f"Added columns: {new_columns}")
    print("Dataset statistics:")
    print(f"  - Total examples: {len(dataset)}")
    print(
        f"  - Average lines edited: {sum(lines_edited_list) / max(1, len(lines_edited_list)):.2f}"
    )
    print(
        f"  - Average problem statement tokens: {sum(problem_statement_tokens_list) / max(1, len(problem_statement_tokens_list)):.2f}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Update dataset with additional columns extracted from patches and problem statements"
    )
    parser.add_argument(
        "dataset_path", help="Path to local dataset file or Hugging Face dataset ID"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output path for the updated dataset (defaults to input path)",
    )
    parser.add_argument(
        "--override",
        "-f",
        action="store_true",
        help="Override existing columns without confirmation",
    )
    parser.add_argument(
        "--split",
        "-s",
        default="test",
        help="split name",
    )

    args = parser.parse_args()

    update_dataset(args.dataset_path, args.output, args.override, split=args.split)


if __name__ == "__main__":
    main()

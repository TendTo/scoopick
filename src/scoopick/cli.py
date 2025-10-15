"""Command-line interface for scoopick."""

import argparse


class CliArguments(argparse.Namespace):
    """Command line arguments

    Args:
        name: Name to greet.
    """

    name: str = "world"


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        An argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(prog="scoopick", description="scoopick CLI")
    return parser

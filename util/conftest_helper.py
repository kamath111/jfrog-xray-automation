"""
Author: Shwetha Kamath

This module provides helper functions for parsing and managing
 command-line options 
used in the JFrog Artifactory automation framework.

Purpose:
- To define and parse command-line options for configuring test execution.
- To support both 'argparse.ArgumentParser' and 'pytest' parsers
 for flexibility.
"""

from util import logging

log = logging.get_main_logger()


def parse_args(parser, arg_parser=False):
    """
    Read and parse command line options.
    Args:
        parser:  argparser or pytest parser
        arg_parser: set True if argparse.ArgumentParser is used
    """
    if arg_parser:
        parser.addoption = parser.add_argument
        parser.getgroup = parser.add_argument_group

    # Add CLI options
    parser.addoption("--repoName", help="Name of the repository to be used.")
    parser.addoption("--user", help="User name for JFrog authentication.")
    parser.addoption("--password", help="Password for JFrog authentication.")
    parser.addoption("--baseUrl", help="Base URL for JFrog Artifactory.")
    parser.addoption("--authToken", help="Authentication token for JFrog.")
    parser.addoption("--packageType", default="docker", help="Type of package for the repository.")
    parser.addoption("--rclass", default="local", help="Repository class (e.g., local, remote).")
    parser.addoption(
        "--xrayIndex", type=bool, default=True, help="Enable Xray indexing for the repository."
    )
    parser.addoption("--policyName", help="Name of the security policy.")
    parser.addoption("--minSeverity", default="high", help="Minimum severity level for the policy.")
    parser.addoption("--watchName", help="Name of the watch to be created.")
    parser.addoption("--artifactPath", help="Path of the artifact to be scanned.")
    parser.addoption("--customTag", help="Custom tag.")
    parser.addoption("--customImageName", help="Custom image name.")

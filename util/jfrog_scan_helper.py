"""
This module provides helper functions for test suite file: 
test_jfrog_xray_e2e_violation_validation.py

Author: shwetha Kamath

"""

import time

from integration_core import constants
from util import logging

log = logging.get_main_logger()


def wait_for_scan_completion(
    jfrog_client,
    repo_name,
    artifact_path,
    timeout=constants.MAX_TIME_INTERVAL_SCAN,
    interval=constants.SCAN_INTERVAL,
):
    """
    This function repeatedly checks the scan status of an artifact
      in a repository
    using the provided JFrog client.
    It waits for the scan to complete or until the timeout is reached,
    logging the progress and retrying at regular intervals.

    Args:
        jfrog_client (JFrogAPIClient): The JFrog client instance used
          to check scan status.
        repo_name (str): The name of the repository containing the artifact.
        artifact_path (str): The path of the artifact to be scanned.
        timeout (int): The maximum time (in seconds) to wait
          for the scan completion
        interval (int): The interval (in seconds) between scan status checks.

    Returns:
        bool: True if the scan completes successfully within
          the timeout, False otherwise.
    """
    elapsed_time = 0
    while elapsed_time < timeout:
        scan_status = jfrog_client.check_scan_status(repo_name, artifact_path)
        if scan_status == "DONE":
            print("Scan completed successfully.")
            print(f"Final time taken: {elapsed_time}")
            return True
        print(f"Scan status: {scan_status}. Retrying in {interval} seconds...")
        time.sleep(interval)
        elapsed_time += interval
    log.info(f"Timeout of{timeout} reached. Scan did not complete.")
    return False

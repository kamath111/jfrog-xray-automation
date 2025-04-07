"""
Author: Shwetha Kamath

This module provides utility functions for loading and managing 
configuration data 
from YAML files and merging it with command-line interface (CLI) options.

Purpose:
- To load test configuration data from a YAML file.
- To merge configuration values from the YAML file with CLI
 options provided during test execution.
"""

import os

import yaml

from integration_core import exceptions


def load_yaml_config(config_file="config.yaml"):
    """
    Load Test configuration from a YAML file.
    Args:
        config_file (str): Path to the YAML configuration file.
    Returns:
        dict: Configuration data.
    """
    try:
        path = os.getcwd()
        file_path = os.path.join(path, config_file)
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise exceptions.FileNotFoundError(f"Configuration file '{config_file}' not found.")
    except yaml.YAMLError as error:
        raise ValueError(f"Error parsing YAML configuration file '{config_file}': {error}")


def merge_config_with_cli(pytestconfig, config_file="config.yaml"):
    """
    Merge CLI options with YAML configuration file values.
    Args:
        pytestconfig: Pytest configuration object.
        config_file (str): Path to the YAML configuration file.
    Returns:
        dict: Final configuration values.
    """
    # Load defaults from the YAML configuration file
    config = load_yaml_config(config_file)

    # Override with CLI options if provided
    for section, options in config.items():
        for key in options.keys():
            cli_value = pytestconfig.getoption(key)
            if cli_value is not None:
                config[section][key] = cli_value

    return config

"""
This module provides a `DockerClient` class to interact with Docker using
 the Docker CLI/API.

Purpose/features:
- To simplify Docker operations such as logging in to a registry, 
pulling images, tagging images, and pushing images.
- To encapsulate Docker-related functionality 
in a reusable and modular class.

Note:
- Ensure that Docker is installed and running on the host machine.
- The 'docker' Python package must be installed in the environment.

Author: Shwetha Kamath
"""

import docker

from integration_core import exceptions
from util import logging, subprocess_helper

log = logging.get_main_logger()


class DockerClient:
    """
    A helper class to interact with Docker using the Docker CLIs
    """

    def __init__(self, username, password, registry_url):
        """
        Initializes a DockerClient object

        Args:
            username (str): The username for Docker registry authentication.
            password (str): The password for Docker registry authentication.
            registry_url (str): The URL of the Docker registry.
        """
        self.username = username
        self.password = password
        self.registry_url = registry_url
        self._docker_client = docker.from_env()
        self._docker_container = None

    def pull_image(self, image_name):
        """
        Pull a Docker image from the registry.

        Args:
            image_name (str): The name of the Docker image to pull.

        Raises:
            DockerImagePullError: If the image pull operation fails.
        """
        try:
            # Check if the image already exists locally
            # if self._docker_client.images.list(name=image_name):
            #     log.info(f"Image '{image_name}' already exists locally. Skipping pull.")
            #     return

            # Pull the image if it doesn't exist
            command = ["docker", "pull", image_name]
            output, error = subprocess_helper.run_logging_command(command, return_error=True)

            # Log the output and error
            log.info(f"Command Output: {output}")
            if error:
                log.error(f"Command Error: {error}")
        except Exception as error:
            log.error(f"Error while pulling image: {error}")
            raise exceptions.DockerImagePullError(
                f"Failed to pull Docker image '{image_name}': {error}"
            ) from error

    def login_to_registry(self):
        """
        Log in to the Docker registry using subprocess_helper.

        Raises:
            DockerLoginError: If the login operation fails.
        """
        try:
            # Check if already logged in
            # command = ["docker", "info"]
            # output, _ = subprocess_helper.run_logging_command(command, return_error=True)
            # if registry_url in output:
            #     log.info(f"Already logged in to registry '{registry_url}'. Skipping login.")
            #     return

            # Login if not already logged in
            command = [
                "docker",
                "login",
                self.registry_url,
                "-u",
                self.username,
                "-p",
                self.password,
            ]
            output, error = subprocess_helper.run_logging_command(command, return_error=True)

            # Log the output and error
            log.info(f"Command Output: {output}")
            if error:
                log.error(f"Command Error: {error}")
        except Exception as error:
            log.error(f"Error while logging in to registry: {error}")
            raise exceptions.DockerLoginError(
                f"Failed to log in to Docker registry '{self.registry_url}': {error}"
            ) from error

    def tag_image(self, source_image, target_image):
        """
        Tag a Docker image with a new name or tag.

        This method uses the Docker CLI to tag a Docker image
          with a new name or tag.
        It logs the output and errors during the operation and raises
          an exception if the tagging fails.

        Args:
            source_image (str): The name of the source Docker image
            target_image (str): The name of the target Docker image

        Raises:
            Exception: If the tagging operation fails.
        """
        try:
            # Check if the target image tag already exists
            # if self._docker_client.images.list(name=target_image):
            #     log.info(f"Image '{target_image}' already exists. Skipping tagging.")
            #     return

            # Tag the image if the tag doesn't exist
            command = ["docker", "tag", source_image, target_image]

            output, error = subprocess_helper.run_logging_command(command, return_error=True)

            # Log the output and error
            log.info(f"Command Output: {output}")
            if error:
                log.error(f"Command Error: {error}")
        except Exception as error:
            log.error(f"Error while tagging image: {error}")

    def push_image(self, image_name):
        """
        Push a Docker image to the registry.

        This method uses the Docker CLI to push a Docker image to the
          specified registry.
        It logs the output and errors during the operation and raises an exception
          if the push fails.

        Args:
        image_name (str): The name of the Docker image to push.

        Raises:
        DockerPushError: If the image push operation fails.
        """
        try:
            # Check if the image is already available in the registry
            # command = ["docker", "manifest", "inspect", image_name]
            # output, _ = subprocess_helper.run_logging_command(command, return_error=True)
            # if "schemaVersion" in output:
            #     log.info(f"Image '{image_name}' already exists in the registry. Skipping push.")
            #     return

            # Push the image if not already available
            command = ["docker", "push", image_name]
            output, error = subprocess_helper.run_logging_command(command, return_error=True)

            # Log the output and error
            log.info(f"Command Output: {output}")
            if error:
                log.error(f"Command Error: {error}")
        except Exception as error:
            log.error(f"Error while pushing image: {error}")
            raise exceptions.DockerPushError(
                f"Failed to push Docker image '{image_name}': {error}"
            ) from error

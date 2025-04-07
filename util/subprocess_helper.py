"""
Author: Shwetha Kamath
Helper file with utility methods for Subprocess
"""


import subprocess

from util import logging

log = logging.get_main_logger()


def run_logging_command(cmd, return_error=False, print_stdout=False, return_exception=False):
    """Run the command using subprocess and log output to logger.

    This can be used to add post/pre-processing to running a system command

    Args:
        cmd (Union[str, list]): Command to execute.
        Can be a shell type string or a list of command and args.
            e.g. ['ps', '-ef'], ['/bin/bash/', script.sh], './script.sh'
        return_error: Whether to return error message
        print_stdout: Whether to print the output lines
    Returns:
        List of lines in the stdout of the ran command.

    Raises:
        subprocess.CalledProcessError:
        Subprocess command returned a non-zero code.
    """
    if isinstance(cmd, list):
        shell = False
    else:
        shell = True
    output = []
    error = []
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, text=True
        )
        while process.poll() is None:
            stdout_line = process.stdout.readline().rstrip("\n")
            if stdout_line:
                output.append(stdout_line)
        return_code = process.returncode

        if return_code != 0:
            error = process.stderr.read().rstrip("\n")
            log.warning(f"Error is: {error}")
            # If user is not expecting error to be returned. raise it
            if not return_error:
                raise subprocess.CalledProcessError(returncode=return_code, cmd=cmd)
        else:
            if print_stdout:
                log.info(f"Successfully ran command: {cmd}")

        process.stdout.close()
        process.stderr.close()
        if print_stdout:
            log.info(f"Command to run - {cmd}  output - {output} and error if any -  {error}")
        return output, error
    except Exception as e:
        log.error(f"Error running the subprocess command - {e}")
        if return_exception:
            return False
        raise e from None

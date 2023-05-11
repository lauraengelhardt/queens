"""Module supplies functions to conduct operation on remote resource."""
import atexit
import logging
import pickle
import uuid
from functools import partial
from pathlib import Path

import cloudpickle
from fabric import Connection

from pqueens.utils.run_subprocess import run_subprocess

_logger = logging.getLogger(__name__)


def make_directory_on_remote(remote_connect, directory):
    """Make (empty) directory on remote resource.

    Args:
        remote_connect: TODO_doc
        directory: TODO_doc
    """
    command_list = [
        'ssh',
        remote_connect,
        '"mkdir -p',
        directory,
        '"',
    ]
    command_string = ' '.join(command_list)
    run_subprocess(
        command_string, additional_error_message="Directory could not be made on remote machine!"
    )


def copy_directory_to_remote(remote_connect, local_dir, remote_dir):
    """Copy (local) directory to remote resource.

    Args:
        remote_connect: TODO_doc
        local_dir: TODO_doc
        remote_dir: TODO_doc
    """
    command_list = [
        "scp -r ",
        local_dir,
        " ",
        remote_connect,
        ":",
        remote_dir,
    ]
    command_string = ' '.join(command_list)
    run_subprocess(
        command_string, additional_error_message="Directory could not be copied to remote machine!"
    )


class RemoteConnection(Connection):
    """This is class wrapper around the Connection class of fabric.

    Attributes:
        func_file_name (str): Filename of temporary pickle file for the deployed function
        output_file_name (str): Filename of temporary pickle file for the output
        python_cmd (str): Command that is executed on remote machine to run python function
    """

    def __init__(self, host, remote_python, user=None):
        """Initialize RemoteConnection object.

        Args:
            host (str): address of remote host
            remote_python (str): Path to remote python
            user (str): User name on remote machine
        """
        super().__init__(host, user=user)
        self.func_file_name = f"temp_func_{str(uuid.uuid4())}.pickle"
        self.output_file_name = f"output_{str(uuid.uuid4())}.pickle"
        self.python_cmd = (
            f"{remote_python} -c 'import pickle; from pathlib import Path;"
            f"file = open(\"{self.func_file_name}\", \"rb\");"
            f"func = pickle.load(file); file.close();"
            f"Path(\"{self.func_file_name}\").unlink(); result = func();"
            f"file = open(\"{self.output_file_name}\", \"wb\");"
            f"pickle.dump(result, file); file.close();'"
        )

    def run_function(self, func, *func_args, wait=True, **func_kwargs):
        """Run a python function remotely using an ssh connection.

        Args:
            func (Function): function that is executed
            wait (bool): Flag to decide whether to wait for result of function
        Returns:
            return_value (obj): Return value of function
        """
        _logger.info("Running %s on %s", func.__name__, self.host)
        partial_func = partial(func, *func_args, **func_kwargs)  # insert function arguments
        with open(self.func_file_name, "wb") as file:
            cloudpickle.dump(partial_func, file)  # pickle function by value

        self.put(self.func_file_name)  # upload local function file
        Path(self.func_file_name).unlink()  # delete local function file

        if not wait:
            _, stdout, stderr = self.client.exec_command(self.python_cmd, get_pty=True)
            return stdout, stderr

        self.run(self.python_cmd, in_stream=False)  # run function remote
        self.get(self.output_file_name)  # download result

        self.run(f'rm {self.output_file_name}', in_stream=False)  # delete remote files

        with open(self.output_file_name, 'rb') as file:  # read return value from output file
            return_value = pickle.load(file)

        Path(self.output_file_name).unlink()  # delete local output file

        return return_value

    def open_port_forwarding(self, local_port, remote_port):
        """Open port forwarding.

        Args:
            local_port (int): Local port
            remote_port (int): Remote port
        """
        cmd = f"ssh -f -N -L {local_port}:{self.host}:{remote_port} {self.user}@{self.host}"
        run_subprocess(cmd, subprocess_type='submit')
        _logger.debug("Port-forwarding opened successfully.")

        kill_cmd = f'pkill -f "{cmd}"'
        atexit.register(run_subprocess, kill_cmd, subprocess_type='submit')

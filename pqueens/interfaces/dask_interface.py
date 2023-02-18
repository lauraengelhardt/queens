"""Job interface class."""
import logging
import time

import numpy as np
from dask.distributed import Client, LocalCluster, as_completed

import pqueens.database.database as DB_module
from pqueens.database import from_config_create_database
from pqueens.interfaces.interface import Interface
from pqueens.resources.resource import parse_resources_from_configuration
from pqueens.schedulers import from_config_create_scheduler
from pqueens.utils.config_directories import experiment_directory

_logger = logging.getLogger(__name__)


class DaskInterface(Interface):
    """Class for mapping input variables to responses.

    The *JobInterface* class maps input variables to outputs, i.e. responses
    by creating a job which is then submitted to a job manager on some
    local or remote resource, which in turn then actually runs the
    simulation software.

    Attributes:
        name (string): Name of interface.
        resources (dict): Dictionary with resources.
        experiment_name (string): Name of experiment.
        db (mongodb): MongoDB to store results and job info.
        polling_time (int): How frequently do we check if jobs are done?
        output_dir (path): Directory to write output to.
        batch_number (int): Number of the current simulation batch.
        num_pending (int): Number of Jobs that are currently pending.
        remote (bool): *True* for remote computation.
        remote_connect (str): Connection to computing resource.
        scheduler_type (str): Scheduler type.
        direct_scheduling (bool): *True* if direct scheduling.
        time_for_data_copy (float): Time (s) to wait such that the copying process of
                                    simulation input file can finish, and we
                                    do not overload the network.
        driver_name (str): Name of the associated driver for the current interface.
        _internal_batch_state (int): Helper attribute to compare *batch_number* with the internal
        experiment_dir (path):                       directory to write output to
        time_for_data_copy (float): Time (s) to wait such that copying process of simulation
                                    input file can finish, and we do not overload the network
        job_num (int):              Number of the current job
        _internal_batch_state (int): Helper attribute to compare batch_number with the internal
    """

    def __init__(
        self,
        interface_name,
        resources,
        experiment_name,
        db,
        polling_time,
        experiment_dir,
        remote,
        remote_connect,
        scheduler_type,
        direct_scheduling,
        time_for_data_copy,
        driver_name,
        scheduler,
        dask_scheduler_port,
    ):
        """Create JobInterface.

        Args:
            interface_name (string):    name of interface
            resources (dict):           dictionary with resources
            experiment_name (string):   name of experiment
            db (mongodb):               mongodb to store results and job info
            polling_time (int):         how frequently do we check if jobs are done
            experiment_dir (path):          directory to write output to
            remote (bool):              true of remote computation
            remote_connect (str):       connection to computing resource
            scheduler_type (str):       scheduler type
            direct_scheduling (bool):   true if direct scheduling
            time_for_data_copy (float): Time (s) to wait such that copying process of simulation
                                        input file can finish, and we do not overload the network
            driver_name (str):          Name of the associated driver for the current interface
        """
        super().__init__(interface_name)
        self.name = interface_name
        self.resources = resources
        self.experiment_name = experiment_name
        self.db = db
        self.polling_time = polling_time
        self.experiment_dir = experiment_dir
        self.batch_number = 0
        self.num_pending = None
        self.remote = remote
        self.remote_connect = remote_connect
        self.scheduler_type = scheduler_type
        self.direct_scheduling = direct_scheduling
        self.time_for_data_copy = time_for_data_copy
        self.driver_name = driver_name
        self._internal_batch_state = 0
        self.job_num = 0

        # self.cluster = LocalCluster(n_workers=1, threads_per_worker=1)
        self.client = Client(address=f"localhost:{dask_scheduler_port}")

        _logger.info(self.client)
        _logger.info(self.client.dashboard_link)

        self.scheduler = scheduler

    @classmethod
    def from_config_create_interface(cls, interface_name, config):
        """Create JobInterface from config dictionary.

        Args:
            interface_name (str):   Name of interface.
            config (dict):          Dictionary containing problem description.

        Returns:
            interface: Instance of JobInterface
        """
        # get experiment name and polling time
        experiment_name = config['global_settings']['experiment_name']
        dask_scheduler_port = config['global_settings']['dask_scheduler_port']
        polling_time = config.get('polling-time', 1.0)

        interface_options = config[interface_name]
        driver_name = interface_options.get('driver_name', None)
        if driver_name is None:
            raise ValueError("No driver_name specified for the JobInterface.")

        # get resources from config
        resources = parse_resources_from_configuration(config, driver_name)

        # get various scheduler options
        # TODO: This is not nice
        first = list(config['resources'])[0]
        scheduler_name = config['resources'][first]['scheduler_name']
        scheduler_options = config[scheduler_name]
        scheduler_type = scheduler_options['type']

        # get flag for remote scheduling
        if scheduler_options.get('remote'):
            remote = True
            remote_connect = scheduler_options['remote']['connect']
        else:
            remote = False
            remote_connect = None

        experiment_dir = experiment_directory(
            experiment_name=experiment_name, remote_connect=remote_connect
        )

        # get flag for Singularity
        singularity = scheduler_options.get('singularity', False)
        if not isinstance(singularity, bool):
            raise TypeError("Singularity option has to be a boolean (true or false).")

        # set flag for direct scheduling
        direct_scheduling = False
        if not singularity:
            if (scheduler_type == 'cluster') or (scheduler_type == 'standard' and remote):
                direct_scheduling = True

        db = None

        # get waiting time for copying data
        time_for_data_copy = interface_options.get('time_for_data_copy')

        resource_name = list(config["resources"].keys())[0]
        # get resource options extract resource info from config
        resource_options = config["resources"][resource_name]
        scheduler_name = resource_options['scheduler_name']

        # create scheduler from config
        scheduler = from_config_create_scheduler(
            scheduler_name=scheduler_name,
            config=config,
            driver_name=driver_name,
        )
        # Create/update singularity image in case of cluster job
        scheduler.pre_run()
        # instantiate object
        return cls(
            interface_name,
            resources,
            experiment_name,
            db,
            polling_time,
            experiment_dir,
            remote,
            remote_connect,
            scheduler_type,
            direct_scheduling,
            time_for_data_copy,
            driver_name,
            scheduler,
            dask_scheduler_port,
        )

    def evaluate(self, samples, gradient_bool=False):
        """Orchestrate call to external simulation software.

        Second variant which takes the input samples as argument.

        Args:
            samples (np.ndarray): Realization/samples of QUEENS simulation input variables
            gradient_bool (bool): Flag to determine whether the gradient of the function at
                                  the evaluation point is expected (*True*) or not (*False*)

        Returns:
            output (dict): Output data
        """
        self.batch_number += 1

        # Main run
        jobs = self._manage_jobs(samples)

        # get sample and response data
        output = self.get_output_data(num_samples=samples.shape[0], gradient_bool=gradient_bool, jobs=jobs)
        return output

    def create_new_job(self, variables, resource_name, new_id=None):
        """Create new job and save it to database and return it.

        Args:
            variables (Variables):     Variables to run model at
            resource_name (string):     Name of resource
            new_id (int):                  ID for job

        Returns:
            job (dict): New job
        """
        job_id = int(new_id)

        job = {
            'id': job_id,
            'params': variables,
            'experiment_dir': str(self.experiment_dir),
            'experiment_name': self.experiment_name,
            'resource': resource_name,
            'status': "",  # TODO: before: 'new'
            'submit_time': time.time(),
            'start_time': 0.0,
            'end_time': 0.0,
            'driver_name': self.driver_name,
        }

        return job

    def get_output_data(self, num_samples, gradient_bool, jobs):
        """Extract output data from database and return it.

        Args:
            num_samples (int): Number of evaluated samples
            gradient_bool (bool): Flag to determine whether the gradient
                                  of the model output w.r.t. the input
                                  is expected (*True* if yes)

        Returns:
            dict: Output dictionary; i
                +------------+------------------------------------------------+
                |**key:**    |**value:**                                      |
                +------------+------------------------------------------------+
                |'mean'      | ndarray shape(batch_size, shape_of_response)   |
                +------------+------------------------------------------------+
                | 'var'      | ndarray (optional)                             |
                +------------+------------------------------------------------+
        """
        output = {}
        mean_values = []
        gradient_values = []
        # Sort job IDs in ascending order to match ordering of samples
        jobids = [job['id'] for job in jobs]
        jobids.sort()

        for current_job_id in jobids:
            current_job = next(job for job in jobs if job['id'] == current_job_id)
            mean_value = np.squeeze(current_job['result'])
            gradient_value = np.squeeze(current_job.get('gradient', None))

            if not mean_value.shape:
                mean_value = np.expand_dims(mean_value, axis=0)
                gradient_value = np.expand_dims(gradient_value, axis=0)

            mean_values.append(mean_value)
            gradient_values.append(gradient_value)

        output['mean'] = np.array(mean_values)[-num_samples:]
        if gradient_bool:
            output['gradient'] = np.array(gradient_values)[-num_samples:]

        return output

    # ------------ private helper methods -------------- #

    def _manage_jobs(self, samples):
        """Manage regular submission of jobs.

        Args:
            samples (DataFrame): realization/samples of QUEENS simulation input variables

        Returns:
            jobid_for_data_processor(ndarray): jobids for data-processing
        """
        num_jobs = 0
        if not num_jobs or self.batch_number == 1:
            job_ids_generator = range(1, samples.shape[0] + 1, 1)
        else:
            job_ids_generator = range(num_jobs + 1, num_jobs + samples.shape[0] + 1, 1)

        jobs = self._manage_job_submission(samples, job_ids_generator)

        return jobs

    def _manage_job_submission(self, samples, jobid_range):
        """Iterate over samples and manage submission of jobs.

        Args:
            samples (DataFrame):     realization/samples of QUEENS simulation input variables
            jobid_range (range):     range of job IDs which are submitted
        """
        futures = []
        for jobid in jobid_range:
            current_job = []
            if len(current_job) == 1:
                current_job = current_job[0]
            elif not current_job:
                if self._internal_batch_state != self.batch_number:
                    self._internal_batch_state = self.batch_number
                    self.job_num = 0

                self.job_num += 1
                sample_dict = self.parameters.sample_as_dict(samples[self.job_num - 1])
                resource_name = "DASK"
                current_job = self.create_new_job(sample_dict, resource_name, jobid)
            else:
                raise ValueError(f"Found more than one job with jobid {jobid} in db.")

            current_job['status'] = 'pending'

            futures.append(
                self.client.submit(
                    self.scheduler.submit,
                    jobid,
                    self.batch_number,
                    current_job,
                    key=f"job-{jobid}-batch-{self.batch_number}",
                )
            )

        completed_futures = as_completed(futures)

        jobs = []
        for completed_future in completed_futures:
            jobs.append(completed_future.result())

        return jobs

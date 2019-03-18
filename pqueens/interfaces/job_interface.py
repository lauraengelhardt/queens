import sys
import time
import numpy as np

from pqueens.interfaces.interface import Interface
from pqueens.resources.resource import parse_resources_from_configuration
from pqueens.resources.resource import print_resources_status
from pqueens.database.mongodb import MongoDB

class JobInterface(Interface):
    """
        Class for mapping input variables to responses

        The JobInterface class maps input variables to outputs, i.e. responses
        by creating a job which is then submitted to a job manager on some
        local or remote resource, which in turn then actually runs the
        simulation software.

    Attributes:
        name (string):              name of interface
        resources (dict):           dictionary with resources
        experiment_name (string):   name of experiment
        db_adress (string):         adress of database to use
        db (mongodb):               mongodb to store results and job info
        polling_time (int):         how frequently do we check if jobs are done
        output_dir (string):        directory to write output to
        driver_type (string):       what kind of simulation driver are we using
        driver_params (dict):       parameters for simulatio driver
        parameters (dict):          dictionary with parameters

    """

    def __init__(self, interface_name, resources, experiment_name, db_address,
                 db, polling_time, output_dir, driver_type, driver_params, parameters):
        """ Create JobInterface

        Args:
            interface_name (string):    name of interface
            resources (dict):           dictionary with resources
            experiment_name (string):   name of experiment
            db_adress (string):         adress of database to use
            db (mongodb):               mongodb to store results and job info
            polling_time (int):         how frequently do we check if jobs are done
            output_dir (string):        directory to write output to
            driver_type (string):       what kind of simulation driver are we using
            driver_params (dict):       parameters for simulatio driver
            variables (dict):           dictionary with parameters
        """
        self.name = interface_name
        self.resources = resources
        self.experiment_name = experiment_name
        self.db_address = db_address
        self.db = db
        self.polling_time = polling_time
        self.output_dir = output_dir
        self.driver_type = driver_type
        self.driver_params = driver_params
        self.parameters = parameters
        self.batch_number = 1

    @classmethod
    def from_config_create_interface(cls, interface_name, config):
        """ Create JobInterface from config dictionary

        Args:
            interface_name (str):   name of interface
            config (dict):          dictionary containing problem description

        Returns:
            interface:              instance of JobInterface
        """
        # get resources from config
        resources = parse_resources_from_configuration(config)

         # connect to the database
        db_address = config['database']['address']
        if 'drop_existing' in config['database']:
            drop_existing = config['database']['drop_existing']
        else:
            drop_existing = False
        experiment_name = config['global_settings']['experiment_name']

        #sys.stderr.write('Using database at %s.\n' % db_address)

        db = MongoDB(database_address=db_address, drop_existing_db=drop_existing)

        polling_time = config.get('polling-time', 30)

        output_dir = config['driver']['driver_params']["experiment_dir"]

        driver_type = config['driver']['driver_type']

        driver_params = config['driver']['driver_params']

        parameters = config['parameters']

        # instanciate object
        return cls(interface_name, resources, experiment_name, db_address, db,
                   polling_time, output_dir, driver_type, driver_params, parameters)


    def map(self, samples):
        """
        Mapping function which orchestrates call to external simulation software

        Second vairiant which takes the input samples as argument

        Args:
            samples (list):         list of variables objects

        Returns:
            np.array,np.array       two arrays containing the inputs from the
                                    suggester, as well as the corresponding outputs

        """
        self.batch_number += 1
        jobs = self.load_jobs()
        for variables in samples:
            processed_suggestion = False
            while not processed_suggestion:
                # loop over all available resources
                for resource_name, resource in self.resources.items():
                    if resource.accepting_jobs(jobs):

                        new_job = self.create_new_job(variables, resource_name)

                        # Submit the job to the appropriate resource
                        process_id = self.attempt_dispatch(resource, new_job)
                        #process_id = resource.attempt_dispatch(self.experiment_name,
                        #                                       self.batch_number,
                        #                                       new_job,
                        #                                       self.db_address,
                        #                                       self.output_dir)

                        # Set the status of the job appropriately (successfully submitted or not)
                        if process_id is None:
                            new_job['status'] = 'broken'
                            self.save_job(new_job)
                        else:
                            new_job['status'] = 'pending'
                            new_job['proc_id'] = process_id
                            self.save_job(new_job)

                        processed_suggestion = True
                        jobs = self.load_jobs()
                        print_resources_status(self.resources, jobs)

                    else:
                        time.sleep(self.polling_time)
                        jobs = self.load_jobs()


        while not self.all_jobs_finished():
            time.sleep(self.polling_time)

        # get sample and response data
        return self.get_output_data()

    def attempt_dispatch(self, resource, new_job):
        """ Attempt to dispatch job multiple times

        Submitting jobs to the queue sometimes fails, hence we try multiple times
        before giving up. We also wait two seconds between submit commands

        Args:
            resource (resource object): Resource to submit job to
            new_job (dict):             Dictionary with job

        Returns:
            int: Process ID of submitted job if successfull, None otherwise
        """
        process_id = None
        num_tries = 0

        while process_id is None and num_tries < 10:
            time.sleep(2)

            # Submit the job to the appropriate resource
            process_id = resource.attempt_dispatch(self.experiment_name,
                                                   self.batch_number,
                                                   new_job,
                                                   self.db_address,
                                                   self.output_dir)
            num_tries += 1

        return process_id

    def load_jobs(self):
        """ Load jobs from the jobs database

        Returns:
            list : list with all jobs or an empty list
        """
        jobs = self.db.load(self.experiment_name, str(self.batch_number), 'jobs')

        if jobs is None:
            jobs = []
        if isinstance(jobs, dict):
            jobs = [jobs]
        return jobs

    def save_job(self, job):
        """ Save a job to the job database

        Args:
            job (dict): dictionary with job details
        """
        self.db.save(job, self.experiment_name, 'jobs', str(self.batch_number), {'id' : job['id']})

    def create_new_job(self, variables, resource_name):
        """ Create new job and save it to database and return it

        Args:
            variables (Variables):     variables to run model at
            resource_name (string):     name of resource

        Returns:
            job: new job
        """

        print("Created new job")
        jobs = self.load_jobs()
        job_id = len(jobs) + 1

        job = {
            'id'           : job_id,
            'params'       : variables.get_active_variables(),
            'expt_dir'     : self.output_dir,
            'expt_name'    : self.experiment_name,
            'resource'     : resource_name,
            'driver_type'  : self.driver_type,
            'driver_params': self.driver_params,
            'status'       : 'new',
            'submit time'  : time.time(),
            'start time'   : None,
            'end time'     : None
        }

        self.save_job(job)

        return job

    def tired(self, resource):
        """ Quick check wether a resource is fully occupied

        Args:
            (resource): resource object
        Returns:
            bool: whether or not resource is tired
        """
        jobs = self.load_jobs()
        if resource.accepting_jobs(jobs):
            return False
        return True

    def all_jobs_finished(self):
        """ Determine whether all jobs are finished

        Finished can either mean, complete or failed

        Returns:
            bool: returns true if all jobs in the database have reached completion
                  or failed
        """
        jobs = self.load_jobs()
        print_resources_status(self.resources, jobs)
        for job in jobs:
            if job['status'] != 'complete' and job['status'] != 'failed' and job['status'] != 'broken':
                return False
        return True

    def get_output_data(self):
        """ Extract output data from database and return it

        Args:
            num_variables (int): number of input variables

        Returns:
            np.array: output data
        """
        output = {}
        mean_values = []
        if not self.all_jobs_finished():
            print("Not all jobs are finished yet, try again later")
        else:
            jobs = self.load_jobs()
            for job in jobs:
                mean_values.append(job['result'])
        output['mean'] = np.reshape(mean_values, (-1, mean_values[1].shape[0]))

        return  output

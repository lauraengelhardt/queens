import os

from pqueens.database.mongodb import MongoDB
from pqueens.drivers.driver import Driver
from pqueens.utils.run_subprocess import run_subprocess
from pqueens.utils.script_generator import generate_submission_script


class BaciDriverNative(Driver):
    """
    Driver to run BACI natively on workstation.

    Returns:
        BaciDriverNative_obj (obj): Instance of BaciDriverNative class

    """

    def __init__(self, base_settings):
        super(BaciDriverNative, self).__init__(base_settings)

    @classmethod
    def from_config_create_driver(cls, config, base_settings, workdir=None):
        """
        Create Driver from input file description

        Args:
            config (dict): Dictionary with input configuration
            base_settings (dict): Dictionary with base settings of the parent class
                                  (depreciated: will be removed soon)
            workdir (str): Path to working directory

        Returns:
            BaciDriverNative_obj (obj): Instance of the BaciDriverNative class

        """
        database_address = 'localhost:27017'
        database_config = dict(
            global_settings=config["global_settings"],
            database=dict(address=database_address, drop_existing=False),
        )
        db = MongoDB.from_config_create_database(database_config)
        base_settings['database'] = db
        return cls(base_settings)

    # ----------------- CHILD METHODS THAT NEED TO BE IMPLEMENTED -----------------
    def setup_dirs_and_files(self):
        """
        Setup directory structure

        Returns:
            None

        """
        # set destination directory and output prefix
        dest_dir = os.path.join(str(self.experiment_dir), str(self.job_id))
        self.output_prefix = str(self.experiment_name) + '_' + str(self.job_id)

        # set path to input file
        input_file_str = self.output_prefix + '.dat'
        self.input_file = os.path.join(dest_dir, input_file_str)

        # set path to output directory (either on local or remote machine)
        self.output_directory = os.path.join(dest_dir, 'output')

        # make (actual) output directory on remote machine as well as "mirror"
        # output directory on local machine for remote scheduling
        if (
            self.scheduler_type == 'remote'
            or self.scheduler_type == 'remote_nohup'
            or self.scheduler_type == 'remote_pbs'
            or self.scheduler_type == 'remote_slurm'
        ):
            # generate command for making output directory on remote machine
            command_list = [
                'ssh',
                self.connect_to_resource,
                '"mkdir -p',
                self.output_directory,
                '"',
            ]
            command_string = ' '.join(command_list)
            _, _, _, stderr = run_subprocess(command_string)

            # detection of failed command
            if stderr:
                raise RuntimeError(
                    "\nOutput directory could not be made on remote machine!"
                    f"\nStderr from remote:\n{stderr}"
                )

            # set path to output directory on local machine
            local_job_dir = os.path.join(str(self.global_output_dir), str(self.job_id))
            self.local_job_output_dir = os.path.join(local_job_dir, 'output')

            # make "mirror" output directory on local machine, if not already existent
            if not os.path.isdir(self.local_job_output_dir):
                os.makedirs(self.local_job_output_dir)
        else:
            # make output directory on local machine, if not already existent
            if not os.path.isdir(self.output_directory):
                os.makedirs(self.output_directory)

        # generate path to output files in general, control file and log file
        self.output_file = os.path.join(self.output_directory, self.output_prefix)
        control_file_str = self.output_prefix + '.control'
        self.control_file = os.path.join(self.output_directory, control_file_str)
        log_file_str = self.output_prefix + '.out'
        self.log_file = os.path.join(self.output_directory, log_file_str)
        err_file_str = self.output_prefix + '.err'
        self.err_file = os.path.join(self.output_directory, err_file_str)

    def run_job(self):
        """
        Run BACI natively either directly or via jobscript.

        Returns:
            None

        """
        # decide whether jobscript-based run or direct run
        if (
            self.scheduler_type == 'local_pbs'
            or self.scheduler_type == 'local_slurm'
            or self.scheduler_type == 'remote_pbs'
            or self.scheduler_type == 'remote_slurm'
        ):
            # set options for jobscript
            script_options = {}
            script_options['job_name'] = '{}_{}_{}'.format(
                self.experiment_name, 'queens', self.job_id
            )
            script_options['ntasks'] = self.num_procs
            script_options['DESTDIR'] = self.output_directory
            script_options['EXE'] = self.executable
            script_options['INPUT'] = self.input_file
            script_options['OUTPUTPREFIX'] = self.output_prefix
            script_options['CLUSTERSCRIPT'] = self.cluster_script
            if (self.postprocessor is not None) and (self.post_options is None):
                script_options['POSTPROCESSFLAG'] = 'true'
                script_options['POSTEXE'] = self.postprocessor
                script_options['nposttasks'] = self.num_procs_post
            else:
                script_options['POSTPROCESSFLAG'] = 'false'
                script_options['POSTEXE'] = ''
                script_options['nposttasks'] = ''
            # flag only required for Singularity-based run
            script_options['POSTPOSTPROCESSFLAG'] = 'false'

            # determine relative path to script template and start command for scheduler
            if self.scheduler_type == 'local_pbs' or self.scheduler_type == 'remote_pbs':
                rel_path = '../utils/jobscript_pbs.sh'
                scheduler_start = 'qsub'
            else:
                rel_path = '../utils/jobscript_slurm.sh'
                scheduler_start = 'sbatch'

            # set paths for script template and final script location
            this_dir = os.path.dirname(__file__)
            submission_script_template = os.path.join(this_dir, rel_path)
            jobfilename = 'jobfile.sh'
            if self.scheduler_type == 'local_pbs' or self.scheduler_type == 'local_slurm':
                submission_script_path = os.path.join(self.experiment_dir, jobfilename)
            else:
                submission_script_path = os.path.join(self.global_output_dir, jobfilename)

            # generate job script for submission
            generate_submission_script(
                script_options, submission_script_path, submission_script_template
            )

            if self.scheduler_type == 'local_pbs' or self.scheduler_type == 'local_slurm':
                # change directory
                os.chdir(self.experiment_dir)

                # assemble command string for jobscript-based run
                command_list = [scheduler_start, submission_script_path]
            else:
                # submit the job with jobfile.sh on remote machine
                command_list = [
                    "scp ",
                    submission_script_path,
                    " ",
                    self.connect_to_resource,
                    ":",
                    self.experiment_dir,
                ]
                command_string = ''.join(command_list)
                _, _, _, stderr = run_subprocess(command_string)

                # detection of failed command
                if stderr:
                    raise RuntimeError(
                        "\nJobscript could not be copied to remote machine!" f"\nStderr:\n{stderr}"
                    )

                # remove local copy of submission script and change path
                # to submission script to the one on remote machine
                os.remove(submission_script_path)
                submission_script_path = os.path.join(self.experiment_dir, jobfilename)

                # submit the job with jobfile.sh on remote machine
                command_list = [
                    'ssh',
                    self.connect_to_resource,
                    '"cd',
                    self.experiment_dir,
                    ';',
                    scheduler_start,
                    submission_script_path,
                    '"',
                ]

            # set command string
            command_string = ' '.join(command_list)

            # submit and run job
            returncode, self.pid, stdout, stderr = run_subprocess(command_string)

            # save path to control file and number of processes to database
            self.job['control_file_path'] = self.control_file
            self.job['num_procs'] = self.num_procs
            self.database.save(
                self.job,
                self.experiment_name,
                'jobs',
                str(self.batch),
                {
                    'id': self.job_id,
                    'expt_dir': self.experiment_dir,
                    'expt_name': self.experiment_name,
                },
            )
        else:
            # assemble command string for BACI run
            baci_run_cmd = self.assemble_baci_run_cmd()

            if self.scheduler_type == 'local_nohup' or self.scheduler_type == 'remote_nohup':
                # assemble command string for nohup BACI run
                nohup_baci_run_cmd = self.assemble_nohup_baci_run_cmd(baci_run_cmd)

                if self.scheduler_type == 'remote_nohup':
                    final_run_cmd = self.assemble_remote_run_cmd(nohup_baci_run_cmd)
                else:
                    final_run_cmd = nohup_baci_run_cmd

                # run BACI via subprocess
                returncode, self.pid, _, _ = run_subprocess(
                    final_run_cmd, subprocess_type='submit',
                )

                # save path to log file and number of processes to database
                self.job['log_file_path'] = self.log_file
                self.job['num_procs'] = self.num_procs
                self.database.save(
                    self.job,
                    self.experiment_name,
                    'jobs',
                    str(self.batch),
                    {
                        'id': self.job_id,
                        'expt_dir': self.experiment_dir,
                        'expt_name': self.experiment_name,
                    },
                )
            else:
                if self.scheduler_type == 'remote':
                    final_run_cmd = self.assemble_remote_run_cmd(baci_run_cmd)
                else:
                    final_run_cmd = baci_run_cmd

                # run BACI via subprocess
                returncode, self.pid, _, _ = run_subprocess(
                    final_run_cmd,
                    subprocess_type='simulation',
                    terminate_expr='PROC.*ERROR',
                    loggername=__name__ + f'_{self.job_id}',
                    output_file=self.output_file,
                )

        # detection of failed jobs
        if returncode:
            self.result = None
            self.job['status'] = 'failed'

    def assemble_baci_run_cmd(self):
        """  Assemble command for BACI run

            Returns:
                BACI run command

        """
        # set MPI command
        mpi_cmd = 'mpirun -np'

        command_list = [
            mpi_cmd,
            str(self.num_procs),
            self.executable,
            self.input_file,
            self.output_file,
        ]

        return ' '.join(filter(None, command_list))

    def assemble_nohup_baci_run_cmd(self, baci_run_cmd):
        """  Assemble command for nohup run of BACI

            Returns:
                nohup BACI run command

        """
        command_list = [
            "nohup",
            baci_run_cmd,
            ">",
            self.log_file,
            "2>",
            self.err_file,
            "< /dev/null &",
        ]

        return ' '.join(filter(None, command_list))

    def assemble_remote_run_cmd(self, run_cmd):
        """  Assemble command for remote (nohup) run of BACI

            Returns:
                remote (nohup) BACI run command

        """
        command_list = [
            'ssh',
            self.connect_to_resource,
            '"cd',
            self.experiment_dir,
            ';',
            run_cmd,
            '"',
        ]

        return ' '.join(filter(None, command_list))

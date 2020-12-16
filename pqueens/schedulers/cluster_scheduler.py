import sys
import os
from .scheduler import Scheduler
from pqueens.utils.manage_singularity import SingularityManager
from pqueens.utils.run_subprocess import run_subprocess
from pqueens.utils.script_generator import generate_submission_script


class ClusterScheduler(Scheduler):
    """
    Cluster scheduler (either based on Slurm or Torque/PBS) for QUEENS.
    """

    def __init__(self, base_settings):
        super(ClusterScheduler, self).__init__(base_settings)

    @classmethod
    def create_scheduler_class(cls, base_settings):
        """
        Create cluster scheduler (Slurm or Torque/PBS) class for QUEENS.

        Args:
            base_settings (dict): dictionary containing settings from base class for
                                  further use and completion in this child class 

        Returns:
            scheduler (obj):      instance of scheduler class

        """
        # get scheduler options from base settings
        scheduler_options = base_settings['options']

        # initalize sub-dictionary for cluster options within base settings
        base_settings['cluster_options'] = {}

        # get general cluster options
        base_settings['cluster_options']['job_name'] = None  # job name assembled later
        base_settings['cluster_options']['walltime'] = scheduler_options['cluster_walltime']
        base_settings['cluster_options']['CLUSTERSCRIPT'] = scheduler_options['cluster_script']

        # set output option (currently not enforced)
        if scheduler_options.get('cluster_output', True):
            base_settings['cluster_options']['output'] = ''
        else:
            base_settings['cluster_options']['output'] = '--output=/dev/null --error=/dev/null'

        # set cluster options required for PBS or SLURM
        if scheduler_options['scheduler_type'] == 'pbs':
            # set PBS start command
            base_settings['cluster_options']['start_cmd'] = 'qsub'

            # set relative path to PBS jobscript template
            rel_path = '../utils/jobscript_pbs.sh'
        else:
            # set SLURM start command
            base_settings['cluster_options']['start_cmd'] = 'sbatch'

            # set relative path to SLURM jobscript template
            rel_path = '../utils/jobscript_slurm.sh'

        # set absolute path to jobscript template
        script_dir = os.path.dirname(__file__)  # absolute path to directory of this file
        abs_path = os.path.join(script_dir, rel_path)
        base_settings['cluster_options']['jobscript_template'] = abs_path

        # set number of processors for processing and post-processing (default: 1)
        if scheduler_options.get('num_procs', False):
            base_settings['cluster_options']['ntasks'] = scheduler_options['num_procs']
        else:
            base_settings['cluster_options']['ntasks'] = '1'
        if scheduler_options.get('num_procs_post', False):
            base_settings['cluster_options']['nposttasks'] = scheduler_options['num_procs_post']
        else:
            base_settings['cluster_options']['nposttasks'] = '1'

        # set cluster options required for Singularity
        if scheduler_options['singularity']:
            # set path to Singularity container in general and
            # also already as executable for jobscript
            singularity_path = scheduler_options['singularity_cluster_path']
            base_settings['cluster_options']['singularity_path'] = singularity_path
            base_settings['cluster_options']['EXE'] = os.path.join(singularity_path, 'driver.simg')

            # set cluster bind for Singularity
            base_settings['cluster_options']['singularity_bind'] = scheduler_options[
                'singularity_cluster_bind'
            ]
            base_settings['cluster_options']['singularity_remote_ip'] = scheduler_options[
                'singularity_remote_ip'
            ]

            # set further fixed options when using Singularity
            base_settings['cluster_options']['OUTPUTPREFIX'] = ''
            base_settings['cluster_options']['POSTPROCESSFLAG'] = 'false'
            base_settings['cluster_options']['POSTEXE'] = ''
            base_settings['cluster_options']['POSTPOSTPROCESSFLAG'] = 'true'
        else:
            # set further fixed options when not using Singularity
            base_settings['cluster_options']['singularity_path'] = None
            base_settings['cluster_options']['singularity_bind'] = None
            base_settings['cluster_options']['POSTPOSTPROCESSFLAG'] = 'false'

        # initalize sub-dictionary for ECS task options within base settings to None
        base_settings['ecs_task_options'] = None

        return cls(base_settings)

    # ------------------- CHILD METHODS THAT MUST BE IMPLEMENTED ------------------
    def pre_run(self):
        """
        Pre-run routine for local and remote computing with Singularity, such as
        automated port-forwarding and copying files/folders

        Returns:
            None

        """

        # pre-run routines required when using Singularity both local and remote
        if self.singularity is True:
            self.singularity_manager.check_singularity_system_vars()
            self.singularity_manager.prepare_singularity_files()

            # pre-run routines required when using Singularity remote only
            if self.remote:
                _, _, hostname, _ = run_subprocess('hostname -i')
                _, _, username, _ = run_subprocess('whoami')
                address_localhost = username.rstrip() + r'@' + hostname.rstrip()

                self.singularity_manager.kill_previous_queens_ssh_remote(username)
                self.singularity_manager.establish_port_forwarding_local(address_localhost)
                self.port = self.singularity_manager.establish_port_forwarding_remote(
                    address_localhost
                )

                self.singularity_manager.copy_temp_json()
                self.singularity_manager.copy_post_post()

    def _submit_singularity(self, job_id, batch, restart):
        """Submit job remotely to Singularity

        Args:
            job_id (int):    ID of job to submit
            batch (str):     Batch number of job

        Returns:
            int:            process ID

        """
        if self.remote:
            # "normal" submission
            if not restart:
                # set job name as well as paths to input file and
                # destination directory for jobscript
                self.cluster_options['job_name'] = '{}_{}_{}'.format(
                    self.experiment_name, 'queens', job_id
                )
                self.cluster_options[
                    'INPUT'
                ] = '--job_id={} --batch={} --port={} --path_json={} --workdir '.format(
                    job_id, batch, self.port, self.cluster_options['singularity_path']
                )
                self.cluster_options['DESTDIR'] = os.path.join(
                    str(self.experiment_dir), str(job_id), 'output'
                )

                # generate jobscript for submission
                submission_script_path = os.path.join(self.experiment_dir, 'jobfile.sh')
                generate_submission_script(
                    self.cluster_options,
                    submission_script_path,
                    self.cluster_options['jobscript_template'],
                    self.remote_connect,
                )

                # submit subscript remotely
                cmdlist_remote_main = [
                    'ssh',
                    self.remote_connect,
                    '"cd',
                    self.experiment_dir,
                    ';',
                    self.cluster_options['start_cmd'],
                    submission_script_path,
                    '"',
                ]
                cmd_remote_main = ' '.join(cmdlist_remote_main)
                _, _, stdout, stderr = run_subprocess(cmd_remote_main)

                # error check
                if stderr:
                    raise RuntimeError(
                        "\nThe file 'remote_main' in remote singularity image "
                        "could not be executed properly!"
                        f"\nStderr from remote:\n{stderr}"
                    )

                # check matching of job ID
                match = self.get_cluster_job_id(stdout)

                try:
                    return int(match)
                except ValueError:
                    sys.stderr.write(stdout)
                    return None
            # restart submission
            else:
                self.cluster_options['EXE'] = self.cluster_options['singularity_path'] + \
                                              '/driver.simg'
                self.cluster_options[
                    'INPUT'
                ] = '--job_id={} --batch={} --port={} --path_json={}'.format(
                    job_id, batch, self.port, self.cluster_options['singularity_path']
                )
                command_list = [
                    'singularity run',
                    self.cluster_options['EXE'],
                    self.cluster_options['INPUT'],
                    '--post=true',
                ]
                submission_script_path = ' '.join(command_list)
                cmdlist_remote_main = [
                    'ssh',
                    self.remote_connect,
                    '"cd',
                    self.experiment_dir,
                    ';',
                    submission_script_path,
                    '"',
                ]
                cmd_remote_main = ' '.join(cmdlist_remote_main)
                _, _, _, _ = run_subprocess(cmd_remote_main)

                return 0
        else:
            raise ValueError("\nSingularity cannot yet be used locally on computing clusters!")
            return None

    def get_cluster_job_id(self, output):
        """
        Helper function to retrieve job_id information after
        submitting a job to the job scheduling software

        Args:
            output (string): Output returned when submitting the job

        Returns:
            match object (str): with regular expression matching job id

        """
        if self.scheduler_type == 'pbs':
            output = output.split('.')[0]
        else:
            output = output.split()[-1]

        return output

    def alive(self, process_id):  # TODO method might me depreciated!
        """ Check whether job is alive
        The function checks if job is alive. If it is not i.e., the job is
        either on hold or suspended the function will attempt to kill it

        Args:
            process_id (int): id of process associated with job

        Returns:
            bool: is job alive or dead

        """

        # initialize alive flag to False
        alive = False

        # set check command, check location and delete command for PBS or SLURM
        if self.scheduler_type == 'pbs':
            check_cmd = 'qstat'
            check_loc = -2
            del_cmd = 'qdel'
        else:
            check_cmd = 'squeue --job'
            check_loc = -4
            del_cmd = 'scancel'

        try:
            # generate check command
            command_list = [
                'ssh',
                self.remote_connect,
                '"',
                check_cmd,
                str(process_id),
                '"',
            ]
            command_string = ' '.join(command_list)
            _, _, stdout, _ = run_subprocess(command_string)

            # split output string
            output2 = stdout.split()

            # second/fourth to last entry should be job status
            # TODO: Check if that still holds
            status = output2[check_loc]
        except ValueError:
            # job not found
            status = -1
            sys.stdout.write("EXC: %s\n" % str(sys.exc_info()[0]))
            sys.stdout.write("Could not find job for process id %d\n" % process_id)

        if status == 'Q':
            sys.stdout.write("Job %d waiting in queue.\n" % (process_id))
            alive = True
        elif status == 'R':
            sys.stdout.write("Job %d running.\n" % (process_id))
            alive = True
        elif status in ['H', 'S']:
            sys.stdout.write("Job %d held or suspended.\n" % (process_id))
            alive = False

        if not alive:
            try:
                # generate delete command
                command_list = [
                    'ssh',
                    self.remote_connect,
                    '"',
                    del_cmd,
                    str(process_id),
                    '"',
                ]
                command_string = ' '.join(command_list)
                _, _, stdout, stderr = run_subprocess(command_string)

                sys.stdout.write("Killed job %d.\n" % (process_id))
            except ValueError:
                sys.stdout.write("Failed to kill job %d.\n" % (process_id))

            return False
        else:
            return True

    def check_job_completion(self, job):
        """
        Check whether this job has been completed

        Returns:
            None

        """
        # intialize completion and failure flags to false
        # (Note that failure is not checked for cluster scheduler
        #  and returned false in any case.)
        completed = False
        failed = False

        if self.remote:
            # indicate completion by existing control file in remote output directory
            command_list = [
                'ssh',
                self.remote_connect,
                '"ls',
                job['control_file_path'],
                '"',
            ]
            command_string = ' '.join(command_list)
            _, _, _, stderr = run_subprocess(command_string)

            if not stderr:
                completed = True
        else:
            # indicate completion by existing control file in local output directory
            completed = os.path.isfile(job['control_file_path'])

        return completed, failed

    def post_run(self):
        """
        Post-run routine for remote computing with Singularity: close ports

        Returns:
            None

        """
        if self.remote and self.singularity:
            self.singularity_manager.close_remote_port(self.port)
            print('All port-forwardings were closed again.')

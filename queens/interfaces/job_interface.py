"""Job interface class."""

from queens.interfaces.interface import Interface
from queens.utils.logger_settings import log_init_args


class JobInterface(Interface):
    """Class for mapping input variables to responses.

    Attributes:
        scheduler (Scheduler):      scheduler for the simulations
        driver (Driver):            driver for the simulations
    """

    @log_init_args
    def __init__(self, scheduler, driver):
        """Create JobInterface.

        Args:
            scheduler (Scheduler):      scheduler for the simulations
            driver (Driver):            driver for the simulations
        """
        super().__init__()
        self.scheduler = scheduler
        self.driver = driver
        self.scheduler.copy_files_to_experiment_dir(self.driver.files_to_copy)

    def evaluate(self, samples):
        """Evaluate.

        Args:
            samples (np.array): Samples of simulation input variables

        Returns:
            output (dict): Output data
        """
        output = self.scheduler.evaluate(samples, driver=self.driver)
        return output

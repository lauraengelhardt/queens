import numpy as np
import GPy
from . regression_approximation import RegressionApproximation

class GPGPyRegression(RegressionApproximation):
    """ Class for creating GP based regression model based on GPy

    This class constructs a GP regression, currently using a GPy model.
    Currently, a lot of parameters are still hard coded, which will be
    improved in the future

    Attributes:
        X (np.array):               Training inputs
        y (np.array):               Training outputs
        m (Gpy.model):              GPy based Gaussian process model

    """
    @classmethod
    def from_options(cls, approx_options, x_train, y_train):
        """ Create approxiamtion from options dictionary

        Args:
            approx_options (dict): Dictionary with approximation options
            x_train (np.array):    Training inputs
            y_train (np.array):    Training outputs

        Returns:
            gp_approximation_gpy: approximation object
        """
        num_posterior_samples = approx_options.get('num_posterior_samples', None)
        return cls(x_train, y_train, num_posterior_samples)

    def __init__(self, X, y, num_posterior_samples):
        """
        Args:
            approx_options (dict):  Dictionary with model options
            X (np.array):           Training inputs
            y (np.array):           Training outputs
        """
        self.X = X
        self.y = y
        self.num_posterior_samples = num_posterior_samples

        # input dimension
        input_dim = self.X.shape[1]
        # simple GP Model
        k = GPy.kern.RBF(input_dim, ARD=True)

        self.m = GPy.models.GPRegression(self.X, self.y,
                                         kernel=k,
                                         normalizer=True)

    def train(self):
        """ Train the GP by maximizing the likelihood """

        self.m[".*Gaussian_noise"] = self.m.Y.var()*0.01
        self.m[".*Gaussian_noise"].fix()
        self.m.optimize(max_iters=500)
        self.m[".*Gaussian_noise"].unfix()
        self.m[".*Gaussian_noise"].constrain_positive()
        self.m.optimize_restarts(30, optimizer="bfgs", max_iters=1000)

    def predict(self, Xnew):
        """ Compute latent function at Xnew

        Args:
            Xnew (np.array): Inputs at which to evaluate latent function f

        Returns:
            dict: Dictionary with mean, variance, and posibly posterior samples
                  of latent function at Xnew
        """
        output = {}
        mean, variance = self.predict_f(Xnew)
        output['mean'] = np.reshape(np.array(mean), (-1, 1))
        output['variance'] = np.reshape(np.array(variance), (-1, 1))
        if self.num_posterior_samples is not None:
            output['post_samples'] = self.predict_f_samples(Xnew, self.num_posterior_samples)

        return output

    def predict_f(self, Xnew):
        """ Compute the mean and variance of the latent function at Xnew

        Args:
            Xnew (np.array): Inputs at which to evaluate latent function f

        Returns:
            np.array, np.array: mean and varaince of latent function at Xnew
        """
        return self.m.predict_noiseless(Xnew, full_cov=False)


    def predict_f_samples(self, Xnew, num_samples):
        """ Produce samples from the posterior latent funtion Xnew

            Args:
                Xnew (np.array):    Inputs at which to evaluate latent function f
                num_samples (int):  Number of posterior realizations of GP

            Returns:
                np.array, np.array: mean and variance of latent functions at Xnew
        """
        return self.m.posterior_samples_f(Xnew, num_samples)

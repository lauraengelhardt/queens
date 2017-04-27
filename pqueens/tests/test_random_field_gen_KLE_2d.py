'''
Created on April 25th 2017
@author: jbi

'''

import unittest
import numpy as np

from scipy import stats
from scipy.stats import norm
from  pqueens.randomfields.random_field_gen_KLE_2d import RandomFieldGenKLE2D
from  pqueens.randomfields.univariate_field_generator_factory import UniVarRandomFieldGeneratorFactory

class TestRandomFieldGeneratorKLE2D(unittest.TestCase):

    def setUp(self):
        # setup some necessary variables to setup random field generators
        self.dimension               = 2
        self.corrstruct              = 'exp'
        self.corr_length             = 25
        self.energy_frac             = 0.95
        self.field_bbox              = np.array([-100, 100,-100,100])
        self.marginal_pdf            = norm(0,1)
        self.num_terms_per_dim       = 100
        self.total_terms             = 500
        self.loc                     = np.array([[0,0],[0,10],[10,0],[0,25],[25,0],[0,100],[100,0]])
        self.seed                    = 42

        self.my_field_generator = UniVarRandomFieldGeneratorFactory.create_new_random_field_generator(
            self.marginal_pdf,
            self.dimension,
            self.corrstruct,
            self.corr_length,
            self.energy_frac,
            self.field_bbox,
            self.num_terms_per_dim,
            self.total_terms)

        self.my_stoch_dim = self.my_field_generator.get_stoch_dim()


    #should trigger error because desired energy fraction not reached
    def test_not_enough_fourier_terms(self):
        with self.assertRaises(RuntimeError):
            UniVarRandomFieldGeneratorFactory.create_new_random_field_generator(
            self.marginal_pdf,
            self.dimension,
            self.corrstruct,
            self.corr_length,
            0.95,
            self.field_bbox,
            100,
            300)

    # # should trigger error because number of phase angles do not match stochastic
    # # dimension
    def test_wrong_number_phase_angles(self):
        with self.assertRaises(RuntimeError):
            mystuff = UniVarRandomFieldGeneratorFactory.create_new_random_field_generator(
            self.marginal_pdf,
            self.dimension,
            self.corrstruct,
            self.corr_length,
            self.energy_frac,
            self.field_bbox,
            self.num_terms_per_dim,
            self.total_terms)
            mystuff.gen_sample_gauss_field(self.loc,np.array((4,4)))

    def test_values_at_location(self):
        np.random.seed(self.seed)
        xi = np.random.randn(self.my_stoch_dim,1)
        my_vals = self.my_field_generator.evaluate_field_at_location(self.loc ,xi)
        # last two arguments are relative and absolute tolerance, respectively
        #np.set_printoptions(formatter={'float': '{: 0.15f}'.format})
        #print(my_vals)
        np.testing.assert_allclose(my_vals,np.array([[-0.665726237739988],
                                                     [-0.371901389999928],
                                                     [-0.074676008030150],
                                                     [-0.238739257314139],
                                                     [ 1.184452833884898],
                                                     [-0.505547339253617],
                                                     [-0.912493463869035]]),
                                                     1e-07,1e-07)
    def test_correlation(self):
        my_vals = np.zeros((self.loc.shape[0], 200))
        np.random.seed(self.seed)
        for i in range(200):
            xi = np.random.randn(self.my_stoch_dim,1)
            my_vals[:, i] = self.my_field_generator.evaluate_field_at_location(self.loc, xi).ravel()

        # compute empirical correlation coefficient
        act_corr_at_dist_10_1 = np.corrcoef(my_vals[0, :], my_vals[2, :])
        act_corr_at_dist_10_2 = np.corrcoef(my_vals[0, :], my_vals[1, :])
        act_corr_at_dist_25_1 = np.corrcoef(my_vals[0, :], my_vals[4, :])
        act_corr_at_dist_25_2 = np.corrcoef(my_vals[0, :], my_vals[3, :])
        act_corr_at_dist_100_1 = np.corrcoef(my_vals[0, :], my_vals[6, :])
        act_corr_at_dist_100_2 = np.corrcoef(my_vals[0, :], my_vals[5, :])


        # print(act_corr_at_dist_10_1[0,1])
        # print(act_corr_at_dist_10_2[0,1])
        # print(act_corr_at_dist_25_1[0,1])
        # print(act_corr_at_dist_25_2[0,1])
        # print(act_corr_at_dist_100_1[0,1])
        # print(act_corr_at_dist_100_2[0,1])


        ref_corr_at_dist_10_1 = 0.775464749465
        ref_corr_at_dist_10_2 = 0.721072478791
        ref_corr_at_dist_25_1 = 0.420837149469
        ref_corr_at_dist_25_2 = 0.274529925672
        ref_corr_at_dist_100_1 = -0.0133749734437
        ref_corr_at_dist_100_2 = -0.0574405583789

        self.assertAlmostEqual(act_corr_at_dist_10_1[0,1], ref_corr_at_dist_10_1,
                               7, 'Correlation for distance 10 is not correct.')
        self.assertAlmostEqual(act_corr_at_dist_10_2[0,1], ref_corr_at_dist_10_2,
                              7, 'Correlation for distance 10 is not correct.')
        self.assertAlmostEqual(act_corr_at_dist_25_1[0,1], ref_corr_at_dist_25_1,
                               7, 'Correlation for distance 25 is not correct.')
        self.assertAlmostEqual(act_corr_at_dist_25_2[0,1], ref_corr_at_dist_25_2,
                               7, 'Correlation for distance 25 is not correct.')
        self.assertAlmostEqual(act_corr_at_dist_100_1[0,1], ref_corr_at_dist_100_1,
                               7,'Correlation for distance 100 is not correct.')
        self.assertAlmostEqual(act_corr_at_dist_100_2[0,1], ref_corr_at_dist_100_2,
                               7,'Correlation for distance 100 is not correct.')

    def test_marginal_distribution(self):
        my_vals=np.zeros((1, 200))
        np.random.seed(self.seed)
        for i in range(200):
            xi = np.random.randn(self.my_stoch_dim,1)
            my_vals[0, i] = self.my_field_generator.evaluate_field_at_location(np.array([[30., 30]]), xi)

        # try to check whether marginal distribution is normally distributed
        # using kstest
        test_statistic = (stats.kstest(my_vals[0, :], 'norm'))[0]
        self.assertAlmostEqual(test_statistic,0.064687161996999587)


if __name__ == '__main__':
    unittest.main()

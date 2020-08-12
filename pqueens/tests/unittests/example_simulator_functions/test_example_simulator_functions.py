"""
Test module for example simulator functions.
"""
import numpy as np
import pytest
import unittest

import pqueens.tests.integration_tests.example_simulator_functions.agawal as agawal

import pqueens.tests.integration_tests.example_simulator_functions.borehole_hifi as borehole_hifi
import pqueens.tests.integration_tests.example_simulator_functions.borehole_lofi as borehole_lofi

import pqueens.tests.integration_tests.example_simulator_functions.branin_hifi as branin_hifi
import pqueens.tests.integration_tests.example_simulator_functions.branin_lofi as branin_lofi
import pqueens.tests.integration_tests.example_simulator_functions.branin_medfi as branin_medfi

import pqueens.tests.integration_tests.example_simulator_functions.currin88_hifi as currin88_hifi
import pqueens.tests.integration_tests.example_simulator_functions.currin88_lofi as currin88_lofi

import pqueens.tests.integration_tests.example_simulator_functions.gardner2014a as gardner2014a

import pqueens.tests.integration_tests.example_simulator_functions.ishigami as ishigami

import pqueens.tests.integration_tests.example_simulator_functions.ma2009 as ma2009

import pqueens.tests.integration_tests.example_simulator_functions.oakley_ohagan2004 as \
    oakley_ohagan2004

import pqueens.tests.integration_tests.example_simulator_functions.park91a_hifi as \
    park91a_hifi
import pqueens.tests.integration_tests.example_simulator_functions.park91a_lofi as \
    park91a_lofi

import pqueens.tests.integration_tests.example_simulator_functions.park91b_hifi as \
    park91b_hifi
import pqueens.tests.integration_tests.example_simulator_functions.park91b_lofi as \
    park91b_lofi

import pqueens.tests.integration_tests.example_simulator_functions.perdikaris_1dsin_hifi as \
    perdikaris_1dsin_hifi
import pqueens.tests.integration_tests.example_simulator_functions.perdikaris_1dsin_lofi as \
    perdikaris_1dsin_lofi

import pqueens.tests.integration_tests.example_simulator_functions.sobol as sobol


class TestAgawal(unittest.TestCase):
    def setUp(self):
        self.params1 = {'x1': 0.6, 'x2': 0.4}
        self.params2 = {'x1': 0.4, 'x2': 0.4}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result1 = agawal.main(self.dummy_id, self.params1)
        desired_result1 = 0.0
        self.assertAlmostEqual(actual_result1, desired_result1, places=8, msg=None, delta=None)

        actual_result2 = agawal.main(self.dummy_id, self.params2)
        desired_result2 = 0.90450849718747361
        self.assertAlmostEqual(actual_result2, desired_result2, places=8, msg=None, delta=None)


class TestPerdikarisMultiFidelity(unittest.TestCase):
    def setUp(self):
        self.params1 = {'x': 0.6}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result_hifi = perdikaris_1dsin_lofi.main(self.dummy_id, self.params1)
        actual_result_lofi = perdikaris_1dsin_hifi.main(self.dummy_id, self.params1)

        # print("actual_result_hifi {}".format(actual_result_hifi))
        # print("actual_result_lofi {}".format(actual_result_lofi))

        desired_result_hifi = 0.5877852522924737
        desired_result_lofi = -0.2813038672746218

        self.assertAlmostEqual(
            actual_result_hifi, desired_result_hifi, places=8, msg=None, delta=None
        )

        self.assertAlmostEqual(
            actual_result_lofi, desired_result_lofi, places=8, msg=None, delta=None
        )


class TestBraninMultiFidelity(unittest.TestCase):
    def setUp(self):
        self.params1 = {'x1': -4, 'x2': 5}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result_hifi = branin_hifi.main(self.dummy_id, self.params1)
        actual_result_medfi = branin_medfi.main(self.dummy_id, self.params1)
        actual_result_lofi = branin_lofi.main(self.dummy_id, self.params1)

        # print("actual_result_hifi {}".format(actual_result_hifi))
        # print("actual_result_medfi {}".format(actual_result_medfi))
        # print("actual_result_lofi {}".format(actual_result_lofi))

        desired_result_hifi = 92.70795679406056
        desired_result_medfi = 125.49860898539086
        desired_result_lofi = 1.4307273110713652

        self.assertAlmostEqual(
            actual_result_hifi, desired_result_hifi, places=8, msg=None, delta=None
        )

        self.assertAlmostEqual(
            actual_result_medfi, desired_result_medfi, places=8, msg=None, delta=None
        )

        self.assertAlmostEqual(
            actual_result_lofi, desired_result_lofi, places=8, msg=None, delta=None
        )


class TestPark91aMultiFidelity(unittest.TestCase):
    def setUp(self):
        self.params1 = {'x1': 0.3, 'x2': 0.6, 'x3': 0.5, 'x4': 0.1}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result_hifi = park91a_hifi.main(self.dummy_id, self.params1)
        actual_result_lofi = park91a_lofi.main(self.dummy_id, self.params1)

        # print("actual_result_hifi {}".format(actual_result_hifi))
        # print("actual_result_lofi {}".format(actual_result_lofi))

        desired_result_hifi = 2.6934187033863846
        desired_result_lofi = 3.2830146685714103

        self.assertAlmostEqual(
            actual_result_hifi, desired_result_hifi, places=8, msg=None, delta=None
        )

        self.assertAlmostEqual(
            actual_result_lofi, desired_result_lofi, places=8, msg=None, delta=None
        )


class TestPark91bMultiFidelity(unittest.TestCase):
    def setUp(self):
        self.params1 = {'x1': 0.3, 'x2': 0.6, 'x3': 0.5, 'x4': 0.1}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result_hifi = park91b_hifi.main(self.dummy_id, self.params1)
        actual_result_lofi = park91b_lofi.main(self.dummy_id, self.params1)

        # print("actual_result_hifi {}".format(actual_result_hifi))
        # print("actual_result_lofi {}".format(actual_result_lofi))

        desired_result_hifi = 2.091792853577546
        desired_result_lofi = 1.510151424293055

        self.assertAlmostEqual(
            actual_result_hifi, desired_result_hifi, places=8, msg=None, delta=None
        )

        self.assertAlmostEqual(
            actual_result_lofi, desired_result_lofi, places=8, msg=None, delta=None
        )


class TestOakleyOHagan(unittest.TestCase):
    def setUp(self):
        self.params1 = {
            'x1': 0.3,
            'x2': 0.6,
            'x3': 0.5,
            'x4': 0.1,
            'x5': 0.9,
            'x6': 0.3,
            'x7': 0.6,
            'x8': 0.5,
            'x9': 0.1,
            'x10': 0.9,
            'x11': 0.3,
            'x12': 0.6,
            'x13': 0.5,
            'x14': 0.1,
            'x15': 0.9,
        }
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result = oakley_ohagan2004.main(self.dummy_id, self.params1)

        # print("actual_result {}".format(actual_result))

        desired_result = 24.496726490699082

        self.assertAlmostEqual(actual_result, desired_result, places=8, msg=None, delta=None)


class TestMa(unittest.TestCase):
    def setUp(self):
        self.params1 = {'x1': 0.25, 'x2': 0.5}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result = ma2009.main(self.dummy_id, self.params1)

        # print("actual_result {}".format(actual_result))

        desired_result = 8.8888888888888875

        self.assertAlmostEqual(actual_result, desired_result, places=8, msg=None, delta=None)


class TestCurrin88bMultiFidelity(unittest.TestCase):
    def setUp(self):
        self.params1 = {'x1': 0.6, 'x2': 0.1}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result_hifi = currin88_hifi.main(self.dummy_id, self.params1)
        actual_result_lofi = currin88_lofi.main(self.dummy_id, self.params1)

        # print("actual_result_hifi {}".format(actual_result_hifi))
        # print("actual_result_lofi {}".format(actual_result_lofi))

        desired_result_hifi = 11.06777716201019
        desired_result_lofi = 10.964538831722423

        self.assertAlmostEqual(
            actual_result_hifi, desired_result_hifi, places=8, msg=None, delta=None
        )

        self.assertAlmostEqual(
            actual_result_lofi, desired_result_lofi, places=8, msg=None, delta=None
        )


class TestBoreholeMultiFidelity(unittest.TestCase):
    def setUp(self):
        self.params1 = {
            'rw': 0.1,
            'r': 500,
            'Tu': 70000,
            'Hu': 1000,
            'Tl': 80,
            'Hl': 750,
            'L': 1550,
            'Kw': 11100,
        }
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result_hifi = borehole_hifi.main(self.dummy_id, self.params1)
        actual_result_lofi = borehole_lofi.main(self.dummy_id, self.params1)

        # print("actual_result_hifi {}".format(actual_result_hifi))
        # print("actual_result_lofi {}".format(actual_result_lofi))

        desired_result_hifi = 56.03080181188316
        desired_result_lofi = 44.58779860979928

        self.assertAlmostEqual(
            actual_result_hifi, desired_result_hifi, places=8, msg=None, delta=None
        )

        self.assertAlmostEqual(
            actual_result_lofi, desired_result_lofi, places=8, msg=None, delta=None
        )


@pytest.fixture(scope="module")
def dummy_job_id():
    """ A possible job id for the main wrappers. """
    return 666


@pytest.fixture(scope="module")
def parameters_sobol_8dim():
    """ Possible parameters for 8 dimensional Sobol G function. """
    A = np.array([0, 1, 4.5, 9, 99, 99, 99, 99])
    ALPHA = np.array([1.0] * A.shape[0])
    DELTA = np.array([0.0] * A.shape[0])

    return dict(a=A, alpha=ALPHA, delta=DELTA)


@pytest.fixture(scope="module")
def input_sobol_8dim():
    """ Possible input vector for 8 dimensional Sobol G function. """
    input_vector = {
        'x1': 0.1,
        'x2': 0.23,
        'x3': 0.4,
        'x4': 0.6,
        'x5': 0.1,
        'x6': 0.25,
        'x7': 0.98,
        'x8': 0.7,
    }
    return input_vector


@pytest.fixture(scope="module")
def input_sobol_10dim():
    """ Possible input vector for 10 dimensional Sobol G function. """
    input_vector = {
        'x1': 0.1,
        'x2': 0.23,
        'x3': 0.4,
        'x4': 0.6,
        'x5': 0.1,
        'x6': 0.25,
        'x7': 0.98,
        'x8': 0.7,
        'x9': 0.33,
        'x10': 0.8,
    }
    return input_vector


def test_sobol_8dim(parameters_sobol_8dim, input_sobol_8dim):
    """ Test 8 dimensional Sobol G function. """
    expected_result = 1.4119532907954928

    a = parameters_sobol_8dim["a"]
    alpha = parameters_sobol_8dim["alpha"]
    delta = parameters_sobol_8dim["delta"]
    result = sobol.sobol(a=a, alpha=alpha, delta=delta, **input_sobol_8dim)

    assert np.allclose(result, expected_result)


def test_sobol_8dim_first_order_variance(parameters_sobol_8dim):
    """ Test first order variance of 8 dimensional Sobol G function. """
    expected_result = np.array(
        [
            0.3333333333333333,
            0.08333333333333333,
            0.011019283746556472,
            0.003333333333333333,
            3.333333333333333e-05,
            3.333333333333333e-05,
            3.333333333333333e-05,
            3.333333333333333e-05,
        ]
    )
    a = parameters_sobol_8dim["a"]
    alpha = parameters_sobol_8dim["alpha"]
    result = sobol.first_effect_variance(a=a, alpha=alpha)

    assert np.allclose(result, expected_result)


def test_sobol_8dim_variance():
    """ Test variance of 8 dimensional Sobol G function. """
    expected_result = 0.4654244319022063

    Vi = np.array(
        [
            0.3333333333333333,
            0.08333333333333333,
            0.011019283746556472,
            0.003333333333333333,
            3.333333333333333e-05,
            3.333333333333333e-05,
            3.333333333333333e-05,
            3.333333333333333e-05,
        ]
    )
    result = sobol.variance(Vi=Vi)

    assert np.allclose(result, expected_result)


def test_sobol_8dim_first_order_indices(parameters_sobol_8dim):
    """ Test first order indices of 8 dimensional Sobol G function. """
    expected_result = np.array(
        [
            0.7161921688790338,
            0.17904804221975845,
            0.0236757741778193,
            0.007161921688790339,
            7.161921688790338e-05,
            7.161921688790338e-05,
            7.161921688790338e-05,
            7.161921688790338e-05,
        ]
    )
    a = parameters_sobol_8dim["a"]
    alpha = parameters_sobol_8dim["alpha"]

    result = sobol.first_order_indices(a=a, alpha=alpha)

    assert np.allclose(result, expected_result)


def test_sobol_8dim_total_order_indices(parameters_sobol_8dim):
    """ Test total order indices of 8 dimensional Sobol G function. """
    expected_result = np.array(
        [
            0.7871441266592755,
            0.24219819281823862,
            0.03431691015408285,
            0.01046038706523954,
            0.00010494905191950606,
            0.00010494905191950606,
            0.00010494905191950606,
            0.00010494905191950606,
        ]
    )
    a = parameters_sobol_8dim["a"]
    alpha = parameters_sobol_8dim["alpha"]

    result = sobol.total_order_indices(a=a, alpha=alpha)

    assert np.allclose(result, expected_result)


def test_sobol_negative_a_valueerror(parameters_sobol_8dim, input_sobol_8dim):
    """ Test 10 dimensional Sobol G function raises ValueError with a<0 """
    # test negative value
    alpha = parameters_sobol_8dim["alpha"]
    delta = parameters_sobol_8dim["delta"]
    with pytest.raises(ValueError):
        a = parameters_sobol_8dim["a"]
        a[0] = -1.23
        result = sobol.sobol(a=a, alpha=alpha, delta=delta, **input_sobol_8dim)


def test_sobol_negative_alpha_valueerror(parameters_sobol_8dim, input_sobol_8dim):
    """ Test 10 dimensional Sobol G function raises ValueError with alpha<=0. """
    a = parameters_sobol_8dim["a"]
    delta = parameters_sobol_8dim["delta"]
    # test negative alpha value
    with pytest.raises(ValueError):
        alpha = parameters_sobol_8dim["alpha"]
        alpha[1] = -1.23
        result = sobol.sobol(a=a, alpha=alpha, delta=delta, **input_sobol_8dim)
    with pytest.raises(ValueError):
        alpha = parameters_sobol_8dim["alpha"]
        alpha[6] = 0.0
        result = sobol.sobol(a=a, alpha=alpha, delta=delta, **input_sobol_8dim)


def test_sobol_delta_out_of_bound_valueerror(parameters_sobol_8dim, input_sobol_8dim):
    """ Test 10 dimensional Sobol G function raises ValueError with delta not in 0<=delta<=1.0. """
    a = parameters_sobol_8dim["a"]
    alpha = parameters_sobol_8dim["alpha"]
    # test negative delta value
    with pytest.raises(ValueError):
        delta = parameters_sobol_8dim["delta"]
        delta[1] = -1.23
        result = sobol.sobol(a=a, alpha=alpha, delta=delta, **input_sobol_8dim)
    # test delta>1 value
    with pytest.raises(ValueError):
        delta = parameters_sobol_8dim["delta"]
        delta[7] = 4.2
        result = sobol.sobol(a=a, alpha=alpha, delta=delta, **input_sobol_8dim)


def test_sobol_shape_mismatch_valueerror(parameters_sobol_8dim, input_sobol_8dim):
    """ Test 10 dimensional Sobol G function raises ValueError with delta not in 0<=delta<=1.0. """
    a = parameters_sobol_8dim["a"]
    alpha = parameters_sobol_8dim["alpha"]
    delta = parameters_sobol_8dim["delta"]
    # test a to small
    with pytest.raises(ValueError):
        result = sobol.sobol(a=a[0:6], alpha=alpha, delta=delta, **input_sobol_8dim)
    # test alpha to small
    with pytest.raises(ValueError):
        result = sobol.sobol(a=a, alpha=alpha[0:6], delta=delta, **input_sobol_8dim)
    # test delta to small
    with pytest.raises(ValueError):
        result = sobol.sobol(a=a, alpha=alpha, delta=delta[0:6], **input_sobol_8dim)
    # test x to small
    with pytest.raises(ValueError):
        too_small_input = input_sobol_8dim.copy()
        too_small_input.pop("x8")
        result = sobol.sobol(a=a, alpha=alpha, delta=delta, **too_small_input)


def test_sobol_default_10dim(input_sobol_10dim):
    """ Test 10 dimensional Sobol G function. """
    expected_result = 0.27670926062343376
    result = sobol.sobol(**input_sobol_10dim)

    assert np.allclose(result, expected_result)


def test_sobol_main_wrapper(input_sobol_10dim, dummy_job_id):
    """ Test 10 dimensional Sobol G function called with main wrapper. """
    expected_result = 0.27670926062343376
    result = sobol.main(dummy_job_id, input_sobol_10dim)

    assert np.allclose(result, expected_result)


def test_sobol_default_10dim_first_order_variance():
    """ Test first order variance of 10 dimensional Sobol G function. """
    expected_result = np.array(
        [
            0.8,
            0.6611570247933883,
            0.5555555555555556,
            0.47337278106508873,
            0.4081632653061225,
            0.24691358024691357,
            0.2,
            0.08888888888888889,
            0.05,
            0.032,
        ]
    )
    result = sobol.first_effect_variance()

    assert np.allclose(result, expected_result)


def test_sobol_default_10dim_variance():
    """ Test variance of 10 dimensional Sobol G function. """
    expected_result = 16.037447681001517

    Vi = np.array(
        [
            0.8,
            0.6611570247933883,
            0.5555555555555556,
            0.47337278106508873,
            0.4081632653061225,
            0.24691358024691357,
            0.2,
            0.08888888888888889,
            0.05,
            0.032,
        ]
    )
    result = sobol.variance(Vi=Vi)

    assert np.allclose(result, expected_result)


def test_sobol_10dim_first_order_indices():
    """ Test first order indices of 10 dimensional Sobol G function. """
    expected_result = np.array(
        [
            0.049883249249673696,
            0.0412258258261766,
            0.0346411453122734,
            0.029516715532351294,
            0.0254506373722825,
            0.01539606458323262,
            0.012470812312418424,
            0.0055425832499637435,
            0.003117703078104606,
            0.0019953299699869476,
        ]
    )
    result = sobol.first_order_indices()

    assert np.allclose(result, expected_result)


def test_sobol_default_10dim_total_order_indices():
    """ Test total order indices of 10 dimensional Sobol G function. """
    expected_result = np.array(
        [
            0.4721573606942631,
            0.42282748718889235,
            0.37941216484360435,
            0.3413185739958529,
            0.30792871349625867,
            0.2103671409033846,
            0.1770590102603487,
            0.086722780535681,
            0.05058828864581391,
            0.03294121121122766,
        ]
    )
    result = sobol.total_order_indices()

    assert np.allclose(result, expected_result)


@pytest.fixture(scope="module")
def parameters_ishigami():
    """ Possible parameters for Ishigami function. """
    P1 = 7
    P2 = 0.1

    return dict(p1=P1, p2=P2)


@pytest.fixture(scope="module")
def input_ishigami():
    """ Possible input vector for Ishigami function.. """
    input_vector = {'x1': 0.1, 'x2': 0.23, 'x3': 0.4}
    return input_vector


@pytest.fixture(scope="module")
def expected_result_ishigami():
    return 0.4639052488541057


def test_ishigami(parameters_ishigami, input_ishigami, expected_result_ishigami):
    """ Test Ishigami function. """
    P1 = parameters_ishigami["p1"]
    P2 = parameters_ishigami["p2"]

    result = ishigami.ishigami(*input_ishigami.values(), p1=P1, p2=P2)

    assert np.allclose(result, expected_result_ishigami)


def test_ishigami_default_parameter(input_ishigami, expected_result_ishigami):
    """ Test Ishigami function with default parameters. """
    result = ishigami.ishigami(*input_ishigami.values())

    assert np.allclose(result, expected_result_ishigami)


def test_ishigami_main_wrapper(input_ishigami, expected_result_ishigami, dummy_job_id):
    """ Test Ishigami function main wrapper which uses default parameters. """
    result = ishigami.main(dummy_job_id, input_ishigami)

    assert np.allclose(result, expected_result_ishigami)


def test_ishigami_variance(parameters_ishigami):
    """ Test variance of Ishigami function. """
    P1 = parameters_ishigami["p1"]
    P2 = parameters_ishigami["p2"]

    expected_result = 13.844587940719254

    result = ishigami.variance(p1=P1, p2=P2)

    assert np.allclose(result, expected_result)


def test_ishigami_first_effect_variance(parameters_ishigami):
    """ Test first effect variance Ishigami function. """
    P1 = parameters_ishigami["p1"]
    P2 = parameters_ishigami["p2"]

    expected_result = np.array([4.34588802, 6.125, 0.0])

    result = ishigami.first_effect_variance(p1=P1, p2=P2)

    assert np.allclose(result, expected_result)


def test_ishigami_first_order_indices(parameters_ishigami):
    """ Test first order indices Ishigami function. """
    P1 = parameters_ishigami["p1"]
    P2 = parameters_ishigami["p2"]

    expected_result = np.array([0.3139051911478115, 0.4424111447900409, 0.0])

    result = ishigami.first_order_indices(p1=P1, p2=P2)

    assert np.allclose(result, expected_result)


def test_ishigami_total_order_indices(parameters_ishigami):
    """ Test total order variance Ishigami function. """
    P1 = parameters_ishigami["p1"]
    P2 = parameters_ishigami["p2"]

    expected_result = np.array([0.5575888552099593, 0.4424111447900409, 0.2436836640621477])

    result = ishigami.total_order_indices(p1=P1, p2=P2)

    assert np.allclose(result, expected_result)


@pytest.fixture(scope="module")
def input_gardner2014a():
    """ Possible input vector for gardner2014a function.. """
    input_vector = {'x1': 1.234, 'x2': 0.666}
    return input_vector


def test_gardner2014a(input_gardner2014a):
    """ Test Gardner2014a function. """

    expected_y_result = 0.32925795427636007
    expected_c_result = -0.32328956686350346

    y_result, c_result = gardner2014a.gardner2014a(
        input_gardner2014a["x1"], input_gardner2014a["x2"]
    )

    assert np.allclose(y_result, expected_y_result)
    assert np.allclose(c_result, expected_c_result)


def test_gardner2014a_main_wrapper(input_gardner2014a, dummy_job_id):
    """ Test Gardner2014a function's main wrapper. """
    expected_y_result = 0.32925795427636007
    expected_c_result = -0.32328956686350346

    y_result, c_result = gardner2014a.main(dummy_job_id, input_gardner2014a)

    assert np.allclose(y_result, expected_y_result)
    assert np.allclose(c_result, expected_c_result)

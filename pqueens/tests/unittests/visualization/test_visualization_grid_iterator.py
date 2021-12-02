import numpy as np
import os
import pytest
import re
import pqueens.visualization.grid_iterator_visualization as qvis
from pqueens.visualization.grid_iterator_visualization import GridIteratorVisualization


# general input fixtures
@pytest.fixture()
def dummy_vis(tmpdir):
    paths = [os.path.join(tmpdir, 'myplot.png')]
    save_bools = [True]
    plot_booleans = [False]
    scale_types_list = ["lin", "lin"]
    var_names_list = ["x1", "x2"]
    grid_vis = GridIteratorVisualization(
        paths, save_bools, plot_booleans, scale_types_list, var_names_list
    )
    qvis.grid_iterator_visualization_instance = grid_vis


# -------------------------------- actual unittests ---------------------------------------------
@pytest.mark.unit_tests
def test_init(tmpdir):
    # expected attributes
    paths = [os.path.join(tmpdir, 'myplot.png')]
    save_bools = [True]
    plot_booleans = [False]
    scale_types_list = ["lin", "lin"]
    var_names_list = ["x1", "x2"]

    # instantiated class
    grid_vis = GridIteratorVisualization(
        paths, save_bools, plot_booleans, scale_types_list, var_names_list
    )

    # tests / asserts
    assert grid_vis.saving_paths_list == paths
    assert grid_vis.save_bools == save_bools
    assert grid_vis.plot_booleans == plot_booleans
    assert grid_vis.scale_types_list == scale_types_list
    assert grid_vis.var_names_list == var_names_list


@pytest.mark.unit_tests
def test_plot_QoI_grid(tmpdir, dummy_vis):
    # set arguments
    output = {"mean": np.array([1.0, 2.0, 3.0, 4.0])}
    samples = np.array([[1.0, 1.0], [2.0, 2.0], [1.0, 2.0], [2.0, 1.0]])
    num_params = 2
    n_grid_p = [2, 2]
    qvis.grid_iterator_visualization_instance.plot_QoI_grid(output, samples, num_params, n_grid_p)
    filepath = os.path.join(tmpdir, 'myplot.png')
    assert os.path.isfile(filepath)


@pytest.mark.unit_tests
def test_get_plotter_one(dummy_vis):
    num_params = 1
    plotter = qvis.grid_iterator_visualization_instance._get_plotter(num_params)
    expected_str = re.split("[\s\.]", plotter.__str__())[3]
    assert "_plot_one_d" == expected_str


@pytest.mark.unit_tests
def test_get_plotter_one(dummy_vis):
    num_params = 2
    plotter = qvis.grid_iterator_visualization_instance._get_plotter(num_params)
    expected_str = re.split("[\s\.]", plotter.__str__())[3]
    assert "_plot_two_d" == expected_str


@pytest.mark.unit_tests
def test_higher_d(dummy_vis):
    num_params = 3
    with pytest.raises(NotImplementedError) as e:
        plotter = qvis.grid_iterator_visualization_instance._get_plotter(num_params)
    assert str(e.value) == 'Grid plot only possible up to 2 parameters'


@pytest.mark.unit_tests
def test_plot_one_d(dummy_vis):
    output = {'mean': np.array([0.0, 1.0])}
    samples = np.array([0.0, 1.0])
    dummy = 1.0
    return_value = qvis.grid_iterator_visualization_instance._plot_one_d(output, samples, dummy)
    assert return_value is None


@pytest.mark.unit_tests
def test_plot_two_d(dummy_vis):
    samples = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
    output = {'mean': np.array([0.0, 1.0, 0.0, 1.0])}
    n_gird_p = [2, 2]
    return_value = qvis.grid_iterator_visualization_instance._plot_two_d(output, samples, n_gird_p)
    assert return_value is None

"""TODO_doc."""

import os
import pickle
from pathlib import Path

import numpy as np
import pytest

from pqueens import run
from pqueens.utils import injector


@pytest.fixture(params=['COBYLA', 'SLSQP'])
def algorithm(request):
    """TODO_doc."""
    return request.param


def test_optimization_paraboloid_constrained(inputdir, tmpdir, algorithm):
    """Test different solution algorithms in optimization iterator.

    COBYLA: constained but unbounded

    SLSQP:  constrained and bounded
    """
    template = os.path.join(inputdir, 'optimization_paraboloid_template.yml')
    input_file = str(tmpdir) + 'paraboloid_opt.yml'

    algorithm_dict = {'algorithm': algorithm}

    injector.inject(algorithm_dict, template, input_file)

    run(Path(input_file), Path(tmpdir))

    result_file = str(tmpdir) + '/' + 'Paraboloid.pickle'
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)
    np.testing.assert_allclose(results.x, np.array([+1.4, +1.7]), rtol=1.0e-4)
    np.testing.assert_allclose(results.fun, np.array(+0.8), atol=1.0e-07)

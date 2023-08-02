"""Iterators.

The iterator package contains the implementation of several UQ and
optimization methods, each of which is implemented in their own iterator
class. The iterator is therefor one of the central building blocks, as
the iterators orchestrate the evaluations on one or multiple models.
QUEENS also permits nesting of iterators to enable hierarchical methods
or surrogate based UQ approaches.
"""

VALID_TYPES = {
    'hmc': [
        'pqueens.iterators.hmc_iterator',
        'HMCIterator',
    ],
    'lhs': ['pqueens.iterators.lhs_iterator', 'LHSIterator'],
    'lhs_mf': ['pqueens.iterators.lhs_iterator_mf', 'MFLHSIterator'],
    'metropolis_hastings': [
        'pqueens.iterators.metropolis_hastings_iterator',
        'MetropolisHastingsIterator',
    ],
    'metropolis_hastings_pymc': [
        'pqueens.iterators.metropolis_hastings_pymc_iterator',
        'MetropolisHastingsPyMCIterator',
    ],
    'monte_carlo': ['pqueens.iterators.monte_carlo_iterator', 'MonteCarloIterator'],
    'nuts': [
        'pqueens.iterators.nuts_iterator',
        'NUTSIterator',
    ],
    'optimization': ['pqueens.iterators.optimization_iterator', 'OptimizationIterator'],
    'read_data_from_file': ['pqueens.iterators.data_iterator', 'DataIterator'],
    'elementary_effects': [
        'pqueens.iterators.elementary_effects_iterator',
        'ElementaryEffectsIterator',
    ],
    'polynomial_chaos': ['pqueens.iterators.polynomial_chaos_iterator', 'PolynomialChaosIterator'],
    'sobol_indices': ['pqueens.iterators.sobol_index_iterator', 'SobolIndexIterator'],
    'sobol_indices_gp_uncertainty': [
        'pqueens.iterators.sobol_index_gp_uncertainty_iterator',
        'SobolIndexGPUncertaintyIterator',
    ],
    'smc': ['pqueens.iterators.sequential_monte_carlo_iterator', 'SequentialMonteCarloIterator'],
    'smc_chopin': [
        'pqueens.iterators.sequential_monte_carlo_chopin',
        'SequentialMonteCarloChopinIterator',
    ],
    'sobol_sequence': ['pqueens.iterators.sobol_sequence_iterator', 'SobolSequenceIterator'],
    'points': ['pqueens.iterators.points_iterator', 'PointsIterator'],
    'bmfmc': ['pqueens.iterators.bmfmc_iterator', 'BMFMCIterator'],
    'grid': ['pqueens.iterators.grid_iterator', 'GridIterator'],
    'baci_lm': ['pqueens.iterators.baci_lm_iterator', 'BaciLMIterator'],
    'bbvi': ['pqueens.iterators.black_box_variational_bayes', 'BBVIIterator'],
    'bmfia': ['pqueens.iterators.bmfia_iterator', 'BMFIAIterator'],
    'rpvi': ['pqueens.iterators.reparameteriztion_based_variational_inference', 'RPVIIterator'],
}

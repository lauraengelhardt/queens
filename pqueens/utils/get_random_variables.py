"""Utils for random variables.xxx."""

from pqueens.distributions import from_config_create_distribution


def get_random_variables(model):
    """Get random variables and fields from model.

    Args:
        model (model): Instance of model class

    Returns:
        random_variables (dict): Random variables
        random_fields (dict): Random fields
        number_input_dimensions (int): Number of input
            parameters/random variables
        distribution_info (list): Information about distribution of
            random variables
    """
    # get random variables (RV) from model
    parameters = model.get_parameter()
    random_variables = parameters.get("random_variables", None)
    if random_variables is not None:
        number_input_dimensions = len(random_variables)
    else:
        raise RuntimeError("Random variables not correctly specified.")

    # get random fields (RF)
    random_fields = parameters.get("random_fields", None)

    distribution_info = get_distribution_info(random_variables)

    return random_variables, random_fields, number_input_dimensions, distribution_info


def get_distribution_info(random_variables):
    """Get distribution info.

    Args:
        random_variables (dict): Random variables

    Return:
        distribution_info (list): Information about distribution of random variables
    """
    distribution_info = []
    for _, rv in random_variables.items():
        distribution_info.append(rv)
    return distribution_info


def get_random_samples(description, num_samples):
    """Get random samples based on QUEENS description of distribution.

    Args:
        description (dict):         Dictionary containing QUEENS distribution
                                    description
        num_samples (int):          Number of samples to generate

    Returns:
        np.array: Array with samples
    """
    distribution = from_config_create_distribution(description)
    samples = distribution.draw(num_draws=num_samples)

    return samples

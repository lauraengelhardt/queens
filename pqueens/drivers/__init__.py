# -*- coding: utf-8 -*-
"""Drivers.

This package contains a set of driver scripts which are used to make the
actual call to the simulation software running either on the system
directly or wrapped in a docker container.
"""
from pqueens.utils.import_utils import get_module_class

VALID_TYPES = {'baci': ["pqueens.drivers.baci_driver", "BaciDriver"]}


def from_config_create_driver(
    config,
    job_id,
    batch,
    driver_name,
    workdir=None,
    cluster_options=None,
):
    """Create driver from problem description.

    Args:
        config (dict):  Dictionary containing configuration from QUEENS input file
        job_id (int):   Job ID as provided in database within range [1, n_jobs]
        batch (int):    Job batch number (multiple batches possible)
        workdir (str):  Path to working directory on remote resource
        driver_name (str): Name of driver instance that should be realized

    Returns:
        driver (obj):   Driver object
    """
    driver_options = config[driver_name]
    driver_class = get_module_class(driver_options, VALID_TYPES, "driver_type")
    driver = driver_class.from_config_create_driver(
        config,
        job_id,
        batch,
        driver_name,
        workdir,
        cluster_options,
    )
    return driver

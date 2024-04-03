from aztec_gddt.params import SINGLE_RUN_PARAMS, INITIAL_STATE, TIMESTEPS, SAMPLES
from aztec_gddt.structure import AZTEC_MODEL_BLOCKS
import logging

DEFAULT_LOGGER = 'aztec-design-digital-twin'

default_run_args = (INITIAL_STATE,
                    {k: [v] for k, v in SINGLE_RUN_PARAMS.items()},
                    AZTEC_MODEL_BLOCKS,
                    TIMESTEPS,
                    SAMPLES)



def setup_logging(
    filename='cadcad.log',
    level=logging.INFO,
    format='\n%(asctime)s - %(name)s - %(levelname)s\n%(message)s',
):
    # Create a logger
    logger = logging.getLogger(DEFAULT_LOGGER)
    logger.setLevel(level)  # Set the logging level

    # Create a file handler and set level to INFO
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(level)

    # Create a console (stream) handler and set level to INFO
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(format, '%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


setup_logging()

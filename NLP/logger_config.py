import logging
import sys

def configure_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Log messages to console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Log messages to a file
    fh = logging.FileHandler('nlp_pipeline.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

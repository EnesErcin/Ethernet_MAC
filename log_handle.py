import logging
import os


def log_handle(id):
    assert type(id) == str

    log_file_path = os.getcwd() +"/Sim.log"
    logging.basicConfig(filemode='w')
    logger = logging.getLogger(id)
    logger.setLevel(logging.DEBUG)

    # Clear the existing log file
    if os.path.exists(log_file_path):
        os.remove(log_file_path)

    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
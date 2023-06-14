import logging
import os


def log_handle():
    log_file_path = os.getcwd() +"/Sim.log"
    logging.basicConfig(filename=log_file_path,
                        format='%(asctime)s %(message)s',
                        filemode='w')

    logger = logging.getLogger("Simulationg Log")
    
    if os.path.exists(log_file_path):
        os.remove(log_file_path)

    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s %(message)s')
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
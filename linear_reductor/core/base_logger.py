import logging 

# Create logger. Logging levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL (not all are necessarily used) 
logger = logging.getLogger("log")
logger.setLevel(logging.ERROR)
logger.propagate = False
formatter = logging.Formatter('%(levelname)s: %(message)s')

# Create console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)

logger.handlers = []
logger.addHandler(ch)
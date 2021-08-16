import logging 
import tqdm

class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)
            

# Create logger. Logging levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL (not all are necessarily used) 
logger = logging.getLogger("log")
logger.setLevel(logging.DEBUG)
logger.propagate = False

  

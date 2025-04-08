import sys
import logging
from ecs.logger import CustomFormatter

class ECSLogHandler(logging.StreamHandler):

    def __init__(self):
        super().__init__(sys.stdout)
        self.setFormatter(CustomFormatter())




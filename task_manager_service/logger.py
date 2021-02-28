import logging

from task_manager_service.consts import SERVICE_NAME


logger = logging.getLogger(SERVICE_NAME)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)-9s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

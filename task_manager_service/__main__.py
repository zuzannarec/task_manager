import logging

from task_manager_service.logger import logger


def create_app():
    return None


def main():
    logger.setLevel(logging.INFO)
    app = create_app()
    logger.info(f"Task manager service starting...")


if __name__ == "__main__":
    main()

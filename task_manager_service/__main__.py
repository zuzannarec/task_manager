import argparse
import logging
import os

import uvicorn
from fastapi import FastAPI

from task_manager_service import routes
from task_manager_service.task_manager_factory import TaskManagerFactory
from task_manager_service.logger import logger


def create_app(behaviour: str) -> FastAPI:
    app = FastAPI()

    @app.on_event("startup")
    async def startup_event():
        task_manager_service = TaskManagerFactory.get_task_manager(behaviour)
        app.state.text_uploader_service = task_manager_service
        app.include_router(router=routes.router)

    @app.on_event('shutdown')
    async def stutdown_event():
        await app.state.text_uploader_service.shutdown()

    return app


def main(behaviour: str):
    logger.setLevel(logging.INFO)
    app = create_app(behaviour)
    logger.info(f"Task Manager service starting...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('TASK_MANAGER_PORT', 8080)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Choose Task Manager behaviour')
    parser.add_argument('--behaviour',
                        type=str,
                        default='default',
                        choices=['default', 'fifo', 'priority_based'],
                        help='behaviour of task manager, one of [default, fifo, priority_based]')
    args = parser.parse_args()
    main(args.behaviour)

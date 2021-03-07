from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/process")
async def add_process(request: Request):
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.get("/processes")
async def get_running(request: Request, order: str):
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.delete("/process/{pid}")
async def kill_process(request: Request, pid: str):
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.delete("/processes/{priority}")
async def kill_group(request: Request, priority: str):
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.delete("/processes")
async def kill_all(request: Request):
    return JSONResponse(status_code=status.HTTP_200_OK)

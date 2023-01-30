"""
This is the Entrypoint of the Program. Following are the significant procedures/steps 
1. Operation Controller Instance
2. Funtions for specific Routes
3. Route for API calls
4. Server Instance
"""

import sys
import logging
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.routing import Route
from sqlalchemy.orm import Session
from controller import Controller
from database.session_manager import safe_session

from data_models import (
    NewClickRequest,
    SavePredict,
    JustPredict
)

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s] [%(asctime)s.%(msecs)-3d] [api] [%(filename)s:%(funcName)s] [%(message)s]",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    stream=sys.stdout,
                    force=True)


# 1. Operation Controller Instance
control = Controller()


# 2. Funtions for Routes
async def version(request):
    return JSONResponse({"version": 0})

async def save_click_and_predict_cluster_api(request: NewClickRequest, 
                                            db_session: Session = Depends(safe_session)):
    data = SavePredict(page_id=request.page_uuid.split('/')[1],
                        x=request.coordinates.x,
                        y=request.coordinates.y)
    return await control.save_and_predict(post_details=data, 
                                            db=db_session)

async def predict_cluster_api(request: NewClickRequest):
    data = JustPredict(page_id=request.page_uuid.split('/')[1],
                        x=request.coordinates.x,
                        y=request.coordinates.y)
    return await control.predict(post_details=data)


# 3. Route for API calls
prod_routes = [
    Route("/", endpoint=version, methods=["GET"]),
    APIRoute(
        "/save_click_and_predict_cluster",
        endpoint=save_click_and_predict_cluster_api,
        methods=["POST"],
    ),
    APIRoute(
        "/predict_cluster",
        endpoint=predict_cluster_api,
        methods=["POST"],
    ),
    APIRoute(
        "/new_click",
        endpoint=save_click_and_predict_cluster_api,
        methods=["POST"],
    ),
    APIRoute(
        "/predict_click",
        endpoint=predict_cluster_api,
        methods=["POST"],
    ),
]

# 4. Server Instance
app = FastAPI(routes=prod_routes)

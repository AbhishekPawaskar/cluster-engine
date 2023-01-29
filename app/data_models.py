""" This module bears all the formats necessary of module communication using Data"""

from typing import List, Optional, Union
from pydantic import BaseModel

class TableStruct(BaseModel):
    """ For database table click_db"""
    id:str
    page:str
    x:float
    y:float

class Coordinates(BaseModel):
    """ For handling coordinates"""
    x: float
    y: float

class SubCordinates(BaseModel):
    """ For handling coordinates (any subclass operation)"""
    coordinates : Coordinates

class SavePredict(BaseModel):
    """ For handling inputs for controller - Save & Predict"""
    page_id:str
    x:float
    y:float

class JustPredict(BaseModel):
    """ For handling inputs for controller - Just Predict"""
    page_id:str
    x:float
    y:float

class SavePredictResponseData(BaseModel):
    """ For handling outputs of the controller - Save & Predict"""
    cluster_idx: Union[int, None] = None
    is_new: bool

class JustPredictResponseData(BaseModel):
    """ For handling outputs of the controller - Just Predict"""
    cluster_idx: Union[int, None] = None


class NewClickRequest(BaseModel):
    coordinates: Coordinates 
    page_uuid: str


class NewClickResponse(BaseModel):
    cluster_idx: int
    is_new: bool


class PredictClickResponse(BaseModel):
    cluster_idx: Optional[int]


class Cluster(BaseModel):
    cluster_idx: int
    all_coordinates: List[Coordinates]


class GetBestClusterRequest(BaseModel):
    page_uuid: str


class GetBestClusterResponse(BaseModel):
    cluster: Cluster

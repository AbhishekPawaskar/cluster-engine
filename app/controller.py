"""This module is the main controller handling the operations related to database, redis, clustering and result generation."""

import sys
import logging
import json
from uuid import uuid4
from sqlalchemy.orm import Session
from data_models import SavePredict,JustPredict,SavePredictResponseData, JustPredictResponseData, TableStruct
from transaction.crud import create_record
from solution.cluster_control import ClusterController

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s] [%(asctime)s.%(msecs)-3d] [api] [%(filename)s:%(funcName)s] [%(message)s]",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    stream=sys.stdout,
                    force=True)


class Controller:
    def __init__(self):
        """
        This Class is the manifestation of the controller to handle all the operations.
        
        Key Methods:
        1. save_and_predict(post_details, db)
        2. predict(post_details)
        """
        try:
            self.cluster_controller = ClusterController()
    
        except Exception as init_ERR:
            logging.error('INITIALIZATION ERROR',exc_info=init_ERR)
    
    async def save_and_predict(self, post_details:SavePredict, db:Session):
        """ Saves the record in DataBase & Looks for Prabable cluster OR Cluster Creation"""
        try:
            
            #record creation
            page_id = post_details.page_id
            cordinates = [post_details.x, post_details.y]
            post_data = TableStruct(id=uuid4().__str__(), page=post_details.page_id,x=post_details.x,y=post_details.y)
            click_id = await create_record(db=db,post=post_data)


            if click_id != None:
                #cluster search
                cluster_found_ack, cluster_node_id = await self.cluster_controller.find_cluster(page_id=page_id,points=cordinates)
                if cluster_found_ack == True:
                    cluster_index = await self.cluster_controller.find_cluster_index(page_id=page_id,click_id=cluster_node_id)
                    return json.dumps(SavePredictResponseData(cluster_idx=int(cluster_index),is_new=False).__dict__)
                else:
                    #cluster creation
                    cluster_create_ack = await self.cluster_controller.create_cluster(page_id=page_id,click_id=click_id,points=cordinates)
                    logging.info("CLUSTER CREATION STATUS: "+str(cluster_create_ack))
                    cluster_index = await self.cluster_controller.find_cluster_index(page_id=page_id,click_id=cluster_node_id)
                    return json.dumps(SavePredictResponseData(cluster_idx=int(cluster_index),is_new=True).__dict__)
    
        except Exception as init_ERR:
            logging.error('SAVE AND PREDICTION ERROR',exc_info=init_ERR)
            return json.dumps(SavePredictResponseData(cluster_idx=None,is_new=True).__dict__)

    async def predict(self, post_details:JustPredict):
        """ Looks for Prabable cluster OR Cluster Creation. No Database operation involved"""
        try:
            #cluster search
            page_id = post_details.page_id
            cordinates = [post_details.x, post_details.y]
            cluster_found_ack, cluster_node_id = await self.cluster_controller.find_cluster(page_id=page_id,points=cordinates)
            logging.info("CLUSTER FOUND STATUS: "+str(cluster_found_ack)+" FOR PAGE_ID:"+str(page_id))
            if cluster_found_ack == True:
                cluster_index = await self.cluster_controller.find_prediction_cluster_index(page_id=page_id,click_id=cluster_node_id)
                return json.dumps(JustPredictResponseData(cluster_idx=int(cluster_index)).__dict__)
            else:
                return json.dumps(JustPredictResponseData(cluster_idx=None).__dict__)

    
        except Exception as init_ERR:
            logging.error('PREDICTION ERROR',exc_info=init_ERR)
            return json.dumps(JustPredictResponseData(cluster_idx=None).__dict__)
 

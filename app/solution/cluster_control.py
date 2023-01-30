"""This module is handles all the operations related to cluster related operations"""

import os
import sys
import logging
import ast
import numpy as np
import scipy
from redis_control.redis_client import RedisClient

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s] [%(asctime)s.%(msecs)-3d] [api] [%(filename)s:%(funcName)s] [%(message)s]",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    stream=sys.stdout,
                    force=True)


class ClusterController:
    def __init__(self):
        """
        This Class is the manifestation of the cluster controller to handle all cluster operations.
        
        Key Methods:
        1. create_cluster(page_id:str, click_id:str, points:list)
        2. find_cluster(page_id:str, points:list)
        3. find_cluster_index(page_id:str, click_id:str)
        4. find_prediction_cluster_index(page_id:str, click_id:str)

        Helper Methods:
        1. retrieve_cluster_node_list(page_id:str)
        2. add_cluster_node_list(page_id:str, click_id:str)
        3. add_cluster_points(page_id:str, click_id:str, points:float)
        4. retrieve_cluster_points_dict(cluster_node_list:list, page_id:str)
        5. retrive_point(key:str)
        6. prepare_array(point_dict:dict, reference_point:list)
        7. compute_distances(reference_array:np.array, points_array:np.array)
        """
        try:
            self.redis_controller = RedisClient()
            self.node_list_key_prefix = 'nodes:page:'
            self.cluster_point_list_key_prefix1 = 'page:'
            self.cluster_point_list_key_prefix2 = 'point:'
            self.cluster_threshold = float(os.getenv("CLUSTER_THRESHOLD"))
        except Exception as init_ERR:
            logging.error('INITIALIZATION ERROR',exc_info=init_ERR)
        
    async def retrieve_cluster_node_list(self, page_id:str) -> list:
        """retrives any cluster nodes for the page"""
        try:
            cluster_points = []
            key = self.node_list_key_prefix+str(page_id)
            cluster_points_list = self.redis_controller.client.get(name=key)
            if (cluster_points_list != None) and (cluster_points_list != '[]') and (cluster_points_list != []):
                cluster_points = ast.literal_eval(cluster_points_list)
                return cluster_points
            else:
                return cluster_points

        except Exception as init_ERR:
            logging.error('CLUSTER NODE LIST RETRIVAL ERROR',exc_info=init_ERR)
            cluster_points = []
            return cluster_points
    
    async def add_cluster_node_list(self, page_id:str, click_id:str) -> bool:
        """adds cluster nodes for the page"""
        try:
            cluster_points = await self.retrieve_cluster_node_list(page_id=page_id)
            key = self.node_list_key_prefix+str(page_id)
            if (cluster_points != None) and (cluster_points != []):
                cluster_points.append(click_id)
                stringified_cluster_points_list = str(cluster_points)
                upload_ack = self.redis_controller.client.set(name=key,value=stringified_cluster_points_list)
                if upload_ack == True:
                    return True
                else:
                    return False
            else:
                cluster_points_list = [click_id]
                stringified_cluster_points_list = str(cluster_points_list)
                upload_ack = self.redis_controller.client.set(name=key,value=stringified_cluster_points_list)
                if upload_ack == True:
                    return True
                else:
                    return False
                

        except Exception as init_ERR:
            logging.error('ADD CLUSTER NODE ERROR',exc_info=init_ERR)
            return False
    
    async def add_cluster_points(self, page_id:str, click_id:str, points:float) -> bool:
        """adds cluster node points for the page"""
        try:
            key = self.cluster_point_list_key_prefix1+str(page_id)+self.cluster_point_list_key_prefix2+str(click_id)
            points_value = str(points)
            upload_ack =  self.redis_controller.client.set(name=key, value=points_value)
            if upload_ack == True:
                return True
            else:
                return False
        except Exception as init_ERR:
            logging.error('CLUSTER ADDITION ERROR',exc_info=init_ERR)
            return False
    
    async def retrieve_cluster_points_dict(self, cluster_node_list:list, page_id:str) -> dict:
        """retrives any cluster node points for the cluster nodes"""
        try:
            cluster_points_dict = {}
            if cluster_node_list != []:
                for node in cluster_node_list:
                    key = self.cluster_point_list_key_prefix1+str(page_id)+self.cluster_point_list_key_prefix2+str(node)
                    points = await self.retrive_point(key=key)
                    if points != None:
                        cluster_points_dict[str(node)] = points
                    else:
                        continue       
            else:
                return cluster_points_dict
                
        except Exception as init_ERR:
            logging.error('CLUSTER RETRIVAL ERROR',exc_info=init_ERR)
            cluster_points_dict = {}
            return cluster_points_dict
    
    async def retrive_point(self,key:str):
        """retrives any cluster node's coordinates for the page"""
        try:
            points = self.redis_controller.client.get(name=key)
            if (points != None) and (points != []) and (points != '[]'):
                point_list = ast.literal_eval(points)
                return point_list
            else:
                return None
        except Exception as init_ERR:
            logging.error('POINT RETRIVAL ERROR',exc_info=init_ERR)
            return None
    
    async def prepare_array(self, point_dict:dict, reference_point:list):
        """prepares the points of cluster nodes of the page for distance calculations"""
        try:
            reference = [reference_point]
            point_list = []
            key_list = list(point_dict.keys())
            if key_list != []:
                for keys in key_list:
                    point_list.append(point_dict[keys])
                final_array = np.array(point_list)
                final_reference = np.array(reference)
                return final_reference, final_array
            else:
                None, None
        except Exception as init_ERR:
            logging.error('ARRAY PREPARATION ERROR',exc_info=init_ERR)
            return None, None

    async def compute_distances(self, reference_array:np.array, points_array:np.array) -> list:
        """computes distance between query point & cluster noe points"""
        try:
            distances = []
            distance_array = scipy.spatial.distance.cdist(reference_array,points_array,metric='cosine')
            distances = list(distance_array[:,0])
            return distances
        
        except Exception as init_ERR:
            logging.error('DISTANCE COMPUTE ERROR',exc_info=init_ERR)
            distances = []
            return distances
    
    async def find_cluster_index(self, page_id:str, click_id:str):
        """finds the cluster id"""
        try:
            node_list = await self.retrieve_cluster_node_list(page_id=page_id)
            if node_list == []:
                return int(0)
            else:
                index = node_list.index(click_id)
                return int(index)
    
        except Exception as init_ERR:
            return int(0)
    
    async def find_prediction_cluster_index(self, page_id:str, click_id:str):
        """finds the cluster id for 'just predict' computation"""
        try:
            node_list = await self.retrieve_cluster_node_list(page_id=page_id)
            if node_list == []:
                return None
            else:
                index = node_list.index(click_id)
                return int(index)
    
        except Exception as init_ERR:
            return None
    
    async def create_cluster(self, page_id:str, click_id:str, points:list) -> bool:
        """creates new cluster"""
        try:
            node_ack = await self.add_cluster_node_list(page_id=page_id,click_id=click_id)
            point_ack = await self.add_cluster_points(page_id=page_id,click_id=click_id, points=points)
            if node_ack and point_ack:
                return True
            else:
                return False
        except Exception as init_ERR:
            logging.error('CLUSTER CREATION ERROR',exc_info=init_ERR)
            return False
    
    async def find_cluster(self, page_id:str, points:list):
        """searches for suitable cluster nodes for the page"""
        try:
            node_list = await self.retrieve_cluster_node_list(page_id=page_id)
            if node_list == []:
                return False, None
            else:
                points_dict = await self.retrieve_cluster_points_dict(cluster_node_list=node_list,page_id=page_id)
                if (points_dict != {}) and (points_dict != None):
                    final_reference, final_array = await self.prepare_array(point_dict=points_dict,reference_point=points)
                    if (final_reference != None) and (final_array != None):
                        distances = await self.compute_distances(reference_array=final_reference, points_array=final_array)
                        if distances != []:
                            arrayed_distance = np.array(distances)
                            thresholded_distances = np.where(arrayed_distance >= self.cluster_threshold, 0, 1)
                            filtered_distances = list(thresholded_distances[:,0])
                            id_key_list = list(points_dict.keys())
                            if int(0) in filtered_distances:
                                cluster_index = np.argmin(distances)
                                result_node = id_key_list[cluster_index]
                                return True, result_node

                            else:
                                return False, None

                        else:
                            return False, None
                    
                    else:
                        return False, None

                else:
                    return False, None

        except Exception as init_ERR:
            logging.error('FIND CLUSTER ERROR',exc_info=init_ERR)
            return False, None
    
    
    
        


            
    

    
    
    
    

    

    






    
        
            
"""This module is handles all the operations related to cluster related operations"""

import os
import sys
import logging
from redis import Redis

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s] [%(asctime)s.%(msecs)-3d] [api] [%(filename)s:%(funcName)s] [%(message)s]",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    stream=sys.stdout,
                    force=True)


class RedisClient:
    def __init__(self):
        """
        This Class is the manifestation of the redis client to handle all redis operations.
        
        Key Methods:
        1. establish_connection()
        2. close_connection()
        3. stabilise_connection()

        Helper Methods:
        1. check_connection()
        """
        try:
            self.redis_host = os.getenv("REDIS_HOST")
            self.redis_port = int(os.getenv("REDIS_PORT"))
            self.redis_db_value = int(os.getenv("REDIS_DB_VALUE"))
            self.connect_retry_value = int(os.getenv("CONNECT_RETRY_VALUE"))
            connection_ack = self.establish_connection()
            logging.info("CONNECTION STATUS: "+str(connection_ack))

        except Exception as init_ERR:
            logging.error('INITIALIZATION ERROR',exc_info=init_ERR)

    def establish_connection(self) -> bool:
        """ Establishes New connection"""
        try:
            self.client = Redis(host=self.redis_host, 
                                port=self.redis_port, 
                                db=self.redis_db_value, 
                                charset='utf-8', 
                                decode_responses=True)
            return True
        except Exception as connect_ERR:
            logging.error('CONNECTION FAILED TO ESTABLISH',exc_info=connect_ERR)
            return False
    
    def check_connection(self) -> bool:
        """ Checks existing connection"""
        try:
            connection_ack = self.client.ping()
            if connection_ack == True:
                return True
            else:
                return False
        except Exception as connect_ERR:
            logging.error('CONNECTION ERROR',exc_info=connect_ERR)
            return False
    
    def close_connection(self) -> bool:
        """ Closes existing connection"""
        try:
            self.client.close()
            logging.info('CONNECTION TO REDIS CLOSED')
            return True
        except Exception as connect_ERR:
            logging.error('CONNECTION ERROR',exc_info=connect_ERR)
            return False
    
    def stabilise_connection(self) -> bool:
        """ Checks status of existing connections & takes necessary steps to manage connection"""
        try:
            connection_status = self.check_connection()
            if connection_status == True:
                return True
            else:
                retry_count = self.connect_retry_value
                for trial in range(0, retry_count):
                    retry_status = self.establish_connection()
                    if retry_status == False:
                        continue
                    elif retry_status == True:
                        logging.debug('CONNECTED AFTER '+str(trial)+' TRIES')
                        return True
                    else:
                        logging.debug('FAILED '+str(trial)+'th ATTEMPT')
                        return False
                
                logging.debug('FAILED TO CONNECT AFTER '+str(trial)+' TRIES')
                return False

        except Exception as connect_ERR:
            logging.error('CONNECTION ERROR',exc_info=connect_ERR)
            return False
        
            
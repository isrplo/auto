#!/usr/bin/env python

import logging
import socket
import time
import sys
import yaml
import broadlink


class Broadlinkconnector:
    __instance = None

    def __init__(self):
        if Broadlinkconnector.__instance is not None:
            return
        devices = {}
        remotes = {}
        gotActictiveConnections = False
        Broadlinkconnector.__instance = self
        self.init('config.yaml')


    @staticmethod
    def getInstance():
        if Broadlinkconnector.__instance is None:
            Broadlinkconnector()
        return Broadlinkconnector.__instance

    def setLogger(self,logger):
        self.logger = logger

    def init(self,configFileName):

        logger = logging.getLogger(__name__)

        with open(configFileName, 'r') as stream:
            config = yaml.load(stream)
        devices={}
        gotActictiveConnections=False
        self.remotes = config['remotes']

        for dev in config['devices'].keys():
            name = dev
            devices[name] = {}
            devices[name]['isConnected'] = False
            ip = config['devices'][dev].get('ip',None)
            mac = bytearray.fromhex("b4430fffffff")#dev.get('mac',None)
            devices[name]['link'] = broadlink.rm(host=(ip, 80), mac=mac)
            logger.info("Connecting to Broadlink: device {} on ip {}".format(name,ip))
            try:
                devices[name]['link'].auth()
            except socket.timeout:
                logger.error("Connection timeout")
                continue
            except:
                logger.fatal(sys.exc_info()[0])


            devices[name]['isConnected'] = True
            gotActictiveConnections = True
            time.sleep(1)
            logger.info("Connected to "+name)

        self.devices = devices
        self.gotActictiveConnections = gotActictiveConnections
        self.urls = config.get('urls',None)


    def execute(self, remote, operation):
        logger=logging.getLogger(__name__)

        rem = self.remotes.get(remote,None)
        if rem is None:
            logger.error("remote {} does not exist".format(remote))
            return

        devName=rem.get('device',None)
        device=self.devices[devName]
        op_hex = rem['oplist'].get(operation,None)

        if op_hex is None:
            logger.error("operation {} does not exist in remote {} in device {}".format(operation, remote, devName))
            return

        if not device['isConnected']:
            logger.error("Cant execute command, device {} is not connected".format(devName))
            return

        device['link'].send_data(op_hex.decode('hex'))
        logger.info("Command {} executes successfully".format(operation))

    def gotactictiveconnections(self):
        return self.gotActictiveConnections
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

        for dev in config['devices'].keys():
            name = dev
            devices[name] = {}
            devices[name]['isConnected'] = False
            ip = config['devices'][dev].get('ip',None)
            mac = bytearray.fromhex("b4430fffffff")#dev.get('mac',None)
            devices[name]['connection'] = broadlink.rm(host=(ip, 80), mac=mac)
            logger.info("Connecting to Broadlink: device {} on ip {}".format(name,ip))
            devices[name]['remotes']=config['devices'][name]['remotes']
            try:
                devices[name]['connection'].auth()
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

    def execute(self, device, remote, operation):
        logger=logging.getLogger(__name__)
        dev = self.devices.get(device,None)
        if dev is None:
            logger.error("device {} does not exist".format(device))
            return
        rem = dev['remotes'].get(remote,None)
        if rem is None:
            logger.error("remote {} does not exist in device {}".format(remote, device))
            return
        op_hex = rem['oplist'].get(operation,None)
        if op_hex is None:
            logger.error("operation {} does not exist in remote {} in device {}".format(operation, remote, device))
            return

        if not dev['isConnected']:
            logger.error("Cant execute command, device {} is not connected".format(device))
            return

        dev['connection'].send_data(op_hex.decode('hex'))
        logger.info("Command {} executes successfully".format(operation))

    def gotactictiveconnections(self):
        return self.gotActictiveConnections
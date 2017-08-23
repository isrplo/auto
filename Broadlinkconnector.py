#!/usr/bin/env python

import logging
import socket
import time
import sys
import yaml
import broadlink


class Broadlinkconnector:

    __instance = None
    logger = None
    remotes = {}
    devices = {}

    def __init__(self):
        if Broadlinkconnector.__instance is not None:
            return
        self.devices = {}
        self.remotes = {}
        self.gotActictiveConnections = False
        self.logger = logging.getLogger(__name__)
        self.init('config.yaml')
        Broadlinkconnector.__instance = self


    @staticmethod
    def getInstance():
        if Broadlinkconnector.__instance is None:
            Broadlinkconnector()
        return Broadlinkconnector.__instance

    def setLogger(self,logger):
        self.logger = logger

    def init(self,configFileName):

        with open(configFileName, 'r') as stream:
            config = yaml.load(stream)
        self.devices = config['devices']
        self.remotes = config['remotes']

        for devName in config['devices'].keys():
            self.devices[devName]['isConnected'] = False
            ip = self.devices[devName].get('ip',None)
            mac = bytearray.fromhex("b4430fffffff")#dev.get('mac',None)
            self.devices[devName]['link'] = broadlink.rm(host=(ip, 80), mac=mac)
            self.logger.info("Connecting to Broadlink device: {} on ip: {}".format(devName,ip))
            try:
                self.devices[devName]['link'].auth()
            except socket.timeout:
                self.logger.error("Connection timeout: " + devName)
                continue
            except:
                self.logger.fatal(sys.exc_info()[0])

            self.devices[devName]['isConnected'] = True
            gotActictiveConnections = True
            time.sleep(1)
            self.logger.info("Connected to device: "+devName)

        self.gotActictiveConnections = gotActictiveConnections
        self.urls = config.get('urls',None)


    def execute(self, remote, operation):

        rem = self.remotes.get(remote,None)
        if rem is None:
            self.logger.error("remote {} does not exist".format(remote))
            return

        devName=rem.get('device',None)
        device=self.devices[devName]
        op_hex = rem['oplist'].get(operation,None)

        if op_hex is None:
            self.logger.error("operation {} does not exist in remote {} in device {}".format(operation, remote, devName))
            return

        if not device['isConnected']:
            self.logger.error("Cant execute command, device {} is not connected".format(devName))
            return

        device['link'].send_data(op_hex.decode('hex'))
        self.logger.info("Command: {} executed successfully on remote: {} device: {}".format(operation,remote, devName))

    def gotactictiveconnections(self):
        return self.gotActictiveConnections
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
    scenarios = {}

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
        self.scenarios = config['scenarios']

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
            self.logger.error("operation {} does not exist for remote {} in device {}".format(operation, remote, devName))
            return

        if not device['isConnected']:
            self.logger.error("Cant execute command, device {} is not connected".format(devName))
            return

        device['link'].send_data(op_hex.decode('hex'))
        self.logger.info("Command: {} executed successfully on remote: {} device: {}".format(operation,remote, devName))

    def gotactictiveconnections(self):
        return self.gotActictiveConnections

    def playScenario(self, scenarioName):
        scenario = self.scenarios.get(scenarioName,None)
        if scenario is None:
            self.logger.error("Scenarion {} not defined".format(scenarioName))
            return

        self.logger.info("going to play scenario {}".format(scenarioName))
        actionList=scenario.get('actions',None)
        for action in actionList:
            command = action.split(',')
            if command[0].lower() == 'execute'.lower():
                arg1 = command[1]
                arg2 = command[2]
                self.execute(arg1,arg2)
            elif command[0].lower() == 'delay'.lower():
                arg1=command[1]
                self.logger.info("sleeping {} seconds".format(arg1))
                time.sleep(int(arg1))
            else:
                self.logger.error('Action: {} is not supported'.format(command[0]))

        self.logger.info("Scenario: {} completed".format(scenarioName))

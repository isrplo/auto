import json
import logging

import web
from Broadlinkconnector import Broadlinkconnector


FORMAT = '%(asctime)-15s: %(name)-8s: %(levelname)s: %(message)s'
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('broadlinkConnector.log')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

#Broadlinkconnector.getInstance()
#bc.init('config.yaml')
Broadlinkconnector.getInstance().playScenario('maser_bedroom_shades_up')

url=('(.*)', 'perform_op')

app = web.application(url, globals())

#if __name__ == "__main__":
#    app.run()


class perform_op:

    def GET(self,url):
        if web.data():
            data = json.loads(web.data())
            remote = data['remote']
            operation = data['operation']
            Broadlinkconnector.getInstance().execute(device,remote,operation)
        return 'OK'
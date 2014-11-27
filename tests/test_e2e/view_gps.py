#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from time import sleep

from sanji.core import Sanji
from sanji.connection.mqtt import Mqtt


REQ_RESOURCE = "/system/gps"
MANUAL_TEST = 0


class View(Sanji):

    # This function will be executed after registered.
    def run(self):

        for count in xrange(0, 100, 1):
            # Normal CRUD Operation
            #   self.publish.[get, put, delete, post](...)
            # One-to-One Messaging
            #   self.publish.direct.[get, put, delete, post](...)
            #   (if block=True return Message, else return mqtt mid number)
            # Agruments
            #   (resource[, data=None, block=True, timeout=60])

            # case 1: test GET
            print "GET %s" % REQ_RESOURCE
            res = self.publish.get(REQ_RESOURCE)
            if res.code != 200:
                print "GET supported, code 200 is expected"
                print res.to_json()
                self.stop()
            if 1 == MANUAL_TEST:
                var = raw_input("Please enter any key to continue...")

            # case 2: test PUT with no data
            sleep(2)
            print "PUT %s" % REQ_RESOURCE
            res = self.publish.put(REQ_RESOURCE, None)
            if res.code != 400 and res.code != 500:
                print "data is required, code 400 is expected"
                print res.to_json()
                self.stop()
            if 1 == MANUAL_TEST:
                var = raw_input("Please enter any key to continue...")

            # case 3: test PUT with empty data
            sleep(2)
            print "PUT %s" % REQ_RESOURCE
            res = self.publish.put(REQ_RESOURCE, data={})
            if res.code != 400 and res.code != 500:
                print "data.lat and data.lon are required, code 400 is " \
                      "expected"
                print res.to_json()
                self.stop()
            if 1 == MANUAL_TEST:
                var = raw_input("Please enter any key to continue...")

            # case 4: test PUT with lon & lat
            sleep(2)
            print "PUT %s" % REQ_RESOURCE
            res = self.publish.put(REQ_RESOURCE, data={"lat": 0.0, "lon": 0.0})
            if res.code != 200:
                print "PUT data with lat and lon should reply code 200"
                print res.to_json()
                self.stop()
            if 1 == MANUAL_TEST:
                print var

            # stop the test view
            self.stop()


if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("GPS")

    view = View(connection=Mqtt())
    view.start()

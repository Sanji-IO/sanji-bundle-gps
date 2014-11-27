#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import logging
import unittest

from mock import patch
from sanji.connection.mockup import Mockup
from sanji.message import Message

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
    from gps import Gps
except ImportError as e:
    print os.path.dirname(os.path.realpath(__file__)) + "/../"
    print sys.path
    print e
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)

dirpath = os.path.dirname(os.path.realpath(__file__))


class TestGpsClass(unittest.TestCase):

    def setUp(self):
        self.gps = Gps(connection=Mockup())

    def tearDown(self):
        self.gps.stop()
        self.gps = None
        try:
            os.remove("%s/data/gps.json" % dirpath)
        except OSError:
            pass

        try:
            os.remove("%s/data/gps.backup.json" % dirpath)
        except OSError:
            pass

    def test_init(self):
        # case 1: no configuration file
        with self.assertRaises(IOError):
            with patch("gps.ModelInitiator") as mock_modelinit:
                mock_modelinit.side_effect = IOError
                self.gps.init()

    def test_load(self):
        # case 1: load current configuration
        self.gps.load(dirpath)
        self.assertEqual(0, self.gps.model.db["lat"])
        self.assertEqual(0, self.gps.model.db["lon"])

        os.remove("%s/data/gps.json" % dirpath)

        # case 2: load backup configuration
        self.gps.load(dirpath)
        self.assertEqual(0, self.gps.model.db["lat"])
        self.assertEqual(0, self.gps.model.db["lon"])

        os.remove("%s/data/gps.json" % dirpath)
        os.remove("%s/data/gps.backup.json" % dirpath)

        # case 3: cannot load any configuration
        with self.assertRaises(IOError):
            self.gps.load("%s/mock" % dirpath)

    def test_save(self):
        # Already tested in init()
        pass

    def test_get(self):
        message = Message({"data": {}, "query": {}, "param": {}})

        # case 1: get current location
        def resp(code=200, data=None):
            self.assertEqual(200, code)
            self.assertEqual(0, data["lat"])
            self.assertEqual(0, data["lon"])
        self.gps.get(message=message, response=resp, test=True)

    def test_put(self):
        message = Message({"query": {}, "param": {}})

        # case 1: no data attribute
        def resp1(code=200, data=None):
            self.assertEqual(400, code)
            self.assertEqual(data, {"message": "Invalid input."})
        self.gps.put(message, response=resp1, test=True)

        # case 2: invalid json schema
        def resp2(code=200, data=None):
            self.assertEqual(400, code)
        message = Message({"data": [], "query": {}, "param": {}})
        self.gps.put(message, response=resp2, test=True)

        message = Message({"data": {}, "query": {}, "param": {}})
        self.gps.put(message, response=resp2, test=True)

        message.data["lat"] = 0
        self.gps.put(message, response=resp2, test=True)

        # case 3: put successfully
        def resp3(code=200, data=None):
            self.assertEqual(200, code)
            self.assertEqual(1.12345, data["lat"])
            self.assertEqual(2.23456, data["lon"])
        message = Message({"data": {}, "query": {}, "param": {}})
        message.data["lat"] = 1.12345
        message.data["lon"] = 2.23456
        self.gps.put(message, response=resp3, test=True)

        message = Message({"data": {}, "query": {}, "param": {}})
        self.gps.get(message, response=resp3, test=True)

if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=20, format=FORMAT)
    logger = logging.getLogger("GPS Test")
    unittest.main()

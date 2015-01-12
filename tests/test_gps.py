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
        self.name = "gps"
        self.bundle = Gps(connection=Mockup())

    def tearDown(self):
        self.bundle.stop()
        self.bundle = None
        try:
            os.remove("%s/data/%s.json" % (dirpath, self.name))
        except OSError:
            pass

        try:
            os.remove("%s/data/%s.json.backup" % (dirpath, self.name))
        except OSError:
            pass

    def test__init__no_conf(self):
        """
        init: no configuration file
        """
        with self.assertRaises(IOError):
            with patch("gps.ModelInitiator") as mock_modelinit:
                mock_modelinit.side_effect = IOError
                self.bundle.init()

    def test__load__current_conf(self):
        """
        load: load current configuration
        """
        self.bundle.load(dirpath)
        self.assertEqual(0, self.bundle.model.db["lat"])
        self.assertEqual(0, self.bundle.model.db["lon"])

    def test__load__backup_conf(self):
        """
        load: load backup configuration
        """
        os.remove("%s/data/%s.json" % (dirpath, self.name))
        self.bundle.load(dirpath)
        self.assertEqual(0, self.bundle.model.db["lat"])
        self.assertEqual(0, self.bundle.model.db["lon"])

    def test__load__no_conf(self):
        """
        load: cannot load any configuration
        """
        with self.assertRaises(IOError):
            self.bundle.load("%s/mock" % dirpath)

    def test__save(self):
        """
        save: tested in init()
        """
        # Already tested in init()
        pass

    def test__get(self):
        """
        get (/system/gps): get current location
        """
        message = Message({"data": {}, "query": {}, "param": {}})

        def resp(code=200, data=None):
            self.assertEqual(200, code)
            self.assertEqual(0, data["lat"])
            self.assertEqual(0, data["lon"])
        self.bundle.get(message=message, response=resp, test=True)

    def test__put__no_data(self):
        """
        put (/system/gps): no data attribute
        """
        message = Message({"query": {}, "param": {}})

        def resp(code=200, data=None):
            self.assertEqual(400, code)
            self.assertEqual(data, {"message": "Invalid input."})
        self.bundle.put(message, response=resp, test=True)

    def test__put__invalid_json1(self):
        """
        put (/system/gps): invalid json schema, data cannot be an array
        """
        message = Message({"data": [], "query": {}, "param": {}})

        def resp(code=200, data=None):
            self.assertEqual(400, code)
        self.bundle.put(message, response=resp, test=True)

    def test__put__invalid_json2(self):
        """
        put (/system/gps): invalid json schema, data cannot be an empty dict
        """
        message = Message({"data": {}, "query": {}, "param": {}})

        def resp(code=200, data=None):
            self.assertEqual(400, code)
        self.bundle.put(message, response=resp, test=True)

    def test__put__invalid_json3(self):
        """
        put (/system/gps): invalid json schema, invalid value
        """
        message = Message({"data": {}, "query": {}, "param": {}})
        message.data["lat"] = 0

        def resp(code=200, data=None):
            self.assertEqual(400, code)
        self.bundle.put(message, response=resp, test=True)

    def test__put(self):
        """
        put (/system/gps)
        """
        message = Message({"data": {}, "query": {}, "param": {}})
        message.data["lat"] = 1.12345
        message.data["lon"] = 2.23456

        def resp(code=200, data=None):
            self.assertEqual(200, code)
            self.assertEqual(1.12345, data["lat"])
            self.assertEqual(2.23456, data["lon"])
        self.bundle.put(message, response=resp, test=True)

        message = Message({"data": {}, "query": {}, "param": {}})
        self.bundle.get(message, response=resp, test=True)


if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=20, format=FORMAT)
    logger = logging.getLogger("GPS Test")
    unittest.main()

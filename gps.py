#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import logging
from sanji.core import Sanji
from sanji.core import Route
from sanji.connection.mqtt import Mqtt
from sanji.model_initiator import ModelInitiator
from voluptuous import Schema
from voluptuous import Any, Extra


# TODO: logger should be defined in sanji package?
logger = logging.getLogger()


class Gps(Sanji):
    """
    A model to handle GPS configuration.

    Attributes:
        model: GPS' database with json format.
    """
    def init(self, *args, **kwargs):
        try:  # pragma: no cover
            bundle_env = kwargs["bundle_env"]
        except KeyError:
            bundle_env = os.getenv("BUNDLE_ENV", "debug")

        path_root = os.path.abspath(os.path.dirname(__file__))
        if bundle_env == "debug":  # pragma: no cover
            path_root = "%s/tests" % path_root

        try:
            self.load(path_root)
        except:
            self.stop()
            raise IOError("Cannot load any configuration.")

    def load(self, path):
        """
        Load the configuration. If configuration is not installed yet,
        initialise them with default value.

        Args:
            path: Path for the bundle, the configuration should be located
                under "data" directory.
        """
        self.model = ModelInitiator("gps", path, backup_interval=-1)
        if not self.model.db:
            raise IOError("Cannot load any configuration.")
        self.save()

    def save(self):
        """
        Save and backup the configuration.
        """
        self.model.save_db()
        self.model.backup_db()

    @Route(methods="get", resource="/system/gps")
    def get(self, message, response):
        return response(data=self.model.db)

    put_schema = Schema({
        "lat": Any(int, float),
        "lon": Any(int, float),
        Extra: object
    }, required=True)

    @Route(methods="put", resource="/system/gps", schema=put_schema)
    def put(self, message, response):
        # TODO: should be removed when schema worked for unittest
        if not hasattr(message, "data"):
            return response(code=400,
                            data={"message": "Invalid input."})

        # TODO: should be removed when schema worked for unittest
        try:
            Gps.put_schema(message.data)
        except Exception as e:
            return response(code=400,
                            data={"message": "Invalid input: %s." % e})

        self.model.db["lat"] = message.data["lat"]
        self.model.db["lon"] = message.data["lon"]
        self.save()
        return response(data=self.model.db)


if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("GPS")

    gps = Gps(connection=Mqtt())
    gps.start()

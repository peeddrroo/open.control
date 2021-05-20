from __future__ import absolute_import
from .opencontrol import opencontrol


def create_instance(*a):
    return opencontrol(*a)

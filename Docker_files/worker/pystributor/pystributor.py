#!/usr/bin/python3

"""
Import wrapper for pystributor worker and hub
"""


from pystributor.pystributor_hub import Hub as _Hub
from pystributor.pystributor_worker import Worker as _Worker

Hub = _Hub
Worker = _Worker

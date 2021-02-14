"""Implements logger for application
"""
import os
import logging

from uvicorn.logging import ColourizedFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

standard = logging.StreamHandler()
standard.setLevel(logging.INFO)

formatter =  ColourizedFormatter('%(asctime)s - [%(levelname)s] : %(message)s')
standard.setFormatter(formatter)
logger.addHandler(standard)
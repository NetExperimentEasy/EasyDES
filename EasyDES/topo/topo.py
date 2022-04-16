import logging
from abc import abstractclassmethod, ABC
from ..node import ControllerNode, WorkerNode

class TopoBase(ABC):
    def __init__(self):
        super().__init__()
        
import logging
from abc import abstractclassmethod, ABC
from enum import Enum

class NodeBase(ABC):
    """
    Node base class 
    """
    def __init__(self) -> None:
        pass

class WorkerType(Enum):
    Switch = "switch"
    Router = "router"
    Server = "server"
    Client = "client"

class Worker(NodeBase):
    """
    Worker
    """ 
    def __init__(self, name, type) -> None:
        super().__init__()
        self.name = name
        self.type = WorkerType(type)

class Controller(NodeBase):
    """
    Controller
    """
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
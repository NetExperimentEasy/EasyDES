import logging
from abc import abstractclassmethod, ABC
from .mission import MissionManager

class NodeBase(ABC):
    """
    Node base class 
    """
    def __init__(self) -> None:
        pass


class WorkerNode(NodeBase, MissionManager):
    """
    Worker
    """ 
    def __init__(self) -> None:
        super().__init__()

class ControllerNode(NodeBase, MissionManager):
    """
    Controller
    """
    def __init__(self) -> None:
        super().__init__()
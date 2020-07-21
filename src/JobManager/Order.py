#! /usr/bin/env python
from enum import Enum

class OrderResponseStatus(Enum):
    """ Class that acts as Enumerator for Order Response status. """
    # 0 = SUCCES, 1 = ERROR
    SUCCES = 0
    ERROR = 1

class OrderKeyword(Enum):
    """ Class that acts as Enumerator for Order keywords. """
    TRANSPORT = 0
    MOVE = 1
    FOLLOW = 2

class OrderTypeArgCount:
    """ Class that acts as Constants for Order types and the number of arguments associated with them. """
    # Example incoming order: [transport, priority, from_location, to_location]
    # Example incoming order: [move, priority, to_location]
    # Example incoming order: [follow, priority, leader_id]
    TRANSPORT = 2
    MOVE = 1
    FOLLOW = 1
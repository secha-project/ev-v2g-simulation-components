# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

from __future__ import annotations
from typing import Any, Dict, Optional, Union

from tools.exceptions.messages import MessageError
from tools.messages import AbstractResultMessage


class GridStateMessage(AbstractResultMessage):
    """Description for the GridStateMessage class"""

    CLASS_MESSAGE_TYPE = "GridState"
    MESSAGE_TYPE_CHECK = True

    GRID_ID_ATTRIBUTE = "GridId"
    GRID_ID_PROPERTY = "grid_id"

    MAX_POWER_ATTRIBUTE = "MaxPower" 
    MAX_POWER_PROPERTY = "max_power" 

    CURRENT_POWER_ATTRIBUTE = "CurrentPower" 
    CURRENT_POWER_PROPERTY = "current_power"  


    # all attributes specific that are added to the AbstractResult should be introduced here
    MESSAGE_ATTRIBUTES = {
        GRID_ID_ATTRIBUTE: GRID_ID_PROPERTY,
        MAX_POWER_ATTRIBUTE: MAX_POWER_PROPERTY,
        CURRENT_POWER_ATTRIBUTE: CURRENT_POWER_PROPERTY
    }
    # list all attributes that are optional here (use the JSON attribute names)
    OPTIONAL_ATTRIBUTES = []

    # all attributes that are using the Quantity block format should be listed here
    QUANTITY_BLOCK_ATTRIBUTES = {}

    # all attributes that are using the Quantity array block format should be listed here
    QUANTITY_ARRAY_BLOCK_ATTRIBUTES = {}

    # all attributes that are using the Time series block format should be listed here
    TIMESERIES_BLOCK_ATTRIBUTES = []

    # always include these definitions to update the full list of attributes to these class variables
    # no need to modify anything here
    MESSAGE_ATTRIBUTES_FULL = {
        **AbstractResultMessage.MESSAGE_ATTRIBUTES_FULL,
        **MESSAGE_ATTRIBUTES
    }
    OPTIONAL_ATTRIBUTES_FULL = AbstractResultMessage.OPTIONAL_ATTRIBUTES_FULL + OPTIONAL_ATTRIBUTES
    QUANTITY_BLOCK_ATTRIBUTES_FULL = {
        **AbstractResultMessage.QUANTITY_BLOCK_ATTRIBUTES_FULL,
        **QUANTITY_BLOCK_ATTRIBUTES
    }
    QUANTITY_ARRAY_BLOCK_ATTRIBUTES_FULL = {
        **AbstractResultMessage.QUANTITY_ARRAY_BLOCK_ATTRIBUTES_FULL,
        **QUANTITY_ARRAY_BLOCK_ATTRIBUTES
    }
    TIMESERIES_BLOCK_ATTRIBUTES_FULL = (
        AbstractResultMessage.TIMESERIES_BLOCK_ATTRIBUTES_FULL +
        TIMESERIES_BLOCK_ATTRIBUTES
    )

    # for each attributes added by this message type provide a property function to get the value of the attribute
    # the name of the properties must correspond to the names given in MESSAGE_ATTRIBUTES
    # template for one property:
    @property
    def grid_id(self) -> str:
        return self.__grid_id

    @property
    def max_power(self) -> float:
        return self.__max_power
    
    @property
    def current_power(self) -> float:
        return self.__current_power
    
    @grid_id.setter
    def grid_id(self, grid_id: str):
        self.__grid_id = grid_id

    @max_power.setter
    def max_power(self, max_power: Union[int, float]):
        self.__max_power = float(max_power)

    @current_power.setter
    def current_power(self, current_power: Union[int, float]):
        self.__current_power = float(current_power)

    def __eq__(self, other: Any) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, GridStateMessage) and
            self.grid_id == other.grid_id and
            self.max_power == other.max_power and
            self.current_power == other.current_power
        )

    @classmethod
    def _check_grid_id(cls, grid_id: str) -> bool:
        return isinstance(grid_id, str)

    @classmethod
    def _check_max_power(cls, max_power: Union[int, float]) -> bool:
        return isinstance(max_power, (int, float))
    
    @classmethod
    def _check_current_power(cls, current_power: Union[int, float]) -> bool:
        return isinstance(current_power, (int, float))

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Optional[GridStateMessage]:
        """TODO: description for the from_json method"""
        try:
            message_object = cls(**json_message)
            return message_object
        except (TypeError, ValueError, MessageError):
            return None


GridStateMessage.register_to_factory()

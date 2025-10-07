# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

from __future__ import annotations
from typing import Any, Dict, Optional, Union

from tools.exceptions.messages import MessageError, MessageValueError
from tools.messages import AbstractResultMessage


class UsedPowerValueToGridMessage(AbstractResultMessage):
    """Description for the UsedPowerValueToGridMessage class"""

    CLASS_MESSAGE_TYPE = "UsedPowerValueToGrid"
    MESSAGE_TYPE_CHECK = True

    USED_POWER_VALUE_ATTRIBUTE = "UsedPowerValue"
    USED_POWER_VALUE_PROPERTY = "used_power_value"

    TOTAL_POWER_VALUE_ATTRIBUTE = "TotalPowerValue"
    TOTAL_POWER_VALUE_PROPERTY = "total_power_value"

    # all attributes specific that are added to the AbstractResult should be introduced here
    MESSAGE_ATTRIBUTES = {
        USED_POWER_VALUE_ATTRIBUTE: USED_POWER_VALUE_PROPERTY,
        TOTAL_POWER_VALUE_ATTRIBUTE: TOTAL_POWER_VALUE_PROPERTY,
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
    def used_power_value(self) -> float:
        return self.__used_power_value

    @used_power_value.setter
    def used_power_value(self, used_power_value: Union[int, float]):
        self.__used_power_value = float(used_power_value)

    @property
    def total_power_value(self) -> float:
        return self.__total_power_value

    @total_power_value.setter
    def total_power_value(self, total_power_value: Union[int, float]):
        self.__total_power_value = float(total_power_value)

    def __eq__(self, other: Any) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, UsedPowerValueToGridMessage) and
            self.used_power_value == other.used_power_value and
            self.total_power_value == other.total_power_value
        )

    @classmethod
    def _check_used_power_value(cls, used_power_value: Union[int, float]) -> bool:
        return isinstance(used_power_value, (int, float))

    @classmethod
    def _check_total_power_value(cls, total_power_value: Union[int, float]) -> bool:
        return isinstance(total_power_value, (int, float))

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Optional[UsedPowerValueToGridMessage]:
        """TODO: description for the from_json method"""
        try:
            message_object = cls(**json_message)
            return message_object
        except (TypeError, ValueError, MessageError):
            return None


UsedPowerValueToGridMessage.register_to_factory()

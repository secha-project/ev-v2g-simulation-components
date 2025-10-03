# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

from __future__ import annotations
from typing import Any, Dict, Optional

from tools.exceptions.messages import MessageError, MessageValueError
from tools.messages import AbstractResultMessage


class TotalChargingCostMessage(AbstractResultMessage):
    """Description for the TotalChargingCostMessage class"""

    CLASS_MESSAGE_TYPE = "TotalChargingCost"
    MESSAGE_TYPE_CHECK = True

    TOTAL_CHARGING_COST_ATTRIBUTE = "TotalChargingCost"
    TOTAL_CHARGING_COST_PROPERTY = "total_charging_cost"

    USER_ID_ATTRIBUTE = "UserId"
    USER_ID_PROPERTY = "user_id"

    # all attributes specific that are added to the AbstractResult should be introduced here
    MESSAGE_ATTRIBUTES = {
        TOTAL_CHARGING_COST_ATTRIBUTE: TOTAL_CHARGING_COST_PROPERTY,
        USER_ID_ATTRIBUTE: USER_ID_PROPERTY
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
    def total_charging_cost(self) -> float:
        return self.__total_charging_cost
    
    @property
    def user_id(self) -> int:
        return self.__user_id

    @total_charging_cost.setter
    def total_charging_cost(self, total_charging_cost: float):
        self.__total_charging_cost = total_charging_cost

    @user_id.setter
    def user_id(self, user_id: int):
        if self._check_user_id(user_id):
            self.__user_id = user_id
        else:
            raise MessageValueError(f"Invalid value for UserId: {user_id}")

    def __eq__(self, other: Any) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, TotalChargingCostMessage) and
            self.total_charging_cost == other.total_charging_cost and
            self.user_id == other.user_id
        )

    @classmethod
    def _check_total_charging_cost(cls, total_charging_cost: float) -> bool:
        return isinstance(total_charging_cost, float)

    @classmethod
    def _check_user_id(cls, user_id: int) -> bool:
        return isinstance(user_id, int)

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Optional[TotalChargingCostMessage]:
        """TODO: description for the from_json method"""
        try:
            message_object = cls(**json_message)
            return message_object
        except (TypeError, ValueError, MessageError):
            return None


TotalChargingCostMessage.register_to_factory()

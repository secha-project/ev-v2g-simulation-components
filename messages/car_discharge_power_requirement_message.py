# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

from __future__ import annotations
from typing import Any, Dict, Optional

from tools.exceptions.messages import MessageError, MessageValueError
from tools.messages import AbstractResultMessage


class CarDischargePowerRequirementMessage(AbstractResultMessage):
    """Description for the CarDischargePowerRequirementMessage class - V2G controller to Station"""

    CLASS_MESSAGE_TYPE = "CarDischargePowerRequirement"
    MESSAGE_TYPE_CHECK = True

    POWER_ATTRIBUTE = "Power"
    POWER_PROPERTY = "power"

    STATION_ID_ATTRIBUTE = "StationId"
    STATION_ID_PROPERTY = "station_id"

    USER_ID_ATTRIBUTE = "UserId"
    USER_ID_PROPERTY = "user_id"

    # all attributes specific that are added to the AbstractResult should be introduced here
    MESSAGE_ATTRIBUTES = {
        POWER_ATTRIBUTE: POWER_PROPERTY,
        STATION_ID_ATTRIBUTE: STATION_ID_PROPERTY,
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
    def power(self) -> float:
        return self.__power

    @property
    def station_id(self) -> str:
        return self.__station_id

    @property
    def user_id(self) -> int:
        return self.__user_id

    @power.setter
    def power(self, power: float):
        self.__power = power

    @station_id.setter
    def station_id(self, station_id: str):
        self.__station_id = station_id

    @user_id.setter
    def user_id(self, user_id: int):
        if self._check_user_id(user_id):
            self.__user_id = user_id
        else:
            raise MessageValueError(f"Invalid value for UserId: {user_id}")

    def __eq__(self, other: Any) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, CarDischargePowerRequirementMessage) and
            self.power == other.power and
            self.station_id == other.station_id and
            self.user_id == other.user_id
        )


    @classmethod
    def _check_user_id(cls, user_id: int) -> bool:
        return isinstance(user_id, int)

    @classmethod
    def _check_power(cls, power: float) -> bool:
        return isinstance(power, float)

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Optional[CarDischargePowerRequirementMessage]:
        """TODO: description for the from_json method"""
        try:
            message_object = cls(**json_message)
            return message_object
        except (TypeError, ValueError, MessageError):
            return None


CarDischargePowerRequirementMessage.register_to_factory()

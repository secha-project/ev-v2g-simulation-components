# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

from __future__ import annotations
from typing import Any, Dict, Optional

from tools.exceptions.messages import MessageError, MessageValueError
from tools.messages import AbstractResultMessage

class UserStateMessage(AbstractResultMessage):
    CLASS_MESSAGE_TYPE = "UserState"
    MESSAGE_TYPE_CHECK = True

    USER_ID_ATTRIBUTE = "UserId"
    USER_ID_PROPERTY = "user_id"

    ARRIVAL_TIME_ATTRIBUTE = "ArrivalTime"
    ARRIVAL_TIME_PROPERTY = "arrival_time"

    TARGET_TIME_ATTRIBUTE = "TargetTime"
    TARGET_TIME_PROPERTY = "target_time"

    MESSAGE_ATTRIBUTES = {
        USER_ID_ATTRIBUTE: USER_ID_PROPERTY,
        TARGET_TIME_ATTRIBUTE: TARGET_TIME_PROPERTY,
        ARRIVAL_TIME_ATTRIBUTE: ARRIVAL_TIME_PROPERTY
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


    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def target_time(self) -> str:
        return self.__target_time

    @property
    def arrival_time(self) -> str:
        return self.__arrival_time

    @user_id.setter
    def user_id(self, user_id: int):
        if self._check_user_id(user_id):
            self.__user_id = user_id
        else:
            raise MessageValueError(f"Invalid value for UserId: {user_id}")

    @target_time.setter
    def target_time(self, target_time: str):
        if self._check_target_time(target_time):
            self.__target_time = target_time
        else:
            raise MessageValueError(f"Invalid value for TargetStateOfCharge: {target_time}")

    @arrival_time.setter
    def arrival_time(self, arrival_time: str):
        if self._check_arrival_time(arrival_time):
            self.__arrival_time = arrival_time
        else:
            raise MessageValueError(f"Invalid value for TargetStateOfCharge: {arrival_time}")

    def __eq__(self, other: Any) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, UserStateMessage) and
            self.user_id == other.user_id and
            self.target_time == other.target_time and
            self.arrival_time == other.arrival_time
        )

    @classmethod
    def _check_user_id(cls, user_id: int) -> bool:
        return isinstance(user_id, int)

    @classmethod
    def _check_target_time(cls, target_time: str) -> bool:
        return cls._check_datetime(target_time)

    @classmethod
    def _check_arrival_time(cls, arrival_time: str) -> bool:
        return cls._check_datetime(arrival_time)

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Optional[UserStateMessage]:
        try:
            message_object = cls(**json_message)
            return message_object
        except (TypeError, ValueError, MessageError):
            return None

UserStateMessage.register_to_factory()

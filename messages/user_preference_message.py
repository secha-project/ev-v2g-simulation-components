# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

from __future__ import annotations
from typing import Any, Dict, Optional

from tools.exceptions.messages import MessageError, MessageValueError
from tools.messages import AbstractResultMessage


class UserPreferenceMessage(AbstractResultMessage):
    CLASS_MESSAGE_TYPE = "UserPreference"
    MESSAGE_TYPE_CHECK = True

    USER_ID_ATTRIBUTE = "UserId"
    USER_ID_PROPERTY = "user_id"

    MINIMUM_SOC_ATTRIBUTE = "MinimumSOC"
    MINIMUM_SOC_PROPERTY = "minimum_soc"

    MAX_COST_FOR_CHARGING_ATTRIBUTE = "MaxCostForCharging"
    MAX_COST_FOR_CHARGING_PROPERTY = "max_cost_for_charging"

    DISCHARGE_PRICE_THRESHOLD_ATTRIBUTE = "DischargePriceThreshold"
    DISCHARGE_PRICE_THRESHOLD_PROPERTY = "discharge_price_threshold"

    MAXIMUM_SOC_ATTRIBUTE = "MaximumSOC"
    MAXIMUM_SOC_PROPERTY = "maximum_soc"

    # all attributes specific that are added to the AbstractResult should be introduced here
    MESSAGE_ATTRIBUTES = {
        USER_ID_ATTRIBUTE: USER_ID_PROPERTY,
        MINIMUM_SOC_ATTRIBUTE: MINIMUM_SOC_PROPERTY,
        MAX_COST_FOR_CHARGING_ATTRIBUTE: MAX_COST_FOR_CHARGING_PROPERTY,
        DISCHARGE_PRICE_THRESHOLD_ATTRIBUTE: DISCHARGE_PRICE_THRESHOLD_PROPERTY,
        MAXIMUM_SOC_ATTRIBUTE: MAXIMUM_SOC_PROPERTY
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
    def minimum_soc(self) -> float:
        return self.__minimum_soc

    @property
    def max_cost_for_charging(self) -> float:
        return self.__max_cost_for_charging

    @property
    def discharge_price_threshold(self) -> float:
        return self.__discharge_price_threshold

    @property
    def maximum_soc(self) -> float:
        return self.__maximum_soc

    @user_id.setter
    def user_id(self, user_id: int):
        if self._check_user_id(user_id):
            self.__user_id = user_id
        else:
            raise MessageValueError(f"Invalid value for UserId: {user_id}")

        
    @minimum_soc.setter
    def minimum_soc(self, minimum_soc: float):
        if self._check_minimum_soc(minimum_soc):
            self.__minimum_soc = minimum_soc
        else:
            raise MessageValueError(f"Invalid value for MinimumSOC: {minimum_soc}")
        
    @max_cost_for_charging.setter
    def max_cost_for_charging(self, max_cost_for_charging: float):
        if self._check_max_cost_for_charging(max_cost_for_charging):
            self.__max_cost_for_charging = max_cost_for_charging
        else:
            raise MessageValueError(f"Invalid value for MaxCostForCharging: {max_cost_for_charging}")
    
    @discharge_price_threshold.setter
    def discharge_price_threshold(self, discharge_price_threshold: float):
        if self._check_discharge_price_threshold(discharge_price_threshold):
            self.__discharge_price_threshold = discharge_price_threshold
        else:
            raise MessageValueError(f"Invalid value for DischargePriceThreshold: {discharge_price_threshold}")
    
    @maximum_soc.setter
    def maximum_soc(self, maximum_soc: float):
        if self._check_maximum_soc(maximum_soc):
            self.__maximum_soc = maximum_soc
        else:
            raise MessageValueError(f"Invalid value for MaximumSOC: {maximum_soc}")

    def __eq__(self, other: Any) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, UserPreferenceMessage) and
            self.user_id == other.user_id and
            self.minimum_soc == other.minimum_soc and
            self.max_cost_for_charging == other.max_cost_for_charging and
            self.discharge_price_threshold == other.discharge_price_threshold and
            self.maximum_soc == other.maximum_soc
        )

    @classmethod
    def _check_user_id(cls, user_id: int) -> bool:
        return isinstance(user_id, int)

    @classmethod
    def _check_minimum_soc(cls, minimum_soc: float) -> bool:
        return isinstance(minimum_soc, float)

    @classmethod
    def _check_max_cost_for_charging(cls, max_cost_for_charging: float) -> bool:
        return isinstance(max_cost_for_charging, float)

    @classmethod
    def _check_discharge_price_threshold(cls, discharge_price_threshold: float) -> bool:
        return isinstance(discharge_price_threshold, float)

    @classmethod
    def _check_maximum_soc(cls, maximum_soc: float) -> bool:
        return isinstance(maximum_soc, float)

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Optional[UserPreferenceMessage]:
        try:
            message_object = cls(**json_message)
            return message_object
        except (TypeError, ValueError, MessageError):
            return None

UserPreferenceMessage.register_to_factory()

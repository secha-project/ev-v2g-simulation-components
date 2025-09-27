# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

import asyncio
from typing import Any, cast, Union

from tools.components import AbstractSimulationComponent
from tools.exceptions.messages import MessageError
from tools.messages import BaseMessage
from tools.tools import FullLogger, load_environmental_variables, log_exception

from messages.station_state_message import StationStateMessage
from messages.power_output_message import PowerOutputMessage
from messages.power_requirement_message import PowerRequirementMessage
from messages.power_discharge_car_to_station_message import PowerDischargeCarToStationMessage
from messages.power_discharge_station_to_grid_message import PowerDischargeStationToGridMessage
from messages.car_discharge_power_requirement_message import CarDischargePowerRequirementMessage
from messages.grid_load_status_message import GridLoadStatusMessage
from messages.total_charging_cost_message import TotalChargingCostMessage

LOGGER = FullLogger(__name__)

STATION_ID = "STATION_ID"
USER_ID = "USER_ID"
MAX_POWER = "MAX_POWER"
CHARGING_COST = "CHARGING_COST"
COMPENSATION_AMOUNT = "COMPENSATION_AMOUNT"

STATION_STATE_TOPIC = "STATION_STATE_TOPIC"
POWER_OUTPUT_TOPIC = "POWER_OUTPUT_TOPIC"
POWER_DISCHARGE_STATION_TO_GRID_TOPIC = "POWER_DISCHARGE_STATION_TO_GRID"
CAR_DISCHARGE_POWER_REQUIREMENT_TOPIC = "CAR_DISCHARGE_POWER_REQUIREMENT_TOPIC"
POWER_REQUIREMENT_TOPIC = "POWER_REQUIREMENT_TOPIC"
TOTAL_CHARGING_COST_TOPIC = "TOTAL_CHARGING_COST_TOPIC"

TIMEOUT = 1.0
GRID_ID = "1"

class StationComponent(AbstractSimulationComponent):


    def __init__(self, station_id: str, max_power: float, charging_cost: float, compensation_amount: float):

        super().__init__()

        self._station_id = station_id
        self._max_power = max_power
        self._charging_cost = charging_cost
        self._compensation_amount = compensation_amount


        self._station_state: bool = False
        self._power_requirement_received: bool = False
        self._power_output: float = 0.0
        self._user_id: int = 0
        self._power_discharge_car_to_station_received: bool = False
        self._discharged_power: float = 0.0
        self._power_discharge_needed: float = 0.0
        self._power_discharge_requirement_received = False
        self._discharge_epoch_sent: bool = False
        self._power_output_epoch_sent: bool = False
        self._grid_load_status_received  = False
        self._grid_load_status = False
        self._total_charging_cost = 0.0
        self._send_total_charging_cost = False

        environment = load_environmental_variables(
            (STATION_STATE_TOPIC, str, "StationStateTopic"),
            (POWER_OUTPUT_TOPIC, str, "PowerOutputTopic"),
            (POWER_DISCHARGE_STATION_TO_GRID_TOPIC, str, "PowerDischargeStationToGrid"),
            (CAR_DISCHARGE_POWER_REQUIREMENT_TOPIC, str, "CarDischargePowerRequirementTopic"),
            (POWER_REQUIREMENT_TOPIC, str, "Station.PowerRequirementTopic"),
            (TOTAL_CHARGING_COST_TOPIC, str, "Station.TotalChargingCost"),
        )
        self._station_state_topic = cast(str, environment[STATION_STATE_TOPIC])
        self._power_output_topic = cast(str, environment[POWER_OUTPUT_TOPIC])
        self._power_discharge_station_to_grid_topic = cast(str, environment[POWER_DISCHARGE_STATION_TO_GRID_TOPIC])
        self._power_discharge_requirement_topic = cast(str, environment[CAR_DISCHARGE_POWER_REQUIREMENT_TOPIC])
        self._power_requirement_topic = cast(str, environment[POWER_REQUIREMENT_TOPIC])
        self._total_charging_cost_topic = cast(str, environment[TOTAL_CHARGING_COST_TOPIC])
        
        # The easiest way to ensure that the component will listen to all necessary topics
        # is to set the self._other_topics variable with the list of the topics to listen to.
        # Note, that the "SimState" and "Epoch" topic listeners are added automatically by the parent class.
        self._other_topics = [
            "V2GController.PowerRequirementTopic", 
            "PowerDischargeCarToStation",
            "V2GController.CarDischargePowerRequirementTopic",
            "V2GController.GridLoadStatus",
        ]

    def clear_epoch_variables(self) -> None:
        self._station_state = False
        self._power_requirement_received = False
        self._power_discharge_car_to_station_received = False
        self._power_output = 0.0
        self._user_id = 0
        self._discharged_power = 0.0
        self._power_discharge_needed: float = 0.0
        self._power_discharge_requirement_received = False
        self._discharge_epoch_sent: bool = False
        self._power_output_epoch_sent: bool = False
        self._grid_load_status_received  = False
        self._grid_load_status = False
        self._send_total_charging_cost = False
        
    async def process_epoch(self) -> bool:

        if not (self._station_state):
            await self._send_stationstate_message()
            self._station_state = True

        if (self._power_requirement_received and not self._power_output_epoch_sent):
            await self._send_poweroutput_message()
            self._power_output_epoch_sent = True
            #return True
        
        if self._power_discharge_requirement_received and not self._discharge_epoch_sent:
            await self._send_power_discharge_requirement_to_user()
            self._discharge_epoch_sent = True
            #return True
        
        LOGGER.info(f"power discharge car to station received value: {self._power_discharge_car_to_station_received}")
        if self._power_discharge_car_to_station_received:
            await self._send_power_discharge_station_to_grid_message()
        
        if self._power_output_epoch_sent and not self._send_total_charging_cost:
    
            self._total_charging_cost += self._power_output * self._charging_cost
            await self._send_total_charging_cost_message()
            self._send_total_charging_cost = True
            LOGGER.info(f"Total charging cost calculated in current epoch: {self._total_charging_cost}")

        
        if not self._grid_load_status and self._power_requirement_received and self._power_output_epoch_sent:
            return True
        
        if self._grid_load_status and \
            self._power_discharge_car_to_station_received and \
            self._power_discharge_car_to_station_received:
            return True
        
        return False

    async def _send_power_discharge_station_to_grid_message(self):
        """
        Sends power discharge station to grid message to Grid component
        """
        LOGGER.info("Sending power discharge station to grid message")

        try:
            powerdischarge_message = self._message_generator.get_message(
                PowerDischargeStationToGridMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                Power=self._discharged_power,
                StationId=self._station_id,
                GridId=GRID_ID
            )

            await self._rabbitmq_client.send_message(
                topic_name=self._power_discharge_station_to_grid_topic,
                message_bytes=powerdischarge_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            # When there is an exception while creating the message, it is in most cases a serious error.
            log_exception(message_error)
            await self.send_error_message("Internal error when creating result message.")

    async def _send_stationstate_message(self):
        """
        Sends a initial station state message to the IC
        """
        try:
            stationstate_message = self._message_generator.get_message(
                StationStateMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                StationId=self._station_id,
                MaxPower=self._max_power,
                ChargingCost=self._charging_cost,
                CompensationAmount=self._compensation_amount
            )

            await self._rabbitmq_client.send_message(
                topic_name=self._station_state_topic,
                message_bytes=stationstate_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            # When there is an exception while creating the message, it is in most cases a serious error.
            log_exception(message_error)
            await self.send_error_message("Internal error when creating result message.")

    async def _send_poweroutput_message(self):
        """
        Sends a powerout message to given user topic
        """
        try:
            poweroutput_message = self._message_generator.get_message(
                PowerOutputMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                StationId=self._station_id,
                UserId=self._user_id,
                PowerOutput=self._power_output
            )

            await self._rabbitmq_client.send_message(
                topic_name=self._power_output_topic,
                message_bytes=poweroutput_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            # When there is an exception while creating the message, it is in most cases a serious error.
            log_exception(message_error)
            await self.send_error_message("Internal error when creating result message.")

    async def _send_power_discharge_requirement_to_user(self):
        try:
            power_discharge_message = self._message_generator.get_message(
                CarDischargePowerRequirementMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                StationId=self._station_id,
                UserId=self._user_id,
                Power=self._power_discharge_needed
            )

            await self._rabbitmq_client.send_message(
                #topic_name=self._power_discharge_requirement_topic,
                topic_name=self._power_requirement_topic,
                message_bytes=power_discharge_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            # When there is an exception while creating the message, it is in most cases a serious error.
            log_exception(message_error)
            await self.send_error_message("Internal error when creating result message.")
    
    # async def _calculate_total_charging_cost(self) -> None:
    #     """
    #     Calculates total charging cost
    #     """
    #     try:
    #         self._total_charging_cost += self._power_output * self._charging_cost
    #         LOGGER.info(f"Total charging cost calculated in current epoch: {self._total_charging_cost}")
    #     except Exception as e:
    #         log_exception(e)
    #         await self.send_error_message("Internal error when calculating total charging cost.")

    async def _send_total_charging_cost_message(self) -> None:
        """Sends a total charging cost message."""
        try:
            total_charging_cost_message = self._message_generator.get_message(
                TotalChargingCostMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                TotalChargingCost=self._total_charging_cost
            )

            await self._rabbitmq_client.send_message(
                topic_name=self._total_charging_cost_topic,
                message_bytes= total_charging_cost_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            log_exception(message_error)
            await self.send_error_message("Internal error when creating total charging cost message.")


    async def all_messages_received_for_epoch(self) -> bool:
        return True

    async def general_message_handler(self, message_object: Union[BaseMessage, Any],
                                      message_routing_key: str) -> None:
        LOGGER.info("message handler.")
        if isinstance(message_object, PowerRequirementMessage):
            message_object = cast(PowerRequirementMessage, message_object)
            LOGGER.info(str(message_object))
            if message_object.station_id == self._station_id:
                LOGGER.info(f"Received PowerRequirementMessage from {message_object.source_process_id}")
                self._power_output = float(message_object.power)
                self._user_id = message_object.user_id
                self._power_requirement_received = True
                await self.start_epoch()
            else:
                LOGGER.info(f"Ignoring PowerRequirementMessage from {message_object.source_process_id}")

        elif isinstance(message_object, CarDischargePowerRequirementMessage):
            message_object = cast(CarDischargePowerRequirementMessage, message_object)
            LOGGER.info(str(message_object))
            if message_object.station_id == self._station_id:
                LOGGER.info(f"Received CarDischargePowerRequirementMessage from {message_object.source_process_id}")
                self._power_discharge_needed = float(message_object.power)
                self._user_id = message_object.user_id
                self._power_discharge_requirement_received = True
                await self.start_epoch()
            else:
                LOGGER.info(f"Ignoring PowerRequirementMessage from {message_object.source_process_id}")

        elif isinstance(message_object, PowerDischargeCarToStationMessage):
            message_object = cast(PowerDischargeCarToStationMessage, message_object)
            LOGGER.info(str(message_object))
            if message_object.station_id == self._station_id:
                LOGGER.info(f"Received PowerDischargeCarToStationMessage from {message_object.source_process_id}")
                self._user_id = message_object.user_id
                self._power_discharge_car_to_station_received = True
                self._discharged_power = message_object.power
                await self.start_epoch()
            else:
                LOGGER.info(f"Ignoring PowerDischargeCarToStationMessage from {message_object.source_process_id}")
        
        elif isinstance(message_object, GridLoadStatusMessage):
            message_object = cast(GridLoadStatusMessage, message_object)
            LOGGER.info(f"Grid load status message received: {str(message_object)}")

            self._grid_load_status_received  = True
            self._grid_load_status = message_object.load_status

            await self.start_epoch()
        else:
            LOGGER.info(f"Received unknown message from {message_routing_key}: {message_object}")


def create_component() -> StationComponent:

    LOGGER.info("create")
    environment_variables = load_environmental_variables(
        (STATION_ID, str, ""),
        (MAX_POWER, float, 0.0),
        (CHARGING_COST, float, 0.0),
        (COMPENSATION_AMOUNT, float, 0.0),
    )
    station_id = cast(str, environment_variables[STATION_ID])
    max_power = cast(float, environment_variables[MAX_POWER])
    charging_cost = cast(float, environment_variables[CHARGING_COST])
    compensation_amount = cast(float, environment_variables[COMPENSATION_AMOUNT])

    return StationComponent(
        station_id=station_id,
        max_power=max_power,
        charging_cost=charging_cost,
        compensation_amount=compensation_amount
    )


async def start_component():
    try:
        LOGGER.info("start")
        station_component = create_component()
        await station_component.start()

        while not station_component.is_stopped:
            await asyncio.sleep(TIMEOUT)

    except BaseException as error:  # pylint: disable=broad-except
        log_exception(error)
        LOGGER.info("Component will now exit.")


if __name__ == "__main__":
    asyncio.run(start_component())

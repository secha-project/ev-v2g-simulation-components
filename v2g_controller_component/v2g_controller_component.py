# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

import asyncio
import csv
import os

from datetime import datetime
from typing import Any, cast, List, Union

from messages.car_discharge_power_requirement_message import CarDischargePowerRequirementMessage
from tools.components import AbstractSimulationComponent
from tools.exceptions.messages import MessageError
from tools.messages import BaseMessage
from tools.tools import FullLogger, load_environmental_variables, log_exception
from tools.datetime_tools import to_utc_datetime_object

from v2g_controller_component.power_info import PowerInfo
from v2g_controller_component.station_data import StationData
from v2g_controller_component.user_data import UserData
from messages.car_metadata_message import CarMetaDataMessage
from messages.station_state_message import StationStateMessage
from messages.user_state_message import UserStateMessage
from messages.power_requirement_message import PowerRequirementMessage
from messages.car_state_message import CarStateMessage
from messages.grid_state_message import GridStateMessage

LOGGER = FullLogger(__name__)

# set the names of the used environment variables to Python variables
USER_ID = "USER_ID"
USER_NAME = "USER_NAME"
STATION_ID = "STATION_ID"
STATE_OF_CHARGE = "STATE_OF_CHARGE"
CAR_BATTERY_CAPACITY = "CAR_BATTERY_CAPACITY"
CAR_MODEL = "CAR_MODEL"
CAR_MAX_POWER = "CAR_MAX_POWER"
TARGET_STATE_OF_CHARGE = "TARGET_STATE_OF_CHARGE"
TARGET_TIME = "TARGET_TIME"
ARRIVAL_TIME = "ARRIVAL_TIME"
MAX_POWER = "MAX_POWER"
TOTAL_MAX_POWER = "TOTAL_MAX_POWER"

USER_STATE_TOPIC = "USER_STATE_TOPIC"
CAR_STATE_TOPIC = "CAR_STATE_TOPIC"
CAR_METADATA_TOPIC = "CAR_METADATA_TOPIC"
STATION_STATE_TOPIC = "STATION_STATE_TOPIC"
POWER_OUTPUT_TOPIC = "POWER_OUTPUT_TOPIC"
POWER_REQUIREMENT_TOPIC = "POWER_REQUIREMENT_TOPIC"

TIMEOUT = 1.0
DEFAULT_MIN_STATE_OF_CHARGE = 50.0
MAX_STATE_OF_CHARGE = 100.0

# get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class V2GControllerComponent(AbstractSimulationComponent):
   
    def __init__(self):

        super().__init__()

        self._users: List[UserData] = []
        self._stations: List[StationData] = []
        self._total_max_power = 0.0
        self._current_available_power = 0.0

        self._total_user_count = 0
        self._total_station_count = 0

        self._car_metadata_received = False
        self._station_state_received = False
        self._user_state_received = False
        self._car_state_received = False
        self._grid_state_received = False
        self._power_requirement_message_sent = False

        self._epoch_car_metadata_count = 0
        self._epoch_station_state_count = 0
        self._epoch_user_state_count = 0
        self._epoch_car_state_count = 0
        self._used_total_power = 0.0
        self._user_preferences = {}
        self._total_max_power_output_received = False
        self._send_car_discharge_power_requirement = False

        environment = load_environmental_variables(
            (POWER_REQUIREMENT_TOPIC, str, "PowerRequirementTopic")
        )

        self._power_requirement_topic = cast(str, environment[POWER_REQUIREMENT_TOPIC])

        self._other_topics = [
            "Init.User.CarMetadata",
            "User.UserState",
            "User.CarState",
            "StationStateTopic",
            "GridState"
        ]

        if self.start_message is not None:
            users = self.start_message.get('ProcessParameters', {}).get('UserComponent', {}).keys()
            stations = self.start_message.get('ProcessParameters', {}).get('StationComponent', {}).keys()
            LOGGER.info("START MESSAGE")
            LOGGER.info(f"Users: {users}")
            LOGGER.info(f"Stations: {stations}")
            self._total_user_count = len(users)
            self._total_station_count = len(stations)

    def clear_epoch_variables(self) -> None:
        """Clears all the variables that are used to store information about the received input within the
           current epoch. This method is called automatically after receiving an epoch message for a new epoch.
           NOTE: this method should be overwritten in any child class that uses epoch specific variables
        """
        self._epoch_station_state_count = 0
        self._epoch_user_state_count = 0
        self._epoch_car_state_count = 0
        self._used_total_power = 0.0

        self._station_state_received = False
        self._user_state_received = False
        self._car_state_received = False
        self._power_requirement_message_sent = False
        self._stations = []
        self._send_car_discharge_power_requirement = False

    async def process_epoch(self) -> bool:
        """
        Process the epoch and do all the required calculations.
        Assumes that all the required information for processing the epoch is available.
        Returns False, if processing the current epoch was not yet possible.
        Otherwise, returns True, which indicates that the epoch processing was fully completed.
        This also indicated that the component is ready to send a Status Ready message to the Simulation Manager.
        NOTE: this method should be overwritten in any child class.
        TODO: add proper description specific for this component.
        """
        LOGGER.info(f"TOTAL AVAILABLE POWER: {self._total_max_power}")
        LOGGER.info("Process epoch")
        LOGGER.info(f"metadata count: {self._epoch_car_metadata_count}")
        LOGGER.info(f"total user count: {self._total_user_count}")

        if self._epoch_car_metadata_count == self._total_user_count:
            self._car_metadata_received = True
            LOGGER.info(f"All Car Metadata Received: {self._car_metadata_received}")

        if self._epoch_station_state_count == self._total_station_count:
            self._station_state_received = True
            LOGGER.info(f"All Station State Received: {self._stations}")

        if self._epoch_user_state_count == self._total_user_count:
            self._user_state_received = True
            LOGGER.info("All User State Received")

        if not self._power_requirement_message_sent and (
            self._grid_state_received and self._car_metadata_received 
            and self._station_state_received and self._user_state_received
        ):
            await self._send_power_requirement_message()
            self._power_requirement_message_sent = True

        if not self._send_car_discharge_power_requirement and (
            self._grid_state_received and self._car_metadata_received
            and self._station_state_received and self._user_state_received
        ):
            await self._send_car_discharge_power_requirement_message()
            self._send_car_discharge_power_requirement = True


        if self._epoch_car_state_count == self._total_user_count:
            self._car_state_received = True

        return self._grid_state_received and self._power_requirement_message_sent and self._car_state_received 

    async def all_messages_received_for_epoch(self) -> bool:
        return True

    async def general_message_handler(self, message_object: Union[BaseMessage, Any], message_routing_key: str) -> None:
        LOGGER.info("message handler.")

        if isinstance(message_object, CarMetaDataMessage):
            message_object = cast(CarMetaDataMessage, message_object)
            carMetaDatainfo = UserData(
                user_id=message_object.user_id,
                user_name=message_object.user_name,
                user_component_name=message_object.source_process_id,
                station_id=message_object.station_id,
                state_of_charge=message_object.state_of_charge,
                car_battery_capacity=message_object.car_battery_capacity,
                car_model=message_object.car_model,
                car_max_power=message_object.car_max_power
            )
            if carMetaDatainfo.user_id in [user.user_id for user in self._users]:
                LOGGER.warning(f"Received second metadata for user {carMetaDatainfo.user_id}")
                return

            self._users.append(carMetaDatainfo)
            LOGGER.info(f"Number of users with metadata: {len(self._users)}")
            self._epoch_car_metadata_count = self._epoch_car_metadata_count + 1
            await self.start_epoch()

        elif isinstance(message_object, StationStateMessage):
            message_object = cast(StationStateMessage, message_object)
            stationInfo = StationData(
                station_id=message_object.station_id,
                max_power=message_object.max_power,
                charging_cost=message_object.charging_cost,
                compensation_amount=message_object.compensation_amount
            )
            if stationInfo.station_id in [station.station_id for station in self._stations]:
                LOGGER.warning(f"Received second data for station {stationInfo.station_id}")
                return

            self._stations.append(stationInfo)
            LOGGER.info(f"Number of stations with data: {len(self._stations)}")
            self._epoch_station_state_count = self._epoch_station_state_count + 1
            await self.start_epoch()

        elif isinstance(message_object, UserStateMessage):
            message_object = cast(UserStateMessage, message_object)
            LOGGER.info(f"user state: {message_object}")
            LOGGER.info(f"USER STATE MESSAGE: {self._user_state_received}")

            if message_object.user_id not in [user.user_id for user in self._users]:
                LOGGER.error(f"Received an user state message for a user without metadata: {message_object.user_id}")
                # TODO: figure out what to do in this case:
                return

            for user in self._users:

                if user.user_id == message_object.user_id:
                    
                    if user.user_id in self._user_preferences:
                        ## TODO: change min soc in file to be in percentage 0 - 100 to avoid conversion here
                        min_soc = self._user_preferences[user.user_id]["MinimumSOC"] * 100
                        user.target_state_of_charge = min_soc
                    else:
                        LOGGER.warning(f"No MinimumSOC preference found for user: {user.user_id}")
                        user.target_state_of_charge = DEFAULT_MIN_STATE_OF_CHARGE
                
                    user.target_time = message_object.target_time
                    user.arrival_time = message_object.arrival_time
                    user.required_energy = user.car_battery_capacity * (user.target_state_of_charge - user.state_of_charge) / 100
                    LOGGER.info(str(user))
                    break

            self._epoch_user_state_count = self._epoch_user_state_count + 1
            await self.start_epoch()

        elif isinstance(message_object, CarStateMessage):
            message_object = cast(CarStateMessage, message_object)
            LOGGER.info(f"car state: {message_object}")

            if message_object.user_id not in [user.user_id for user in self._users]:
                LOGGER.error(f"Received a car state message for a user without data: {message_object.user_id}")
                # TODO: figure out what to do in this case:
                return

            for user in self._users:
                if user.user_id == message_object.user_id:
                    user.state_of_charge = message_object.state_of_charge
                    
                    if self._check_user_discharge_need(user):
                        if user.state_of_charge > user.target_state_of_charge:
                            user.required_energy = 0.0
                            user.target_state_of_charge = max(user.state_of_charge - 10.0, 
                                                              self._user_preferences[user.user_id]["MinimumSOC"]* 100)

                    # If SoC == target SoC, check if user is willing to pay for more charging
                    elif user.state_of_charge == user.target_state_of_charge:
                        station = next((s for s in self._stations if s.station_id == user.station_id), None)
                        if station and user.user_id in self._user_preferences:
                            max_cost = self._user_preferences[user.user_id]["MaxCostForCharging"]
                            if max_cost >= station.charging_cost:
                                # Allow further charging by increasing target SoC (e.g., up to 100%)
                                if user.target_state_of_charge < MAX_STATE_OF_CHARGE:
                                    LOGGER.info(f"User {user.user_id} is willing to pay for more charging at station {station.station_id}. Increasing target SoC.")
                                    user.target_state_of_charge = MAX_STATE_OF_CHARGE # min(100.0, user.target_state_of_charge + 10.0)  # or any other logic
                                    user.required_energy = user.car_battery_capacity * (user.target_state_of_charge - user.state_of_charge) / 100

                    LOGGER.info(str(user))
                    break

            LOGGER.info(f"car_state_received: {self._car_state_received}")
            self._epoch_car_state_count = self._epoch_car_state_count + 1
            await self.start_epoch()
        
        elif isinstance(message_object, GridStateMessage):
            message_object = cast(GridStateMessage, message_object)
            LOGGER.info(f"car state: {message_object}")

            self._grid_state_received  = True

            if not self._total_max_power_output_received:
                self._total_max_power = message_object.max_power
                self._total_max_power_output_received = True
            
            self._current_available_power = message_object.current_power

            await self.start_epoch()

        else:
            LOGGER.debug(f"Received unknown message from {message_routing_key}: {message_object}")

    async def _send_power_requirement_message(self):
        LOGGER.info("power requirement message initiated")
        
        if self._latest_epoch_message is None:
            await self.send_error_message("Tried to calculate power distribution before any epoch messages had arrived")
            return
        start_time = to_utc_datetime_object(self._latest_epoch_message.start_time)
        end_time = to_utc_datetime_object(self._latest_epoch_message.end_time)
        epoch_length = int((end_time - start_time).total_seconds())

        connected_users: List[UserData] = []

        for user in self._users:
            arrival_time = to_utc_datetime_object(user.arrival_time)
            target_time = to_utc_datetime_object(user.target_time)
            if start_time >= arrival_time and end_time <= target_time:
                connected_users.append(user)
        connected_users = sorted(connected_users, key=lambda user: (user.target_time, -user.required_energy))
        LOGGER.info(f"Connected_users: {connected_users}")

        power_requirements = self._calculate_power_requirements(connected_users, start_time)

        for power_info in power_requirements:
            powerRequirementForStation = float(0.0)
            LOGGER.info(f"POWER REQUIREMENT: {power_info}")

            if power_info.user_id != 0:
                if self._used_total_power < self._current_available_power:
                    LOGGER.info("IN CONDITION")
                    LOGGER.info("EPOCH MESSAGE")
                    LOGGER.info("START TIME")
                    LOGGER.info(f"epoch_length: {epoch_length}")

                    if power_info.target_state_of_charge > power_info.state_of_charge:
                        powerRequirementForStation = min(
                            power_info.station_max_power,
                            power_info.car_max_power,
                            self._current_available_power - self._used_total_power,
                            power_info.required_energy / (epoch_length / 3600)
                        )
                        self._used_total_power = self._used_total_power + powerRequirementForStation
                    LOGGER.info(f"power to station '{power_info.station_id}': {powerRequirementForStation}")

            await self._send_single_power_requirement_message(power_info, powerRequirementForStation)

        LOGGER.info(f"Allocated {self._used_total_power} power (maximum: {self._current_available_power}) in epoch {self._latest_epoch}")
    

    def _calculate_power_requirements(self, connected_users: List[UserData], start_time: datetime):
        """Calculates and returns the power requirements for each station."""
        power_requirements: List[PowerInfo] = []
        empty_power_requirements: List[PowerInfo] = []

        for station in self._stations:
            LOGGER.info(f"STATION LOGGER: {station}")
            isConnected = False
            for user in connected_users:
                if user.station_id == station.station_id:
                    isConnected = True
                    LOGGER.info(str(start_time))
                    LOGGER.info(str(user.arrival_time))
                    powerInfo = PowerInfo(
                        user_id=user.user_id,
                        station_id=user.station_id,
                        station_max_power=station.max_power,
                        car_max_power=user.car_max_power,
                        state_of_charge=user.state_of_charge,
                        target_state_of_charge=user.target_state_of_charge,
                        required_energy=user.required_energy,
                        target_time=user.target_time
                    )
                    power_requirements.append(powerInfo)
            if not isConnected:
                empty_power_requirements.append(PowerInfo(user_id=0, station_id=station.station_id))

        power_requirements = sorted(power_requirements, key=lambda power_info: (power_info.target_time, -power_info.required_energy))
        LOGGER.info(f"power_requirements: {power_requirements}")

        power_requirements = power_requirements + empty_power_requirements
        LOGGER.info(f"power_requirements: {power_requirements}")

        return power_requirements

    async def _send_single_power_requirement_message(self, power_info: PowerInfo, power_requirement: float) -> None:
        """Publishes one power requirement message."""
        try:
            power_requirement_message = self._message_generator.get_message(
                PowerRequirementMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                StationId = power_info.station_id,
                UserId = power_info.user_id,
                Power = power_requirement
            )

            await self._rabbitmq_client.send_message(
                topic_name=self._power_requirement_topic,
                message_bytes= power_requirement_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            log_exception(message_error)
            await self.send_error_message("Internal error when creating result message.")
    
    def _load_user_preferences_from_file(self):
        
        csv_path = os.path.join(BASE_DIR, "v2g_user_preferences.csv")

        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self._user_preferences[row["UserID"]] = {
                    "MinimumSOC": float(row["MinimumSOC"]),
                    "MaxCostForCharging": float(row["MaxCostForCharging"]),
                    "DischargePriceThreshold": float(row["DischargePriceThreshold"]),
                }

    def _is_grid_under_load(self) -> bool:
        """Checks if the grid is under load."""
        start_time = to_utc_datetime_object(self._latest_epoch_message.start_time)
        hour_str = start_time.strftime("%H:00")

        csv_path = os.path.join(BASE_DIR, "grid_load_daily.csv")
        try:
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row["time"] == hour_str:
                        return row["grid_on_load"] == "1"
        except Exception as e:
            LOGGER.error(f"Error reading grid_load_daily.csv: {e}")

        return False

    def _check_user_discharge_need(self, user: UserData) -> bool:
        """Checks if the car is needed for discharging based on user preferences and grid load."""
        if user.user_id not in self._user_preferences:
            LOGGER.warning(f"No preferences found for user {user.user_id}. Cannot discharge.")
            return False

        if self._is_grid_under_load():
            LOGGER.info(f"Grid is under load")
            station = next((s for s in self._stations if s.station_id == user.station_id), None)
            if station:
                discharge_price_threshold = self._user_preferences[user.user_id]["DischargePriceThreshold"]
                if discharge_price_threshold <= station.compensation_amount:
                    user.discharge = True
        
        return user.discharge

    async def _send_car_discharge_power_requirement_message(self) -> None:
        """Sends a car discharge power requirement message."""

        LOGGER.info("Car discharge power requirement message initiated")
        
        if self._latest_epoch_message is None:
            await self.send_error_message("Tried to send discharge power message before any epoch messages had arrived")
            return
        start_time = to_utc_datetime_object(self._latest_epoch_message.start_time)
        end_time = to_utc_datetime_object(self._latest_epoch_message.end_time)
        # epoch_length = int((end_time - start_time).total_seconds())

        discharge_users: List[UserData] = []

        for user in self._users:
            arrival_time = to_utc_datetime_object(user.arrival_time)
            target_time = to_utc_datetime_object(user.target_time)
            discharge_users = [user for user in self._users if user.discharge and start_time >= arrival_time and end_time <= target_time]

        LOGGER.info(f"Discharge_users: {discharge_users}")

        for user in discharge_users:
            LOGGER.info(f"USER DISCHARGE STATUS: {user.user_id} - {user.discharge}")

            await self._send_single_discharge_power_requirement_message(user)

    async def _send_single_discharge_power_requirement_message(self, user: UserData) -> None:
        """Publishes one power requirement message."""
        try:
            power_requirement_message = self._message_generator.get_message(
                CarDischargePowerRequirementMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                StationId = user.station_id,
                UserId = user.user_id,
                Power = user.car_battery_capacity * (user.state_of_charge - user.target_state_of_charge) / 100
            )

            await self._rabbitmq_client.send_message(
                topic_name=self._power_requirement_topic,
                message_bytes= power_requirement_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            log_exception(message_error)
            await self.send_error_message("Internal error when creating result message.")

def create_component() -> V2GControllerComponent:
    LOGGER.info("create V2G Controller component")
    return V2GControllerComponent()


async def start_component():
    """
    Creates and starts a V2G Controller component.
    """

    try:
        LOGGER.debug("start V2G Controller component")
        v2g_controller_component = create_component()
        v2g_controller_component._load_user_preferences_from_file()

        await v2g_controller_component.start()

        while not v2g_controller_component.is_stopped:
            await asyncio.sleep(TIMEOUT)

    except BaseException as error: 
        log_exception(error)
        LOGGER.info("Component will now exit.")


if __name__ == "__main__":
    asyncio.run(start_component())

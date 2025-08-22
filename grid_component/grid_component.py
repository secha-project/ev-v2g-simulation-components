# Copyright 2022 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

from __future__ import annotations
import asyncio
from typing import Any, cast, Union

from tools.components import AbstractSimulationComponent
from tools.exceptions.messages import MessageError
from tools.messages import BaseMessage
from tools.tools import FullLogger, load_environmental_variables, log_exception

# import all the required messages from installed libraries
from messages.grid_state_message import GridStateMessage
from messages.power_discharge_station_to_grid_message import PowerDischargeStationToGridMessage


# initialize logging object for the module
LOGGER = FullLogger(__name__)


# set the names of the used environment variables to Python variables
GRID_ID = "GRID_ID"
TOTAL_MAX_POWER_OUTPUT = "TOTAL_MAX_POWER_OUTPUT"


GRID_STATE_TOPIC = "GRID_STATE_TOPIC"

# time interval in seconds on how often to check whether the component is still running
TIMEOUT = 1.0

class GridComponent(AbstractSimulationComponent):
    # The constructor for the component class.
    def __init__(
        self,
        grid_id: int,
        total_max_power_output: float
    ):

        # Initialize the AbstractSimulationComponent using the values from the environmental variables.
        # This will initialize various variables including the message client for message bus access.
        super().__init__()

        # Set the object variables for the extra parameters.
        self._grid_id = grid_id   
        self._total_max_power_output = total_max_power_output

        self._power_received = 0.0
        self._current_power_capacity = self._total_max_power_output
        self._grid_state_sent = False
        self._power_discharge_station_to_grid_received = False
        

        # Add checks for the parameters if necessary
        # and set initialization error if there is a problem with the parameters.
        # if <some_check_for_the_parameters>:
        #     # add appropriate error message
        #     self.initialization_error = "There was a problem with the parameters"
        #     LOGGER.error(self.initialization_error)

        # variables to keep track of the components that have provided input within the current epoch
        # and to keep track of the current sum of the input values


        # Load environmental variables for those parameters that were not given to the constructor.
        # In this template the used topics are set in this way with given default values as an example.
        # fix topic names
        environment = load_environmental_variables(
            (GRID_STATE_TOPIC, str, "GridState"),
        )

        self._grid_state_topic = cast(str, environment[GRID_STATE_TOPIC])

        # The easiest way to ensure that the component will listen to all necessary topics
        # is to set the self._other_topics variable with the list of the topics to listen to.
        # Note, that the "SimState" and "Epoch" topic listeners are added automatically by the parent class.

        # receive topic
        self._other_topics = [
            "PowerDischargeStationToGrid",
        ]

        # The base class contains several variables that can be used in the child class.
        # The variable list below is not an exhaustive list but contains the most useful variables.

        if self.start_message is not None:
            LOGGER.info("START MESSAGE")
            LOGGER.info(str(self.start_message.get("ProcessParameters", {}).get("GridComponent", {}).keys()))

        # Variables that should only be READ in the child class:
        # - self.simulation_id               the simulation id
        # - self.component_name              the component name
        # - self._simulation_state           either "running" or "stopped"
        # - self._latest_epoch               epoch number for the current epoch
        # - self._completed_epoch            epoch number for the latest epoch that has been completed
        # - self._latest_epoch_message       the latest epoch message as EpochMessage object

        # Variable for the triggering message ids where all relevant message ids should be appended.
        # The list is automatically cleared at the start of each epoch.
        # - self._triggering_message_ids

        # MessageGenerator object that can be used to generate the message objects:
        # - self._message_generator

        # RabbitmqClient object for communicating with the message bus:
        # - self._rabbitmq_client

    def clear_epoch_variables(self) -> None:
        """Clears all the variables that are used to store information about the received input within the
           current epoch. This method is called automatically after receiving an epoch message for a new epoch.
           NOTE: this method should be overwritten in any child class that uses epoch specific variables
        """
        self._grid_state_sent = False
        self._power_discharge_station_to_grid_received = False

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
                
        if self._power_discharge_station_to_grid_received:
            new_grid_capacity = self._current_power_capacity + self._power_received

            if new_grid_capacity >= self._total_max_power_output:
                self._current_power_capacity = self._total_max_power_output
            
            elif new_grid_capacity < self._total_max_power_output:
                self._current_power_capacity = new_grid_capacity
        
        if not self._grid_state_sent:
            await self._send_grid_state_message()
            self._grid_state_sent = True

        return self._grid_state_sent


    async def all_messages_received_for_epoch(self) -> bool:
        return True

    async def general_message_handler(self, message_object: Union[BaseMessage, Any],
                                      message_routing_key: str) -> None:
        LOGGER.info("message handler.")
        if isinstance(message_object, PowerDischargeStationToGridMessage):
            message_object = cast(PowerDischargeStationToGridMessage, message_object)
            LOGGER.info(str(message_object))
            # if message_object.station_id == self._station_id:
            LOGGER.debug(f"Received PowerDischargeStationToGridMessage from {message_object.source_process_id}")
            self._power_received = float(message_object.power)
            self._power_discharge_station_to_grid_received = True
            await self.start_epoch()
            # else:
            #     LOGGER.debug(f"Ignoring PowerDischargeStationToGridMessage from {message_object.source_process_id}")
        else:
            LOGGER.debug(f"Received unknown message from {message_routing_key}: {message_object}")

    async def _send_grid_state_message(self):
        LOGGER.info("grid state message sent")
        try:
            grid_state_message = self._message_generator.get_message(
                GridStateMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                GridId=self._grid_id,
                MaxPower=self._total_max_power_output,
                CurrentPower=self._current_power_capacity
                # TotalMaxPowerOutput=self._total_max_power_output
            )

            await self._rabbitmq_client.send_message(
                topic_name=self._grid_state_topic,
                message_bytes= grid_state_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            # When there is an exception while creating the message, it is in most cases a serious error.
            log_exception(message_error)
            await self.send_error_message("Internal error when creating user state message.")


def create_component() -> GridComponent:
    """
    TODO: add proper description specific for this component.
    """
    LOGGER.info("create user component")
    # Read the parameters for the component from the environment variables.
    environment_variables = load_environmental_variables(
        (GRID_ID, int, 0),
        (TOTAL_MAX_POWER_OUTPUT, float, 0.0)
    )

    # The cast function here is only used to help Python linters like pyright to recognize the proper type.
    # They are not necessary and can be omitted.
    grid_id = cast(int, environment_variables[GRID_ID])
    total_max_power_output = cast(str, environment_variables[TOTAL_MAX_POWER_OUTPUT])

    # Create and return a new SimpleComponent object using the values from the environment variables
    return GridComponent(
        grid_id = grid_id,
        total_max_power_output = total_max_power_output
    )

async def start_component():
    """
    Creates and starts a GridComponent component.
    """
    # A general exception handler that should catch any unhandled error that would otherwise crash the program.
    # Having this might be especially useful when testing components in large simulations and some component(s)
    # crash without giving any output.
    #
    # Note, that any exceptions thrown in async functions will not be caught here.
    # Instead they should get logged as warnings but otherwise should not crash the component.
    try:
        LOGGER.debug("start grid component")
        grid_component = create_component()

        # The component will only start listening to the message bus once the start() method has been called.
        await grid_component.start()

        # Wait in the loop until the component has stopped itself.
        while not grid_component.is_stopped:
            await asyncio.sleep(TIMEOUT)

    except BaseException as error:  # pylint: disable=broad-except
        log_exception(error)
        LOGGER.info("Component will now exit.")


if __name__ == "__main__":
    asyncio.run(start_component())
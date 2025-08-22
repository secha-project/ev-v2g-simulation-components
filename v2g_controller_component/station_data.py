# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

"""Dataclass for holding information about the current state of a station during simulation."""

from dataclasses import dataclass


@dataclass
class StationData:
    """Dataclass for holding station information"""
    station_id: str
    max_power: float
    charging_cost: float
    compensation_amount: float

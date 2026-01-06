from typing import Any, TypedDict


class DoorStatus(TypedDict):
    closed: bool


class Doors(TypedDict):
    all_doors_locked: bool
    driver_front_locked: bool
    front_left: DoorStatus
    front_right: DoorStatus
    rear_left: DoorStatus
    rear_right: DoorStatus
    tailgate: DoorStatus


class TireStatus(TypedDict):
    status: str
    pressure: float
    placard_pressure: float


class Tires(TypedDict):
    front_left: TireStatus
    front_right: TireStatus
    rear_left: TireStatus
    rear_right: TireStatus


class WindowStatus(TypedDict):
    lower: float
    upper: float


class Windows(TypedDict):
    front_left: WindowStatus
    front_right: WindowStatus
    rear_left: WindowStatus
    rear_right: WindowStatus


class VehicleData(TypedDict):
    acceleration: tuple[float, float, float]
    accelerator_pedal_position: float
    ambient_temp: float
    battery_charge_level: float
    battery_voltage: float
    brake_pedal_status: str
    brake_torque: float
    compass_direction: str
    doors: Doors
    engine_coolant_temp: float
    engine_speed: float
    fuel_level: float
    fuel_range: float
    gear_lever_position: str
    heading: tuple[str, str, float, float]
    hood_status: str
    hybrid_vehicle_mode_status: str
    ignition_status: str
    outside_temperature: float
    yaw_rate: float
    windows: Windows
    wheel_torque_status: str
    tires: Tires
    position: tuple[str, float, float, float]
    parking_brake_status: tuple[str, str] | None
    oil_life_remaining: float
    odometer: float
    speed: float
    vehicle_life_cycle_mode: str
    battery_load_status: tuple[str, str]
    torque_at_transmission: float
    trip_fuel_economy: tuple[str, float]
    trip_xev_battery_distance_accumulated: tuple[str, float]


def parse_api_response(data: dict[str, Any]) -> VehicleData:
    metrics = data["metrics"]
    tire_pressure_status = {
        i["vehicleWheel"]: i["value"] for i in metrics["tirePressureStatus"]
    }
    tire_pressure = {i["vehicleWheel"]: i for i in metrics["tirePressure"]}
    windows = {
        i["vehicleSide"] + "." + i["vehicleWindow"]: i["value"]
        for i in metrics["windowStatus"]
    }
    door_lock = {
        i.get("vehicleSide", "") + "." + i["vehicleDoor"]: i
        for i in metrics["doorLockStatus"]
    }
    door_status = {
        (
            i.get("vehicleDoor", ""),
            i.get("vehicleSide", ""),
            i.get("vehicleOccupantRole", ""),
        ): i
        for i in metrics["doorStatus"]
    }

    parking_brake_status = None
    if "parkingBrakeStatus" in metrics:
        parking_brake_status = (
            metrics["parkingBrakeStatus"]["parkingBrakeType"],
            metrics["parkingBrakeStatus"]["value"],
        )

    return {
        "acceleration": (
            metrics["acceleration"]["value"]["x"],
            metrics["acceleration"]["value"]["y"],
            metrics["acceleration"]["value"]["z"],
        ),
        "accelerator_pedal_position": metrics["acceleratorPedalPosition"]["value"],
        "ambient_temp": metrics["ambientTemp"]["value"],
        "battery_charge_level": metrics["batteryStateOfCharge"]["value"],
        "battery_voltage": metrics["batteryVoltage"]["value"],
        "brake_pedal_status": metrics["brakePedalStatus"]["value"],
        "brake_torque": metrics["brakeTorque"]["value"],
        "compass_direction": metrics["compassDirection"]["value"],
        "doors": {
            "all_doors_locked": door_lock[".ALL_DOORS"]["value"] == "LOCKED",
            "driver_front_locked": door_lock["DRIVER.UNSPECIFIED_FRONT"]["value"]
            == "LOCKED",
            "front_left": {
                "closed": door_status[("UNSPECIFIED_FRONT", "DRIVER", "DRIVER")][
                    "value"
                ]
                == "CLOSED",
            },
            "front_right": {
                "closed": door_status[("UNSPECIFIED_FRONT", "PASSENGER", "PASSENGER")][
                    "value"
                ]
                == "CLOSED",
            },
            "rear_left": {
                "closed": door_status[("REAR_LEFT", "UNKNOWN", "PASSENGER")]["value"]
                == "CLOSED",
            },
            "rear_right": {
                "closed": door_status[("REAR_RIGHT", "UNKNOWN", "PASSENGER")]["value"]
                == "CLOSED",
            },
            "tailgate": {
                "closed": door_status[("TAILGATE", "", "PASSENGER")]["value"]
                == "CLOSED",
            },
        },
        "engine_coolant_temp": metrics["engineCoolantTemp"]["value"],
        "engine_speed": metrics["engineSpeed"]["value"],
        "fuel_level": metrics["fuelLevel"]["value"],
        "fuel_range": metrics["fuelRange"]["value"],
        "gear_lever_position": metrics["gearLeverPosition"]["value"],
        "heading": (
            metrics["heading"]["gpsModuleTimestamp"],
            metrics["heading"]["value"]["detectionType"],
            metrics["heading"]["value"]["heading"],
            metrics["heading"]["value"]["uncertainty"],
        ),
        "hood_status": metrics["hoodStatus"]["value"],
        "hybrid_vehicle_mode_status": metrics["hybridVehicleModeStatus"]["value"],
        "ignition_status": metrics["ignitionStatus"]["value"],
        "outside_temperature": metrics["outsideTemperature"]["value"],
        "yaw_rate": metrics["yawRate"]["value"],
        "windows": {
            "front_left": {
                "lower": windows.get("DRIVER.UNSPECIFIED_FRONT", {}).get("lower", 0.0),
                "upper": windows.get("DRIVER.UNSPECIFIED_FRONT", {}).get("upper", 0.0),
            },
            "front_right": {
                "lower": windows.get("PASSENGER.UNSPECIFIED_FRONT", {}).get(
                    "lower", 0.0
                ),
                "upper": windows.get("PASSENGER.UNSPECIFIED_FRONT", {}).get(
                    "upper", 0.0
                ),
            },
            "rear_left": {
                "lower": windows.get("DRIVER.UNSPECIFIED_REAR", {}).get("lower", 0.0),
                "upper": windows.get("DRIVER.UNSPECIFIED_REAR", {}).get("upper", 0.0),
            },
            "rear_right": {
                "lower": windows.get("PASSENGER.UNSPECIFIED_REAR", {}).get(
                    "lower", 0.0
                ),
                "upper": windows.get("PASSENGER.UNSPECIFIED_REAR", {}).get(
                    "upper", 0.0
                ),
            },
        },
        "wheel_torque_status": metrics["wheelTorqueStatus"]["value"],
        "tires": {
            "front_left": {
                "status": tire_pressure_status.get("FRONT_LEFT", ""),
                "pressure": tire_pressure.get("FRONT_LEFT", {}).get("value", 0.0),
                "placard_pressure": tire_pressure.get("FRONT_LEFT", {}).get(
                    "wheelPlacardFront", 0.0
                ),
            },
            "front_right": {
                "status": tire_pressure_status.get("FRONT_RIGHT", ""),
                "pressure": tire_pressure.get("FRONT_RIGHT", {}).get("value", 0.0),
                "placard_pressure": tire_pressure.get("FRONT_RIGHT", {}).get(
                    "wheelPlacardFront", 0.0
                ),
            },
            "rear_left": {
                "status": tire_pressure_status.get("REAR_LEFT", ""),
                "pressure": tire_pressure.get("REAR_LEFT", {}).get("value", 0.0),
                "placard_pressure": tire_pressure.get("REAR_LEFT", {}).get(
                    "wheelPlacardRear", 0.0
                ),
            },
            "rear_right": {
                "status": tire_pressure_status.get("REAR_RIGHT", ""),
                "pressure": tire_pressure.get("REAR_RIGHT", {}).get("value", 0.0),
                "placard_pressure": tire_pressure.get("REAR_RIGHT", {}).get(
                    "wheelPlacardRear", 0.0
                ),
            },
        },
        "position": (
            metrics["position"]["gpsModuleTimestamp"],
            metrics["position"]["value"]["location"]["lat"],
            metrics["position"]["value"]["location"]["lon"],
            metrics["position"]["value"]["location"]["alt"],
        ),
        "parking_brake_status": parking_brake_status,
        "oil_life_remaining": metrics["oilLifeRemaining"]["value"],
        "odometer": metrics["odometer"]["value"],
        "speed": metrics["speed"]["value"],
        "vehicle_life_cycle_mode": metrics["vehicleLifeCycleMode"]["value"],
        "battery_load_status": (
            metrics["batteryLoadStatus"]["vehicleBattery"],
            metrics["batteryLoadStatus"]["value"],
        ),
        "torque_at_transmission": metrics["torqueAtTransmission"]["value"],
        "trip_fuel_economy": (
            metrics["tripFuelEconomy"]["tripProgress"],
            metrics["tripFuelEconomy"]["value"],
        ),
        "trip_xev_battery_distance_accumulated": (
            metrics["tripXevBatteryDistanceAccumulated"]["tripProgress"],
            metrics["tripXevBatteryDistanceAccumulated"]["value"],
        ),
    }

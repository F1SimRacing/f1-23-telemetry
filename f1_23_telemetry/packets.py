"""
The hard work for this file was taken from here:
https://forums.codemasters.com/topic/
80231-f1-2021-udp-specification/?do=findComment&comment=624274
"""

import ctypes
import json

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def to_json(*args, **kwargs):
    kwargs.setdefault("indent", 2)

    kwargs["sort_keys"] = True
    kwargs["ensure_ascii"] = False
    kwargs["separators"] = (",", ": ")

    return json.dumps(*args, **kwargs)


class PacketMixin(object):
    """A base set of helper methods for ctypes based packets"""

    def get_value(self, field):
        """Returns the field's value and formats the types value"""
        return self._format_type(getattr(self, field))

    def pack(self):
        """Packs the current data structure into a compressed binary

        Returns:
            (bytes):
                - The packed binary

        """
        return bytes(self)

    @classmethod
    def size(cls):
        return ctypes.sizeof(cls)

    @classmethod
    def unpack(cls, buffer):
        """Attempts to unpack the binary structure into a python structure

        Args:
            buffer (bytes):
                - The encoded buffer to decode

        """
        return cls.from_buffer_copy(buffer)

    def to_dict(self):
        """Returns a ``dict`` with key-values derived from _fields_"""
        return {k: self.get_value(k) for k, _ in self._fields_}

    def to_json(self):
        """Returns a ``str`` of sorted JSON derived from _fields_"""
        return to_json(self.to_dict())

    def _format_type(self, value):
        """A type helper to format values"""
        class_name = type(value).__name__

        if class_name == "float":
            return round(value, 3)

        if class_name == "bytes":
            return value.decode()

        if isinstance(value, ctypes.Array):
            return _format_array_type(value)

        if hasattr(value, "to_dict"):
            return value.to_dict()

        return value


def _format_array_type(value):
    results = []

    for item in value:
        if isinstance(item, Packet):
            results.append(item.to_dict())
        else:
            results.append(item)

    return results


class Packet(ctypes.LittleEndianStructure, PacketMixin):
    """The base packet class for API version F1 22"""

    _pack_ = 1

    def __repr__(self):
        return self.to_json()


class PacketHeader(Packet):
    """
    struct PacketHeader
    {
        uint16 m_packetFormat; // 2023
        uint8 m_gameYear; // Game year - last two digits e.g. 23
        uint8 m_gameMajorVersion; // Game major version - "X.00"
        uint8 m_gameMinorVersion; // Game minor version - "1.XX"
        uint8 m_packetVersion; // Version of this packet type, all start from 1
        uint8 m_packetId; // Identifier for the packet type, see below
        uint64 m_sessionUID; // Unique identifier for the session
        float m_sessionTime; // Session timestamp
        uint32 m_frameIdentifier; // Identifier for the frame the data was retrieved on
        uint32 m_overallFrameIdentifier; // Overall identifier for the frame the data was retrieved
        // on, doesn't go back after flashbacks
        uint8 m_playerCarIndex; // Index of player's car in the array
        uint8 m_secondaryPlayerCarIndex; // Index of secondary player's car in the array (splitscreen)
        // 255 if no second player
    };
    """

    _fields_ = [
        ("packet_format", ctypes.c_int16),  # 2023
        ("game_year", ctypes.c_uint8),  # Game year - last two digits e.g. 23
        ("game_major_version", ctypes.c_uint8),  # Game major version - "X.00"
        ("game_minor_version", ctypes.c_uint8),  # Game minor version - "1.XX"
        ("packet_version", ctypes.c_uint8),  # Version of this packet type, all start from 1
        ("packet_id", ctypes.c_uint8),  # Identifier for the packet type
        ("session_uid", ctypes.c_uint64),  # unique identifier for the session
        ("session_time", ctypes.c_float),  # Session timestamp
        ("frame_identifier", ctypes.c_uint32),  # Identifier for the frame the data was retrieved on
        ("overall_frame_identifier", ctypes.c_uint32),  # Overall identifier for the frame the data was retrieved
        # on, doesn't go back after flashbacks
        ("player_car_index", ctypes.c_uint8),  # Index of player's car in the array
        ("secondary_player_car_index", ctypes.c_uint8),  # Index of secondary player's car in the array (splitscreen)
        # 255 if no second player
    ]


class CarMotionData(Packet):
    """
    struct CarMotionData
    {
        float m_worldPositionX; // World space X position - metres
        float m_worldPositionY; // World space Y position
        float m_worldPositionZ; // World space Z position
        float m_worldVelocityX; // Velocity in world space X – metres/s
        float m_worldVelocityY; // Velocity in world space Y
        float m_worldVelocityZ; // Velocity in world space Z
        int16 m_worldForwardDirX; // World space forward X direction (normalised)
        int16 m_worldForwardDirY; // World space forward Y direction (normalised)
        int16 m_worldForwardDirZ; // World space forward Z direction (normalised)
        int16 m_worldRightDirX; // World space right X direction (normalised)
        int16 m_worldRightDirY; // World space right Y direction (normalised)
        int16 m_worldRightDirZ; // World space right Z direction (normalised)
        float m_gForceLateral; // Lateral G-Force component
        float m_gForceLongitudinal; // Longitudinal G-Force component
        float m_gForceVertical; // Vertical G-Force component
        float m_yaw; // Yaw angle in radians
        float m_pitch; // Pitch angle in radians
        float m_roll; // Roll angle in radians
    };
    """

    _fields_ = [
        ("world_position_x", ctypes.c_float),  # World space X position
        ("world_position_y", ctypes.c_float),  # World space Y position
        ("world_position_z", ctypes.c_float),  # World space Z position
        ("world_velocity_x", ctypes.c_float),  # Velocity in world space X
        ("world_velocity_y", ctypes.c_float),  # Velocity in world space Y
        ("world_velocity_z", ctypes.c_float),  # Velocity in world space Z
        ("world_forward_dir_x", ctypes.c_int16),  # World space forward X direction (normalised)
        ("world_forward_dir_y", ctypes.c_int16),  # World space forward Y direction (normalised)
        ("world_forward_dir_z", ctypes.c_int16),  # World space forward Z direction (normalised)
        ("world_right_dir_x", ctypes.c_int16),  # World space right X direction (normalised)
        ("world_right_dir_y", ctypes.c_int16),  # World space right Y direction (normalised)
        ("world_right_dir_z", ctypes.c_int16),  # World space right Z direction (normalised)
        ("g_force_lateral", ctypes.c_float),  # Lateral G-Force component
        ("g_force_longitudinal", ctypes.c_float),  # Longitudinal G-Force component
        ("g_force_vertical", ctypes.c_float),  # Vertical G-Force component
        ("yaw", ctypes.c_float),  # Yaw angle in radians
        ("pitch", ctypes.c_float),  # Pitch angle in radians
        ("roll", ctypes.c_float),  # Roll angle in radians
    ]


class PacketMotionData(Packet):
    """
    struct PacketMotionData
    {
        PacketHeader m_header; // Header
        CarMotionData m_carMotionData[22]; // Data for all cars on track
    };
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("car_motion_data", CarMotionData * 22),  # Data for all cars on track
    ]


class MarshalZone(Packet):
    """
    struct MarshalZone
    {
        float m_zoneStart; // Fraction (0..1) of way through the lap the marshal zone starts
        int8 m_zoneFlag; // -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow
    };
    """

    _fields_ = [
        ("zone_start", ctypes.c_float),  # Fraction (0..1) of way through the lap the marshal zone starts
        (
            "zone_flag",
            ctypes.c_int8,
        ),  # -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow, 4 = red
    ]


class WeatherForecastSample(Packet):
    """
    struct WeatherForecastSample
    {
        uint8 m_sessionType; // 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P, 5 = Q1
        // 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ, 10 = R, 11 = R2
        // 12 = R3, 13 = Time Trial
        uint8 m_timeOffset; // Time in minutes the forecast is for
        uint8 m_weather; // Weather - 0 = clear, 1 = light cloud, 2 = overcast
        // 3 = light rain, 4 = heavy rain, 5 = storm
        int8 m_trackTemperature; // Track temp. in degrees Celsius
        int8 m_trackTemperatureChange; // Track temp. change – 0 = up, 1 = down, 2 = no change
        int8 m_airTemperature; // Air temp. in degrees celsius
        int8 m_airTemperatureChange; // Air temp. change – 0 = up, 1 = down, 2 = no change
        uint8 m_rainPercentage; // Rain percentage (0-100)
    };
    """

    _fields_ = [
        # 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P, 5 = Q1
        # 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ, 10 = R, 11 = R2
        # 12 = R3, 13 = Time Trial
        ("session_type", ctypes.c_uint8),
        # Time in minutes the forecast is for
        # Weather - 0 = clear, 1 = light cloud, 2 = overcast
        # 3 = light rain, 4 = heavy rain, 5 = storm
        ("time_offset", ctypes.c_uint8),
        ("weather", ctypes.c_uint8),  # Weather - 0 = clear, 1 = light cloud, 2 = overcast
        ("track_temperature", ctypes.c_int8),  # Track temp. in degrees Celsius
        ("track_temperature_change", ctypes.c_int8),  # Track temp. change – 0 = up, 1 = down, 2 = no change
        ("air_temperature", ctypes.c_int8),  # Air temp. in degrees celsius
        ("air_temperature_change", ctypes.c_int8),  # Air temp. change – 0 = up, 1 = down, 2 = no change
        ("rain_percentage", ctypes.c_uint8),  # Rain percentage (0-100)
    ]


class PacketSessionData(Packet):
    """
    struct PacketSessionData
    {
        PacketHeader m_header; // Header
        uint8 m_weather; // Weather - 0 = clear, 1 = light cloud, 2 = overcast
        // 3 = light rain, 4 = heavy rain, 5 = storm
        int8 m_trackTemperature; // Track temp. in degrees celsius
        int8 m_airTemperature; // Air temp. in degrees celsius
        uint8 m_totalLaps; // Total number of laps in this race
        uint16 m_trackLength; // Track length in metres
        uint8 m_sessionType; // 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P
        // 5 = Q1, 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ
        // 10 = R, 11 = R2, 12 = R3, 13 = Time Trial
        int8 m_trackId; // -1 for unknown, see appendix
        uint8 m_formula; // Formula, 0 = F1 Modern, 1 = F1 Classic, 2 = F2,
        // 3 = F1 Generic, 4 = Beta, 5 = Supercars
        // 6 = Esports, 7 = F2 2021
        uint16 m_sessionTimeLeft; // Time left in session in seconds
        uint16 m_sessionDuration; // Session duration in seconds
        uint8 m_pitSpeedLimit; // Pit speed limit in kilometres per hour
        uint8 m_gamePaused; // Whether the game is paused – network game only
        uint8 m_isSpectating; // Whether the player is spectating
        uint8 m_spectatorCarIndex; // Index of the car being spectated
        uint8 m_sliProNativeSupport; // SLI Pro support, 0 = inactive, 1 = active
        uint8 m_numMarshalZones; // Number of marshal zones to follow
        MarshalZone m_marshalZones[21]; // List of marshal zones – max 21
        uint8 m_safetyCarStatus; // 0 = no safety car, 1 = full
        // 2 = virtual, 3 = formation lap
        uint8 m_networkGame; // 0 = offline, 1 = online
        uint8 m_numWeatherForecastSamples; // Number of weather samples to follow
        WeatherForecastSample m_weatherForecastSamples[56]; // Array of weather forecast samples
        uint8 m_forecastAccuracy; // 0 = Perfect, 1 = Approximate
        uint8 m_aiDifficulty; // AI Difficulty rating – 0-110
        uint32 m_seasonLinkIdentifier; // Identifier for season - persists across saves
        uint32 m_weekendLinkIdentifier; // Identifier for weekend - persists across saves
        uint32 m_sessionLinkIdentifier; // Identifier for session - persists across saves
        uint8 m_pitStopWindowIdealLap; // Ideal lap to pit on for current strategy (player)
        uint8 m_pitStopWindowLatestLap; // Latest lap to pit on for current strategy (player)
        uint8 m_pitStopRejoinPosition; // Predicted position to rejoin at (player)
        uint8 m_steeringAssist; // 0 = off, 1 = on
        uint8 m_brakingAssist; // 0 = off, 1 = low, 2 = medium, 3 = high
        uint8 m_gearboxAssist; // 1 = manual, 2 = manual & suggested gear, 3 = auto
        uint8 m_pitAssist; // 0 = off, 1 = on
        uint8 m_pitReleaseAssist; // 0 = off, 1 = on
        uint8 m_ERSAssist; // 0 = off, 1 = on
        uint8 m_DRSAssist; // 0 = off, 1 = on
        uint8 m_dynamicRacingLine; // 0 = off, 1 = corners only, 2 = full
        uint8 m_dynamicRacingLineType; // 0 = 2D, 1 = 3D
        uint8 m_gameMode; // Game mode id - see appendix
        uint8 m_ruleSet; // Ruleset - see appendix
        uint32 m_timeOfDay; // Local time of day - minutes since midnight
        uint8 m_sessionLength; // 0 = None, 2 = Very Short, 3 = Short, 4 = Medium
        // 5 = Medium Long, 6 = Long, 7 = Full
        uint8 m_speedUnitsLeadPlayer; // 0 = MPH, 1 = KPH
        uint8 m_temperatureUnitsLeadPlayer; // 0 = Celsius, 1 = Fahrenheit
        uint8 m_speedUnitsSecondaryPlayer; // 0 = MPH, 1 = KPH
        uint8 m_temperatureUnitsSecondaryPlayer; // 0 = Celsius, 1 = Fahrenheit
        uint8 m_numSafetyCarPeriods; // Number of safety cars called during session
        uint8 m_numVirtualSafetyCarPeriods; // Number of virtual safety cars called
        uint8 m_numRedFlagPeriods; // Number of red flags called during session
    };
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        # Weather - 0 = clear, 1 = light cloud, 2 = overcast
        # 3 = light rain, 4 = heavy rain, 5 = storm
        ("weather", ctypes.c_uint8),
        ("track_temperature", ctypes.c_int8),  # Track temp. in degrees celsius
        ("air_temperature", ctypes.c_int8),  # Air temp. in degrees celsius
        ("total_laps", ctypes.c_uint8),  # Total number of laps in this race
        ("track_length", ctypes.c_uint16),  # Track length in metres
        # 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P, 5 = Q1
        # 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ, 10 = R, 11 = R2
        # 12 = R3, 13 = Time Trial
        ("session_type", ctypes.c_uint8),
        ("track_id", ctypes.c_int8),  # -1 for unknown, see appendix
        # Formula, 0 = F1 Modern, 1 = F1 Classic, 2 = F2,
        # 3 = F1 Generic, 4 = Beta, 5 = Supercars
        # 6 = Esports, 7 = F2 2021
        ("formula", ctypes.c_uint8),
        ("session_time_left", ctypes.c_uint16),  # Time left in session in seconds
        ("session_duration", ctypes.c_uint16),  # Session duration in seconds
        ("pit_speed_limit", ctypes.c_uint8),  # Pit speed limit in kilometres per hour
        ("game_paused", ctypes.c_uint8),  # Whether the game is paused
        ("is_spectating", ctypes.c_uint8),  # Whether the player is spectating
        ("spectator_car_index", ctypes.c_uint8),  # Index of the car being spectated
        ("sli_pro_native_support", ctypes.c_uint8),  # SLI Pro support, 0 = inactive, 1 = active
        ("num_marshal_zones", ctypes.c_uint8),  # Number of marshal zones to follow
        ("marshal_zones", MarshalZone * 21),  # List of marshal zones – max 21
        ("safety_car_status", ctypes.c_uint8),  # 0 = no safety car, 1 = full, 2 = virtual, 3 = formation lap
        ("network_game", ctypes.c_uint8),  # 0 = offline, 1 = online
        ("num_weather_forecast_samples", ctypes.c_uint8),  # Number of weather samples to follow
        ("weather_forecast_samples", WeatherForecastSample * 56),  # Array of weather forecast samples
        ("forecast_accuracy", ctypes.c_uint8),  # 0 = Perfect, 1 = Approximate
        ("ai_difficulty", ctypes.c_uint8),  # AI Difficulty rating – 0-110
        ("season_link_identifier", ctypes.c_uint32),  # Identifier for season - persists across saves
        ("weekend_link_identifier", ctypes.c_uint32),  # Identifier for weekend - persists across saves
        ("session_link_identifier", ctypes.c_uint32),  # Identifier for session - persists across saves
        ("pit_stop_window_ideal_lap", ctypes.c_uint8),  # Ideal lap to pit on for current strategy (player)
        ("pit_stop_window_latest_lap", ctypes.c_uint8),  # Latest lap to pit on for current strategy (player)
        ("pit_stop_rejoin_position", ctypes.c_uint8),  # Predicted position to rejoin at (player)
        ("steering_assist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("braking_assist", ctypes.c_uint8),  # 0 = off, 1 = low, 2 = medium, 3 = high
        ("gearbox_assist", ctypes.c_uint8),  # 1 = manual, 2 = manual & suggested gear, 3 = auto
        ("pit_assist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("pit_release_assist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("ers_assist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("drs_assist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("dynamic_racing_line", ctypes.c_uint8),  # 0 = off, 1 = corners only, 2 = full
        ("dynamic_racing_line_type", ctypes.c_uint8),  # 0 = 2D, 1 = 3D
        ("game_mode", ctypes.c_uint8),  # Game mode id - see appendix
        ("rule_set", ctypes.c_uint8),  # Ruleset - see appendix
        ("time_of_day", ctypes.c_uint32),  # Local time of day - minutes since midnight
        ("session_length", ctypes.c_uint8),  # 0 = None, 2 = Very Short, 3 = Short, 4 = Medium
        # 5 = Medium Long, 6 = Long, 7 = Full
        ("speed_units_lead_player", ctypes.c_uint8),  # 0 = MPH, 1 = KPH
        ("temperature_units_lead_player", ctypes.c_uint8),  # 0 = Celsius, 1 = Fahrenheit
        ("speed_units_secondary_player", ctypes.c_uint8),  # 0 = MPH, 1 = KPH
        ("temperature_units_secondary_player", ctypes.c_uint8),  # 0 = Celsius, 1 = Fahrenheit
        ("num_safety_car_periods", ctypes.c_uint8),  # Number of safety cars called during session
        ("num_virtual_safety_car_periods", ctypes.c_uint8),  # Number of virtual safety cars called
        ("num_red_flag_periods", ctypes.c_uint8),  # Number of red flags called during session
    ]


class LapData(Packet):
    """
    The lap data packet gives details of all the cars in the session.
    Frequency: Rate as specified in menus
    Size: 1131 bytes
    Version: 1
    struct LapData
    {
        uint32 m_lastLapTimeInMS; // Last lap time in milliseconds
        uint32 m_currentLapTimeInMS; // Current time around the lap in milliseconds
        uint16 m_sector1TimeInMS; // Sector 1 time in milliseconds
        uint8 m_sector1TimeMinutes; // Sector 1 whole minute part
        uint16 m_sector2TimeInMS; // Sector 2 time in milliseconds
        uint8 m_sector2TimeMinutes; // Sector 2 whole minute part
        uint16 m_deltaToCarInFrontInMS; // Time delta to car in front in milliseconds
        uint16 m_deltaToRaceLeaderInMS; // Time delta to race leader in milliseconds
        float m_lapDistance; // Distance vehicle is around current lap in metres – could
        // be negative if line hasn’t been crossed yet
        float m_totalDistance; // Total distance travelled in session in metres – could
        // be negative if line hasn’t been crossed yet
        float m_safetyCarDelta; // Delta in seconds for safety car
        uint8 m_carPosition; // Car race position
        uint8 m_currentLapNum; // Current lap number
        uint8 m_pitStatus; // 0 = none, 1 = pitting, 2 = in pit area
        uint8 m_numPitStops; // Number of pit stops taken in this race
        uint8 m_sector; // 0 = sector1, 1 = sector2, 2 = sector3
        uint8 m_currentLapInvalid; // Current lap invalid - 0 = valid, 1 = invalid
        uint8 m_penalties; // Accumulated time penalties in seconds to be added
        uint8 m_totalWarnings; // Accumulated number of warnings issued
        uint8 m_cornerCuttingWarnings; // Accumulated number of corner cutting warnings issued
        uint8 m_numUnservedDriveThroughPens; // Num drive through pens left to serve
        uint8 m_numUnservedStopGoPens; // Num stop go pens left to serve
        uint8 m_gridPosition; // Grid position the vehicle started the race in
        uint8 m_driverStatus; // Status of driver - 0 = in garage, 1 = flying lap
        // 2 = in lap, 3 = out lap, 4 = on track
        uint8 m_resultStatus; // Result status - 0 = invalid, 1 = inactive, 2 = active
        // 3 = finished, 4 = didnotfinish, 5 = disqualified
        // 6 = not classified, 7 = retired
        uint8 m_pitLaneTimerActive; // Pit lane timing, 0 = inactive, 1 = active
        uint16 m_pitLaneTimeInLaneInMS; // If active, the current time spent in the pit lane in ms
        uint16 m_pitStopTimerInMS; // Time of the actual pit stop in ms
        uint8 m_pitStopShouldServePen; // Whether the car should serve a penalty at this stop
    };
    """

    _fields_ = [
        ("last_lap_time_in_ms", ctypes.c_uint32),  # Last lap time in milliseconds
        ("current_lap_time_in_ms", ctypes.c_uint32),  # Current time around the lap in milliseconds
        ("sector_1_time_in_ms", ctypes.c_uint16),  # Sector 1 time in milliseconds
        ("sector_1_time_minutes", ctypes.c_uint8),  # Sector 1 whole minute part
        ("sector_2_time_in_ms", ctypes.c_uint16),  # Sector 2 time in milliseconds
        ("sector_2_time_minutes", ctypes.c_uint8),  # Sector 2 whole minute part
        ("delta_to_car_in_front_in_ms", ctypes.c_uint16),  # Time delta to car in front, in milliseconds
        ("delta_to_race_leader_in_ms", ctypes.c_uint16),  # Time delta to race leader in milliseconds
        ("lap_distance", ctypes.c_float),  # Distance vehicle is around current lap in metres – could
        # be negative if line hasn’t been crossed yet
        ("total_distance", ctypes.c_float),  # Total distance travelled in session in metres – could
        # be negative if line hasn’t been crossed yet
        ("safety_car_delta", ctypes.c_float),  # Delta in seconds for safety car
        ("car_position", ctypes.c_uint8),  # Car race position
        ("current_lap_num", ctypes.c_uint8),  # Current lap number
        ("pit_status", ctypes.c_uint8),  # 0 = none, 1 = pitting, 2 = in pit area
        ("num_pit_stops", ctypes.c_uint8),  # Number of pit stops taken in this race
        ("sector", ctypes.c_uint8),  # 0 = sector1, 1 = sector2, 2 = sector3
        ("current_lap_invalid", ctypes.c_uint8),
        # Current lap invalid - 0 = valid, 1 = invalid
        ("penalties", ctypes.c_uint8),
        # Accumulated time penalties in seconds to be added
        ("total_warnings", ctypes.c_uint8),  # Accumulated number of warnings issued
        ("corner_cutting_warnings", ctypes.c_uint8),  # Accumulated number of corner cutting warnings issued
        ("num_unserved_drive_through_pens", ctypes.c_uint8),  # Num drive through pens left to serve
        ("num_unserved_stop_go_pens", ctypes.c_uint8),  # Num stop go pens left to serve
        ("grid_position", ctypes.c_uint8),  # Grid position the vehicle started the race in
        ("driver_status", ctypes.c_uint8),  # Status of driver - 0 = in garage, 1 = flying lap # 2 = in lap,
        # 3 = out lap, 4 = on track
        ("result_status", ctypes.c_uint8),  # Result status - 0 = invalid, 1 = inactive, 2 = active
        # 3 = finished, 4 = didnotfinish, 5 = disqualified
        # 6 = not classified, 7 = retired
        ("pit_lane_timer_active", ctypes.c_uint8),  # Pit lane timing, 0 = inactive, 1 = active
        ("pit_lane_time_in_lane_in_ms", ctypes.c_uint16),  # If active, the current time spent in the pit lane in ms
        ("pit_stop_timer_in_ms", ctypes.c_uint16),  # Time of the actual pit stop in ms
        ("pit_stop_should_serve_pen", ctypes.c_uint8),  # Whether the car should serve a penalty at this stop
    ]


class PacketLapData(Packet):
    """
    struct PacketLapData
    {
        PacketHeader m_header; // Header
        LapData m_lapData[22]; // Lap data for all cars on track
        uint8 m_timeTrialPBCarIdx; // Index of Personal Best car in time trial (255 if invalid)
        uint8 m_timeTrialRivalCarIdx; // Index of Rival car in time trial (255 if invalid)
    };
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("lap_data", LapData * 22),  # Lap data for all cars on track
        ("time_trial_pb_car_idx", ctypes.c_uint8),  # Index of Personal Best car in time trial (255 if invalid)
        ("time_trial_rival_car_idx", ctypes.c_uint8),  # Index of Rival car in time trial (255 if invalid)
    ]


class FastestLap(Packet):
    _fields_ = [
        ("vehicle_idx", ctypes.c_uint8),  # Vehicle index of car achieving fastest lap
        ("lap_time", ctypes.c_float),  # Lap time is in seconds
    ]


class Retirement(Packet):
    _fields_ = [
        ("vehicle_idx", ctypes.c_uint8),  # Vehicle index of car retiring
    ]


class TeamMateInPits(Packet):
    _fields_ = [
        ("vehicle_idx", ctypes.c_uint8),  # Vehicle index of team mate
    ]


class RaceWinner(Packet):
    _fields_ = [
        ("vehicle_idx", ctypes.c_uint8),  # Vehicle index of the race winner
    ]


class Penalty(Packet):
    _fields_ = [
        ("penalty_type", ctypes.c_uint8),  # Penalty type – see Appendices
        ("infringement_type", ctypes.c_uint8),  # Infringement type – see Appendices
        (
            "vehicle_idx",
            ctypes.c_uint8,
        ),  # Vehicle index of the car the penalty is applied to
        (
            "other_vehicle_idx",
            ctypes.c_uint8,
        ),  # Vehicle index of the other car involved
        ("time", ctypes.c_uint8),  # Time gained, or time spent doing action in seconds
        ("lap_num", ctypes.c_uint8),  # Lap the penalty occurred on
        ("places_gained", ctypes.c_uint8),  # Number of places gained by this
    ]


class SpeedTrap(Packet):
    _fields_ = [
        ("vehicle_idx", ctypes.c_uint8),  # Vehicle index of the vehicle triggering speed trap
        ("speed", ctypes.c_float),  # Top speed achieved in kilometres per hour
        ("overall_fastest_in_session", ctypes.c_uint8),  # Overall fastest speed in session = 1, otherwise 0
        ("is_driver_fastest_in_session", ctypes.c_uint8),  # Fastest speed for driver in session = 1, otherwise 0
        ("fastest_vehicle_idx_in_sSession", ctypes.c_uint8),  # Vehicle index of the vehicle that is the fastest
        # in this session
        ("fastest_speed_in_session", ctypes.c_float),  # Speed of the vehicle that is the fastest in this session
    ]


class StartLights(Packet):
    _fields_ = [
        ("num_lights", ctypes.c_uint8),  # Number of lights showing
    ]


class DriveThroughPenaltyServed(Packet):
    _fields_ = [
        ("vehicle_idx", ctypes.c_uint8),  # Vehicle index of the vehicle serving drive through
    ]


class StopGoPenaltyServed(Packet):
    _fields_ = [
        ("vehicle_idx", ctypes.c_uint8),  # Vehicle index of the vehicle serving stop go
    ]


class Flashback(Packet):
    _fields_ = [
        ("flashback_frame_identifier", ctypes.c_uint32),  # Frame identifier flashed back to
        ("flashback_session_time", ctypes.c_float),  # Session time flashed back to
    ]


class Buttons(Packet):
    _fields_ = [
        ("button_status", ctypes.c_uint32),  # Bit flags specifying which buttons are being pressed currently
        # - see appendices
    ]


class OverTake(Packet):
    _fields_ = [
        ("overtaking_vehicle_idx", ctypes.c_uint8),
        ("being_overtaken_vehicle_idx", ctypes.c_uint8),
    ]


class EventDataDetails(ctypes.Union, PacketMixin):
    _fields_ = [
        ("fastest_lap", FastestLap),
        ("retirement", Retirement),
        ("team_mate_in_pits", TeamMateInPits),
        ("race_winner", RaceWinner),
        ("penalty", Penalty),
        ("speed_trap", SpeedTrap),
        ("start_lights", StartLights),
        ("drive_through_penalty_served", DriveThroughPenaltyServed),
        ("stop_go_penalty_served", StopGoPenaltyServed),
        ("flashback", Flashback),
        ("buttons", Buttons),
        ("overtake", OverTake),
    ]


class PacketEventData(Packet):
    """
    Event                Code   Description
    Session Started      "SSTA" Sent when the session starts
    Session Ended        "SEND" Sent when the session ends
    Fastest Lap          "FTLP" When a driver achieves the fastest lap
    Retirement           "RTMT" When a driver retires
    DRS enabled          "DRSE" Race control have enabled DRS
    DRS disabled         "DRSD" Race control have disabled DRS
    Team mate in pits    "TMPT" Your team mate has entered the pits
    Chequered flag       "CHQF" The chequered flag has been waved
    Race Winner          "RCWN" The race winner is announced
    Penalty Issued       "PENA" A penalty has been issued – details in event
    Speed Trap Triggered "SPTP" Speed trap has been triggered by fastest speed
    Start lights         "STLG" Start lights – number shown
    Lights out           "LGOT" Lights out
    Drive through served "DTSV" Drive through penalty served
    Stop go served       "SGSV" Stop go penalty served
    Flashback            "FLBK" Flashback activated
    Button status        "BUTN" Button status changed
    Red Flag             "RDFL" Red flag shown
    Overtake             "OVTK" Overtake occurred
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("event_string_code", ctypes.c_uint8 * 4),  # Event string code, see below
        ("event_details", EventDataDetails),  # Event details - should be interpreted differently for each type
    ]


class ParticipantData(Packet):
    """
    struct ParticipantData
    {
        uint8 m_aiControlled; // Whether the vehicle is AI (1) or Human (0) controlled
        uint8 m_driverId; // Driver id - see appendix, 255 if network human
        uint8 m_networkId; // Network id – unique identifier for network players
        uint8 m_teamId; // Team id - see appendix
        uint8 m_myTeam; // My team flag – 1 = My Team, 0 = otherwise
        uint8 m_raceNumber; // Race number of the car
        uint8 m_nationality; // Nationality of the driver
        char m_name[48]; // Name of participant in UTF-8 format – null terminated
        // Will be truncated with ... (U+2026) if too long
        uint8 m_yourTelemetry; // The player's UDP setting, 0 = restricted, 1 = public
        uint8 m_showOnlineNames; // The player's show online names setting, 0 = off, 1 = on
        uint8 m_platform; // 1 = Steam, 3 = PlayStation, 4 = Xbox, 6 = Origin, 255 = unknown
    };
    """

    _fields_ = [
        ("ai_controlled", ctypes.c_uint8),  # Whether the vehicle is AI (1) or Human (0) controlled
        ("driver_id", ctypes.c_uint8),  # Driver id - see appendix, 255 if network human
        ("network_id", ctypes.c_uint8),  # Network id – unique identifier for network players
        ("team_id", ctypes.c_uint8),  # Team id - see appendix
        ("my_team", ctypes.c_uint8),  # My team flag – 1 = My Team, 0 = otherwise
        ("race_number", ctypes.c_uint8),  # Race number of the car
        ("nationality", ctypes.c_uint8),  # Nationality of the driver
        ("name", ctypes.c_char * 48),  # Name of participant in UTF-8 format – null terminated
        # Will be truncated with … (U+2026) if too long
        ("your_telemetry", ctypes.c_uint8),  # The player's UDP setting, 0 = restricted, 1 = public
        ("show_online_names", ctypes.c_uint8),  # The player's show online names setting, 0 = off, 1 = on
        ("platform", ctypes.c_uint8),  # 1 = Steam, 3 = PlayStation, 4 = Xbox, 6 = Origin, 255 = unknown
    ]


class PacketParticipantsData(Packet):
    """
    struct PacketParticipantsData
    {
        PacketHeader m_header; // Header
        uint8 m_numActiveCars; // Number of active cars in the data – should match number of cars on HUD
        ParticipantData m_participants[22];
    };
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("num_active_cars", ctypes.c_uint8),  # Number of active cars in the data – should match number of cars on HUD
        ("participants", ParticipantData * 22),
    ]


class CarSetupData(Packet):
    """
    struct CarSetupData
    {
        uint8 m_frontWing; // Front wing aero
        uint8 m_rearWing; // Rear wing aero
        uint8 m_onThrottle; // Differential adjustment on throttle (percentage)
        uint8 m_offThrottle; // Differential adjustment off throttle (percentage)
        float m_frontCamber; // Front camber angle (suspension geometry)
        float m_rearCamber; // Rear camber angle (suspension geometry)
        float m_frontToe; // Front toe angle (suspension geometry)
        float m_rearToe; // Rear toe angle (suspension geometry)
        uint8 m_frontSuspension; // Front suspension
        uint8 m_rearSuspension; // Rear suspension
        uint8 m_frontAntiRollBar; // Front anti-roll bar
        uint8 m_rearAntiRollBar; // Front anti-roll bar
        uint8 m_frontSuspensionHeight; // Front ride height
        uint8 m_rearSuspensionHeight; // Rear ride height
        uint8 m_brakePressure; // Brake pressure (percentage)
        uint8 m_brakeBias; // Brake bias (percentage)
        float m_rearLeftTyrePressure; // Rear left tyre pressure (PSI)
        float m_rearRightTyrePressure; // Rear right tyre pressure (PSI)
        float m_frontLeftTyrePressure; // Front left tyre pressure (PSI)
        float m_frontRightTyrePressure; // Front right tyre pressure (PSI)
        uint8 m_ballast; // Ballast
        float m_fuelLoad; // Fuel load
    };
    """

    _fields_ = [
        ("front_wing", ctypes.c_uint8),  # Front wing aero
        ("rear_wing", ctypes.c_uint8),  # Rear wing aero
        ("on_throttle", ctypes.c_uint8),  # Differential adjustment on throttle (percentage)
        ("off_throttle", ctypes.c_uint8),  # Differential adjustment off throttle (percentage)
        ("front_camber", ctypes.c_float),  # Front camber angle (suspension geometry)
        ("rear_camber", ctypes.c_float),  # Rear camber angle (suspension geometry)
        ("front_toe", ctypes.c_float),  # Front toe angle (suspension geometry)
        ("rear_toe", ctypes.c_float),  # Rear toe angle (suspension geometry)
        ("front_suspension", ctypes.c_uint8),  # Front suspension
        ("rear_suspension", ctypes.c_uint8),  # Rear suspension
        ("front_anti_roll_bar", ctypes.c_uint8),  # Front anti-roll bar
        ("rear_anti_roll_bar", ctypes.c_uint8),  # Front anti-roll bar
        ("front_suspension_height", ctypes.c_uint8),  # Front ride height
        ("rear_suspension_height", ctypes.c_uint8),  # Rear ride height
        ("brake_pressure", ctypes.c_uint8),  # Brake pressure (percentage)
        ("brake_bias", ctypes.c_uint8),  # Brake bias (percentage)
        ("rear_left_tyre_pressure", ctypes.c_float),  # Rear left tyre pressure (PSI)
        ("rear_right_tyre_pressure", ctypes.c_float),  # Rear right tyre pressure (PSI)
        ("front_left_tyre_pressure", ctypes.c_float),  # Front left tyre pressure (PSI)
        ("front_right_tyre_pressure", ctypes.c_float),  # Front right tyre pressure (PSI)
        ("ballast", ctypes.c_uint8),  # Ballast
        ("fuel_load", ctypes.c_float),  # Fuel load
    ]


class PacketCarSetupData(Packet):
    """
    struct PacketCarSetupData
    {
        PacketHeader m_header; // Header
        CarSetupData m_carSetups[22];
    };
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("car_setups", CarSetupData * 22),
    ]


class CarTelemetryData(Packet):
    """
    struct CarTelemetryData
    {
        uint16 m_speed; // Speed of car in kilometres per hour
        float m_throttle; // Amount of throttle applied (0.0 to 1.0)
        float m_steer; // Steering (-1.0 (full lock left) to 1.0 (full lock right))
        float m_brake; // Amount of brake applied (0.0 to 1.0)
        uint8 m_clutch; // Amount of clutch applied (0 to 100)
        int8 m_gear; // Gear selected (1-8, N=0, R=-1)
        uint16 m_engineRPM; // Engine RPM
        uint8 m_drs; // 0 = off, 1 = on
        uint8 m_revLightsPercent; // Rev lights indicator (percentage)
        uint16 m_revLightsBitValue; // Rev lights (bit 0 = leftmost LED, bit 14 = rightmost LED)
        uint16 m_brakesTemperature[4]; // Brakes temperature (celsius)
        uint8 m_tyresSurfaceTemperature[4]; // Tyres surface temperature (celsius)
        uint8 m_tyresInnerTemperature[4]; // Tyres inner temperature (celsius)
        uint16 m_engineTemperature; // Engine temperature (celsius)
        float m_tyresPressure[4]; // Tyres pressure (PSI)
        uint8 m_surfaceType[4]; // Driving surface, see appendices
    };
    """

    _fields_ = [
        ("speed", ctypes.c_uint16),  # Speed of car in kilometres per hour
        ("throttle", ctypes.c_float),  # Amount of throttle applied (0.0 to 1.0)
        ("steer", ctypes.c_float),  # Steering (-1.0 (full lock left) to 1.0 (full lock right))
        ("brake", ctypes.c_float),  # Amount of brake applied (0.0 to 1.0)
        ("clutch", ctypes.c_uint8),  # Amount of clutch applied (0 to 100)
        ("gear", ctypes.c_int8),  # Gear selected (1-8, N=0, R=-1)
        ("engine_rpm", ctypes.c_uint16),  # Engine RPM
        ("drs", ctypes.c_uint8),  # 0 = off, 1 = on
        ("rev_lights_percent", ctypes.c_uint8),  # Rev lights indicator (percentage)
        ("rev_lights_bit_value", ctypes.c_uint16),  # Rev lights (bit 0 = leftmost LED, bit 14 = rightmost LED)
        ("brakes_temperature", ctypes.c_uint16 * 4),  # Brakes temperature (celsius)
        ("tyres_surface_temperature", ctypes.c_uint8 * 4),  # Tyres surface temperature (celsius)
        ("tyres_inner_temperature", ctypes.c_uint8 * 4),  # Tyres inner temperature (celsius)
        ("engine_temperature", ctypes.c_uint16),  # Engine temperature (celsius)
        ("tyres_pressure", ctypes.c_float * 4),  # Tyres pressure (PSI)
        ("surface_type", ctypes.c_uint8 * 4),  # Driving surface, see appendices
    ]


class PacketCarTelemetryData(Packet):
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("car_telemetry_data", CarTelemetryData * 22),
        ("mfd_panel_index", ctypes.c_uint8),  # Index of MFD panel open - 255 = MFD closed
        # Single player, race – 0 = Car setup, 1 = Pits
        # 2 = Damage, 3 =  Engine, 4 = Temperatures
        # May vary depending on game mode
        ("mfd_panel_index_secondary_player", ctypes.c_uint8),  # See above
        ("suggested_gear", ctypes.c_int8),  # Suggested gear for the player (1-8), 0 if no gear suggested
    ]


class CarStatusData(Packet):
    """
    struct CarStatusData
    {
        uint8 m_tractionControl; // Traction control - 0 = off, 1 = medium, 2 = full
        uint8 m_antiLockBrakes; // 0 (off) - 1 (on)
        uint8 m_fuelMix; // Fuel mix - 0 = lean, 1 = standard, 2 = rich, 3 = max
        uint8 m_frontBrakeBias; // Front brake bias (percentage)
        uint8 m_pitLimiterStatus; // Pit limiter status - 0 = off, 1 = on
        float m_fuelInTank; // Current fuel mass
        float m_fuelCapacity; // Fuel capacity
        float m_fuelRemainingLaps; // Fuel remaining in terms of laps (value on MFD)
        uint16 m_maxRPM; // Cars max RPM, point of rev limiter
        uint16 m_idleRPM; // Cars idle RPM
        uint8 m_maxGears; // Maximum number of gears
        uint8 m_drsAllowed; // 0 = not allowed, 1 = allowed
        uint16 m_drsActivationDistance; // 0 = DRS not available, non-zero - DRS will be available
        // in [X] metres
        uint8 m_actualTyreCompound; // F1 Modern - 16 = C5, 17 = C4, 18 = C3, 19 = C2, 20 = C1
        // 21 = C0, 7 = inter, 8 = wet
        // F1 Classic - 9 = dry, 10 = wet
        // F2 – 11 = super soft, 12 = soft, 13 = medium, 14 = hard
        // 15 = wet
        uint8 m_visualTyreCompound; // F1 visual (can be different from actual compound)
        // 16 = soft, 17 = medium, 18 = hard, 7 = inter, 8 = wet
        // F1 Classic – same as above
        // F2 ‘19, 15 = wet, 19 – super soft, 20 = soft
        // 21 = medium , 22 = hard
        uint8 m_tyresAgeLaps; // Age in laps of the current set of tyres
        int8 m_vehicleFiaFlags; // -1 = invalid/unknown, 0 = none, 1 = green
        // 2 = blue, 3 = yellow
        float m_enginePowerICE; // Engine power output of ICE (W)
        float m_enginePowerMGUK; // Engine power output of MGU-K (W)
        float m_ersStoreEnergy; // ERS energy store in Joules
        uint8 m_ersDeployMode; // ERS deployment mode, 0 = none, 1 = medium
        // 2 = hotlap, 3 = overtake
        float m_ersHarvestedThisLapMGUK; // ERS energy harvested this lap by MGU-K
        float m_ersHarvestedThisLapMGUH; // ERS energy harvested this lap by MGU-H
        float m_ersDeployedThisLap; // ERS energy deployed this lap
        uint8 m_networkPaused; // Whether the car is paused in a network game
    };
    """

    _fields_ = [
        ("traction_control", ctypes.c_uint8),  # Traction control - 0 = off, 1 = medium, 2 = full
        ("anti_lock_brakes", ctypes.c_uint8),  # 0 (off) - 1 (on)
        ("fuel_mix", ctypes.c_uint8),  # Fuel mix - 0 = lean, 1 = standard, 2 = rich, 3 = max
        ("front_brake_bias", ctypes.c_uint8),  # Front brake bias (percentage)
        ("pit_limiter_status", ctypes.c_uint8),  # Pit limiter status - 0 = off, 1 = on
        ("fuel_in_tank", ctypes.c_float),  # Current fuel mass
        ("fuel_capacity", ctypes.c_float),  # Fuel capacity
        ("fuel_remaining_laps", ctypes.c_float),  # Fuel remaining in terms of laps (value on MFD)
        ("max_rpm", ctypes.c_uint16),  # Cars max RPM, point of rev limiter
        ("idle_rpm", ctypes.c_uint16),  # Cars idle RPM
        ("max_gears", ctypes.c_uint8),  # Maximum number of gears
        ("drs_allowed", ctypes.c_uint8),  # 0 = not allowed, 1 = allowed
        ("drs_activation_distance", ctypes.c_uint16),  # 0 = DRS not available, non-zero - DRS will be available
        # in [X] metres
        ("actual_tyre_compound", ctypes.c_uint8),  # F1 Modern - 16 = C5, 17 = C4, 18 = C3, 19 = C2, 20 = C1
        # 21 = C0, 7 = inter, 8 = wet
        # F1 Classic - 9 = dry, 10 = wet
        # F2 – 11 = super soft, 12 = soft, 13 = medium, 14 = hard
        # 15 = wet
        ("visual_tyre_compound", ctypes.c_uint8),  # F1 visual (can be different from actual compound)
        # 16 = soft, 17 = medium, 18 = hard, 7 = inter, 8 = wet
        # F1 Classic – same as above
        # F2 ‘19, 15 = wet, 19 – super soft, 20 = soft
        # 21 = medium , 22 = hard
        ("tyres_age_laps", ctypes.c_uint8),  # Age in laps of the current set of tyres
        ("vehicle_fia_flags", ctypes.c_int8),  # -1 = invalid/unknown, 0 = none, 1 = green 2 = blue, 3 = yellow, 4 = red
        ("engine_power_ice", ctypes.c_float),  # Engine power output of ICE (W)
        ("engine_power_mguk", ctypes.c_float),  # Engine power output of MGU-K (W)
        ("ers_store_energy", ctypes.c_float),  # ERS energy store in Joules
        ("ers_deploy_mode", ctypes.c_uint8),  # ERS deployment mode, 0 = none, 1 = medium 2 = hotlap, 3 = overtake
        ("ers_harvested_this_lap_mguk", ctypes.c_float),  # ERS energy harvested this lap by MGU-K
        ("ers_harvested_this_lap_mguh", ctypes.c_float),  # ERS energy harvested this lap by MGU-H
        ("ers_deployed_this_lap", ctypes.c_float),  # ERS energy deployed this lap
        (
            "network_paused",
            ctypes.c_uint8,
        ),  # Whether the car is paused in a network game
    ]


class PacketCarStatusData(Packet):
    """
    struct PacketCarStatusData
    {
        PacketHeader m_header; // Header
        CarStatusData m_carStatusData[22];
    };
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("car_status_data", CarStatusData * 22),
    ]


class FinalClassificationData(Packet):
    _fields_ = [
        ("position", ctypes.c_uint8),  # Finishing position
        ("num_laps", ctypes.c_uint8),  # Number of laps completed
        ("grid_position", ctypes.c_uint8),  # Grid position of the car
        ("points", ctypes.c_uint8),  # Number of points scored
        ("num_pit_stops", ctypes.c_uint8),  # Number of pit stops made
        ("result_status", ctypes.c_uint8),  # Result status - 0 = invalid, 1 = inactive, 2 = active
        # 3 = finished, 4 = didnotfinish, 5 = disqualified
        # 6 = not classified, 7 = retired
        ("best_lap_time_in_ms", ctypes.c_uint32),  # Best lap time of the session in milliseconds
        ("total_race_time", ctypes.c_double),  # Total race time in seconds without penalties
        ("penalties_time", ctypes.c_uint8),  # Total penalties accumulated in seconds
        ("num_penalties", ctypes.c_uint8),  # Number of penalties applied to this driver
        ("num_tyre_stints", ctypes.c_uint8),  # Number of tyres stints up to maximum
        ("tyre_stints_actual", ctypes.c_uint8 * 8),  # Actual tyres used by this driver
        ("tyre_stints_visual", ctypes.c_uint8 * 8),  # Visual tyres used by this driver
        ("tyre_stints_end_laps", ctypes.c_uint8 * 8),  # The lap number stints end on
    ]


class PacketFinalClassificationData(Packet):
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("num_cars", ctypes.c_uint8),  # Number of cars in the final classification
        ("classification_data", FinalClassificationData * 22),
    ]


class LobbyInfoData(Packet):
    _fields_ = [
        ("ai_controlled", ctypes.c_uint8),  # Whether the vehicle is AI (1) or Human (0) controlled
        ("team_id", ctypes.c_uint8),  # Team id - see appendix (255 if no team currently selected)
        ("nationality", ctypes.c_uint8),  # Nationality of the driver
        ("platform", ctypes.c_uint8),  # 1 = Steam, 3 = PlayStation, 4 = Xbox, 6 = Origin, 255 = unknown
        ("name", ctypes.c_char * 48),  # Name of participant in UTF-8 format – null terminated
        # Will be truncated with ... (U+2026) if too long
        ("car_number", ctypes.c_uint8),  # Car number of the player
        ("ready_status", ctypes.c_uint8),  # 0 = not ready, 1 = ready, 2 = spectating
    ]


class PacketLobbyInfoData(Packet):
    _fields_ = [
        ("header", PacketHeader),  # Header
        # Packet specific data
        ("num_players", ctypes.c_uint8),  # Number of players in the lobby data
        ("lobby_players", LobbyInfoData * 22),
    ]


class CarDamageData(Packet):
    """
    Car Damage Packet
    This packet details car damage parameters for all the cars in the race.
    Frequency: 10 per second
    Size: 953 bytes
    Version: 1
    struct CarDamageData
    {
        float m_tyresWear[4]; // Tyre wear (percentage)
        uint8 m_tyresDamage[4]; // Tyre damage (percentage)
        uint8 m_brakesDamage[4]; // Brakes damage (percentage)
        uint8 m_frontLeftWingDamage; // Front left wing damage (percentage)
        uint8 m_frontRightWingDamage; // Front right wing damage (percentage)
        uint8 m_rearWingDamage; // Rear wing damage (percentage)
        uint8 m_floorDamage; // Floor damage (percentage)
        uint8 m_diffuserDamage; // Diffuser damage (percentage)
        uint8 m_sidepodDamage; // Sidepod damage (percentage)
        uint8 m_drsFault; // Indicator for DRS fault, 0 = OK, 1 = fault
        uint8 m_ersFault; // Indicator for ERS fault, 0 = OK, 1 = fault
        uint8 m_gearBoxDamage; // Gear box damage (percentage)
        uint8 m_engineDamage; // Engine damage (percentage)
        uint8 m_engineMGUHWear; // Engine wear MGU-H (percentage)
        uint8 m_engineESWear; // Engine wear ES (percentage)
        uint8 m_engineCEWear; // Engine wear CE (percentage)
        uint8 m_engineICEWear; // Engine wear ICE (percentage)
        uint8 m_engineMGUKWear; // Engine wear MGU-K (percentage)
        uint8 m_engineTCWear; // Engine wear TC (percentage)
        uint8 m_engineBlown; // Engine blown, 0 = OK, 1 = fault
        uint8 m_engineSeized; // Engine seized, 0 = OK, 1 = fault
    }
    """

    _fields_ = [
        ("tyres_wear", ctypes.c_float * 4),  # Tyre wear (percentage)
        ("tyres_damage", ctypes.c_uint8 * 4),  # Tyre damage (percentage)
        ("brakes_damage", ctypes.c_uint8 * 4),  # Brakes damage (percentage)
        ("front_left_wing_damage", ctypes.c_uint8),  # Front left wing damage (percentage)
        ("front_right_wing_damage", ctypes.c_uint8),  # Front right wing damage (percentage)
        ("rear_wing_damage", ctypes.c_uint8),  # Rear wing damage (percentage)
        ("floor_damage", ctypes.c_uint8),  # Floor damage (percentage)
        ("diffuser_damage", ctypes.c_uint8),  # Diffuser damage (percentage)
        ("sidepod_damage", ctypes.c_uint8),  # Sidepod damage (percentage)
        ("drs_fault", ctypes.c_uint8),  # Indicator for DRS fault, 0 = OK, 1 = fault
        ("ers_fault", ctypes.c_uint8),  # Indicator for ERS fault, 0 = OK, 1 = fault
        ("gearbox_damage", ctypes.c_uint8),  # Gear box damage (percentage)
        ("engined_damage", ctypes.c_uint8),  # Engine damage (percentage)
        ("engine_mguh_wear", ctypes.c_uint8),  # Engine wear MGU-H (percentage)
        ("engine_energy_store_wear", ctypes.c_uint8),  # Engine wear ES (percentage)
        ("engine_control_electronics_wear", ctypes.c_uint8),  # Engine wear CE (percentage)
        ("engine_internal_combustion_engine_wear", ctypes.c_uint8),  # Engine wear ICE (percentage)
        ("engine_mguk_wear", ctypes.c_uint8),  # Engine wear MGU-K (percentage)
        ("engine_turbo_charger_wear", ctypes.c_uint8),  # Engine wear TC (percentage)
        ("engine_blown", ctypes.c_uint8),  # Engine blown, 0 = OK, 1 = fault
        ("engine_seized", ctypes.c_uint8),  # Engine seized, 0 = OK, 1 = fault
    ]


class PacketCarDamageData(Packet):
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("car_damage_data", CarDamageData * 22),
    ]


class LapHistoryData(Packet):
    """
    This packet contains lap times and tyre usage for the session. This packet works slightly differently
    to other packets. To reduce CPU and bandwidth, each packet relates to a specific vehicle and is
    sent every 1/20 s, and the vehicle being sent is cycled through. Therefore in a 20 car race you
    should receive an update for each vehicle at least once per second.
    Note that at the end of the race, after the final classification packet has been sent, a final bulk update
    of all the session histories for the vehicles in that session will be sent.
    Frequency: 20 per second but cycling through cars
    Size: 1460 bytes
    Version: 1
    struct LapHistoryData
    {
        uint32 m_lapTimeInMS; // Lap time in milliseconds
        uint16 m_sector1TimeInMS; // Sector 1 time in milliseconds
        uint8 m_sector1TimeMinutes; // Sector 1 whole minute part
        uint16 m_sector2TimeInMS; // Sector 2 time in milliseconds
        uint8 m_sector1TimeMinutes; // Sector 2 whole minute part
        uint16 m_sector3TimeInMS; // Sector 3 time in milliseconds
        uint8 m_sector3TimeMinutes; // Sector 3 whole minute part
        uint8 m_lapValidBitFlags; // 0x01 bit set-lap valid, 0x02 bit set-sector 1 valid
        // 0x04 bit set-sector 2 valid, 0x08 bit set-sector 3 valid
    };
    """

    _fields_ = [
        ("lap_time_in_ms", ctypes.c_uint32),  # Lap time in milliseconds
        ("sector1_time_in_ms", ctypes.c_uint16),  # Sector 1 time in milliseconds
        ("sector1_time_minutes", ctypes.c_uint8),  # Sector 1 whole minute part
        ("sector2_time_in_ms", ctypes.c_uint16),  # Sector 2 time in milliseconds
        ("sector2_time_minutes", ctypes.c_uint8),  # Sector 2 whole minute part
        ("sector3_time_in_ms", ctypes.c_uint16),  # Sector 3 time in milliseconds
        ("sector1_time_minutes", ctypes.c_uint8),  # Sector 3 whole minute part
        ("lap_valid_bit_flags", ctypes.c_uint8),  # 0x01 bit set-lap valid, 0x02 bit set-sector 1 valid
        # 0x04 bit set-sector 2 valid, 0x08 bit set-sector 3 valid
    ]


class TyreStintHistoryData(Packet):
    _fields_ = [
        # Lap the tyre usage ends on (255 of current tyre)
        ("end_lap", ctypes.c_uint8),
        ("tyre_actual_compound", ctypes.c_uint8),  # Actual tyres used by this driver
        ("tyre_visual_compound", ctypes.c_uint8),  # Visual tyres used by this driver
    ]


class PacketSessionHistoryData(Packet):
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("car_idx", ctypes.c_uint8),  # Index of the car this lap data relates to
        ("num_laps", ctypes.c_uint8),  # Num laps in the data (including current partial lap)
        ("num_tyre_stints", ctypes.c_uint8),  # Number of tyre stints in the data
        ("best_lap_time_lap_num", ctypes.c_uint8),  # Lap the best lap time was achieved on
        ("best_sector1_lap_num", ctypes.c_uint8),  # Lap the best Sector 1 time was achieved on
        ("best_sector2_lap_num", ctypes.c_uint8),  # Lap the best Sector 2 time was achieved on
        ("best_sector3_lap_num", ctypes.c_uint8),  # Lap the best Sector 3 time was achieved on
        ("lap_history_data", LapHistoryData * 100),  # 100 laps of data max
        ("tyre_stints_history_data", TyreStintHistoryData * 8),
    ]


class TyreSetData(Packet):
    """
    Tyre Sets Packet
    This packets gives a more in-depth details about tyre sets assigned to a vehicle during the session.
    Frequency: 20 per second but cycling through cars
    Size: 231 bytes
    Version: 1
    struct TyreSetData
    {
        uint8 m_actualTyreCompound; // Actual tyre compound used
        uint8 m_visualTyreCompound; // Visual tyre compound used
        uint8 m_wear; // Tyre wear (percentage)
        uint8 m_available; // Whether this set is currently available
        uint8 m_recommendedSession; // Recommended session for tyre set
        uint8 m_lifeSpan; // Laps left in this tyre set
        uint8 m_usableLife; // Max number of laps recommended for this compound
        int16 m_lapDeltaTime; // Lap delta time in milliseconds compared to fitted set
        uint8 m_fitted; // Whether the set is fitted or not
    };
    """

    _fields_ = [
        ("actual_tyre_compound", ctypes.c_uint8),  # Actual tyre compound used
        ("visual_tyre_compound", ctypes.c_uint8),  # Visual tyre compound used
        ("wear", ctypes.c_uint8),  # Tyre wear (percentage)
        ("available", ctypes.c_uint8),  # Whether this set is currently available
        ("recommended_session", ctypes.c_uint8),  # Recommended session for tyre set
        ("life_span", ctypes.c_uint8),  # Laps left in this tyre set
        ("usable_life", ctypes.c_uint8),  # Max number of laps recommended for this compound
        ("lap_delta_time", ctypes.c_uint16),  # Lap delta time in milliseconds compared to fitted set
        ("fitted", ctypes.c_uint8),  # Whether the set is fitted or not
    ]


class PacketTyreSetsData(Packet):
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("car_idx", ctypes.c_uint8),  # Index of the car this data relates to
        ("tyre_set_data", TyreSetData * 20),  # 13 (dry) + 7 (wet)
        ("fitted_idx", ctypes.c_uint8),  # Index into array of fitted tyre
    ]


class PacketMotionExData(Packet):
    """
    The motion packet gives extended data for the car being driven with the goal of being able to drive a
    motion platform setup.
    Frequency: Rate as specified in menus
    Size: 217 bytes
    Version: 1
    struct PacketMotionExData
    {
        PacketHeader m_header; // Header
        // Extra player car ONLY data
        float m_suspensionPosition[4]; // Note: All wheel arrays have the following order:
        float m_suspensionVelocity[4]; // RL, RR, FL, FR
        float m_suspensionAcceleration[4]; // RL, RR, FL, FR
        float m_wheelSpeed[4]; // Speed of each wheel
        float m_wheelSlipRatio[4]; // Slip ratio for each wheel
        float m_wheelSlipAngle[4]; // Slip angles for each wheel
        float m_wheelLatForce[4]; // Lateral forces for each wheel
        float m_wheelLongForce[4]; // Longitudinal forces for each wheel

        float m_heightOfCOGAboveGround; // Height of centre of gravity above ground
        float m_localVelocityX; // Velocity in local space – metres/s
        float m_localVelocityY; // Velocity in local space
        float m_localVelocityZ; // Velocity in local space
        float m_angularVelocityX; // Angular velocity x-component – radians/s
        float m_angularVelocityY; // Angular velocity y-component
        float m_angularVelocityZ; // Angular velocity z-component

        float m_angularAccelerationX; // Angular acceleration x-component – radians/s/s
        float m_angularAccelerationY; // Angular acceleration y-component
        float m_angularAccelerationZ; // Angular acceleration z-component
        float m_frontWheelsAngle; // Current front wheels angle in radians
        float m_wheelVertForce[4]; // Vertical forces for each wheel
    };
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("m_suspensionPosition", ctypes.c_float * 4),  # Note: All wheel arrays have the following order:
        ("m_suspensionVelocity", ctypes.c_float * 4),  # RL, RR, FL, FR
        ("m_suspensionAcceleration", ctypes.c_float * 4),  # RL, RR, FL, FR
        ("m_wheelSpeed", ctypes.c_float * 4),  # Speed of each wheel
        ("m_wheelSlipRatio", ctypes.c_float * 4),  # Slip ratio for each wheel
        ("m_wheelSlipAngle", ctypes.c_float * 4),  # Slip angles for each wheel
        ("m_wheelLatForce", ctypes.c_float * 4),  # Lateral forces for each wheel
        ("m_wheelLongForce", ctypes.c_float * 4),  # Longitudinal forces for each wheel
        ("m_heightOfCOGAboveGround", ctypes.c_float),  # Height of centre of gravity above ground
        ("m_localVelocityX", ctypes.c_float),  # Velocity in local space – metres/s
        ("m_localVelocityY", ctypes.c_float),  # Velocity in local space
        ("m_localVelocityZ", ctypes.c_float),  # Velocity in local space
        ("m_angularVelocityX", ctypes.c_float),  # Angular velocity x-component – radians/s
        ("m_angularVelocityY", ctypes.c_float),  # Angular velocity y-component
        ("m_angularVelocityZ", ctypes.c_float),  # Angular velocity z-component
        ("m_angularAccelerationX", ctypes.c_float),  # Angular acceleration x-component – radians/s/s
        ("m_angularAccelerationY", ctypes.c_float),  # Angular acceleration y-component
        ("m_angularAccelerationZ", ctypes.c_float),  # Angular acceleration z-component
        ("m_frontWheelsAngle", ctypes.c_float),  # Current front wheels angle in radians
        ("m_wheelVertForce", ctypes.c_float),  # Vertical forces for each wheel
    ]


HEADER_FIELD_TO_PACKET_TYPE = {
    (2023, 1, 0): PacketMotionData,
    (2023, 1, 1): PacketSessionData,
    (2023, 1, 2): PacketLapData,
    (2023, 1, 3): PacketEventData,
    (2023, 1, 4): PacketParticipantsData,
    (2023, 1, 5): PacketCarSetupData,
    (2023, 1, 6): PacketCarTelemetryData,
    (2023, 1, 7): PacketCarStatusData,
    (2023, 1, 8): PacketFinalClassificationData,
    (2023, 1, 9): PacketLobbyInfoData,
    (2023, 1, 10): PacketCarDamageData,
    (2023, 1, 11): PacketSessionHistoryData,
    (2023, 1, 12): PacketTyreSetsData,
    (2023, 1, 13): PacketMotionExData,
}

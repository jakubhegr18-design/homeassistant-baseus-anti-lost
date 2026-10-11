"""Constants for the Baseus Anti-Lost T2 integration."""

DOMAIN = "baseus_anti_lost"

# Configuration keys
CONF_ADDRESS = "address"
CONF_MODE = "mode"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_RSSI_THRESHOLD = "rssi_threshold"
CONF_OUT_OF_RANGE_TIMEOUT = "out_of_range_timeout"
CONF_NOTIFY_WHEN_LOST = "notify_when_lost"
CONF_ENABLE_LOCATION = "enable_location_tracking"

# Config modes
MODE_BLUETOOTH = "bluetooth"
MODE_ACCOUNT = "account"

# Defaults
DEFAULT_RSSI_THRESHOLD = -80
DEFAULT_OUT_OF_RANGE_TIMEOUT = 300
DEFAULT_NOTIFY_WHEN_LOST = True
DEFAULT_ENABLE_LOCATION = True

# Services
SERVICE_START_TRACKING = "start_tracking"
SERVICE_STOP_TRACKING = "stop_tracking"
SERVICE_RESET_DEVICE = "reset_device"

# Device states
STATE_SAFE = "safe"
STATE_LOST = "lost"
STATE_OUT_OF_RANGE = "out_of_range"
STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"

# Sensor keys
SENSOR_SIGNAL_STRENGTH = "signal_strength"
SENSOR_CONNECTION_STATUS = "connection_status"
SENSOR_LAST_SEEN = "last_seen"
SENSOR_BATTERY_LEVEL = "battery_level"
SENSOR_TRACKING_STATUS = "tracking_status"
SENSOR_DISTANCE_ESTIMATE = "distance_estimate"

BINARY_SENSOR_DEVICE_LOST = "device_lost"
BINARY_SENSOR_BLUETOOTH_CONNECTED = "bluetooth_connected"

SWITCH_ANTI_LOST = "anti_lost_enabled"

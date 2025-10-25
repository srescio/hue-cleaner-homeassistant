"""Constants for the Hue Cleaner integration."""

DOMAIN = "hue_cleaner"

# Configuration keys
CONF_HUE_IP = "hue_ip"
CONF_API_KEY = "api_key"

# Default values
DEFAULT_SCAN_INTERVAL = 7200  # 2 hours in seconds
DEFAULT_TIMEOUT = 10

# API endpoints
HUE_API_BASE = "http://{ip}/api"
HUE_ENTERTAINMENT_API = "https://{ip}/clip/v2/resource/entertainment_configuration"

# Entertainment area patterns
ENTERTAINMENT_AREA_NAME_PATTERN = "Entertainment area"
ENTERTAINMENT_AREA_INACTIVE_STATUS = "inactive"

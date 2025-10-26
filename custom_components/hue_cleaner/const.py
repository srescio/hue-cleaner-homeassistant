"""Constants for the Hue Cleaner integration."""

DOMAIN = "hue_cleaner"

# Configuration keys
CONF_HUE_IP = "hue_ip"
CONF_API_KEY = "api_key"

# Default values
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour in seconds (fallback polling)
DEFAULT_TIMEOUT = 10
DEFAULT_CLEANUP_DELAY = 5  # seconds to wait before cleaning after new area detection

# API endpoints
HUE_API_BASE = "https://{ip}/api"
HUE_ENTERTAINMENT_API = "https://{ip}/clip/v2/resource/entertainment_configuration"

# Entertainment area patterns
ENTERTAINMENT_AREA_NAME_PATTERN = "Entertainment area"
ENTERTAINMENT_AREA_INACTIVE_STATUS = "inactive"

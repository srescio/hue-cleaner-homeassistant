"""Config flow for Hue Cleaner integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, HUE_API_BASE

_LOGGER = logging.getLogger(__name__)

# Step 1: IP Input
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)

# Step 2: Connection Test (no input needed)
STEP_CONNECTION_TEST_SCHEMA = vol.Schema({})

# Step 3: API Instructions (no input needed)
STEP_API_INSTRUCTIONS_SCHEMA = vol.Schema({})

# Step 4: API Key Input
STEP_API_KEY_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_key"): str,
    }
)

# Step 5: Final Test (no input needed)
STEP_FINAL_TEST_SCHEMA = vol.Schema({})


class HueCleanerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hue Cleaner."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.hue_ip = None
        self.api_key = None
        self.connection_tested = False
        self.api_key_tested = False

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Handle IP input."""
        errors: dict[str, str] = {}

        if user_input is not None:
            hue_ip = user_input[CONF_HOST]
            
            # Validate IP format
            if not self._is_valid_ip(hue_ip):
                errors["base"] = "invalid_ip"
            else:
                self.hue_ip = hue_ip
                return await self.async_step_connection_test()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "instructions": self._get_translation("instructions", "find_ip"),
                "example": self._get_translation("instructions", "example_ip")
            }
        )

    async def async_step_connection_test(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Test connection to Hue Hub."""
        if user_input is not None:
            # Test connection
            if await self._test_connection(self.hue_ip):
                self.connection_tested = True
                return await self.async_step_api_instructions()
            else:
                return self.async_show_form(
                    step_id="connection_test",
                    data_schema=STEP_CONNECTION_TEST_SCHEMA,
                    errors={"base": "cannot_connect"}
                )

        return self.async_show_form(
            step_id="connection_test",
            data_schema=STEP_CONNECTION_TEST_SCHEMA,
            description_placeholders={
                "hue_ip": self.hue_ip,
                "status": self._get_translation("status", "testing_connection")
            }
        )

    async def async_step_api_instructions(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 3: Show API key instructions."""
        if user_input is not None:
            return await self.async_step_api_key()

        return self.async_show_form(
            step_id="api_instructions",
            data_schema=STEP_API_INSTRUCTIONS_SCHEMA,
            description_placeholders={
                "hue_ip": self.hue_ip,
                "status": self._get_translation("status", "connection_successful")
            }
        )

    async def async_step_api_key(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 4: Handle API key input."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input["api_key"]
            
            # Test API key
            if await self._test_api_key(self.hue_ip, api_key):
                self.api_key = api_key
                self.api_key_tested = True
                return await self.async_step_final_test()
            else:
                errors["base"] = "invalid_api_key"

        return self.async_show_form(
            step_id="api_key",
            data_schema=STEP_API_KEY_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "hue_ip": self.hue_ip,
                "instructions": self._get_translation("instructions", "api_key_steps")
            }
        )

    async def async_step_final_test(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 5: Final test and create entry."""
        if user_input is not None:
            # Perform final test
            if await self._test_api_key(self.hue_ip, self.api_key):
                return self.async_create_entry(
                    title=f"Hue Cleaner ({self.hue_ip})",
                    data={
                        CONF_HOST: self.hue_ip,
                        "api_key": self.api_key,
                    },
                )
            else:
                return self.async_show_form(
                    step_id="final_test",
                    data_schema=STEP_FINAL_TEST_SCHEMA,
                    errors={"base": "final_test_failed"}
                )

        return self.async_show_form(
            step_id="final_test",
            data_schema=STEP_FINAL_TEST_SCHEMA,
            description_placeholders={
                "hue_ip": self.hue_ip,
                "status": self._get_translation("status", "final_test_progress")
            }
        )

    def _get_translation(self, category: str, key: str) -> str:
        """Get translation for a specific key."""
        try:
            # Get the current language
            language = self.hass.config.language
            
            # Load translations for this integration
            translations = self.hass.data.get("frontend_translations", {}).get("hue_cleaner", {})
            if not translations:
                # Fallback to English if no translations found
                language = "en"
                translations = self.hass.data.get("frontend_translations", {}).get("hue_cleaner", {})
            
            # Try to get the translation
            if language in translations:
                return translations[language].get("config", {}).get(category, {}).get(key, f"Missing: {key}")
            else:
                # Fallback to English
                return translations.get("en", {}).get("config", {}).get(category, {}).get(key, f"Missing: {key}")
        except Exception:
            # Ultimate fallback
            return f"Missing: {key}"

    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format."""
        pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
        return bool(re.match(pattern, ip))

    async def _test_connection(self, hue_ip: str) -> bool:
        """Test connection to Hue Hub."""
        try:
            session = aiohttp_client.async_get_clientsession(self.hass)
            url = HUE_API_BASE.format(ip=hue_ip)
            
            async with session.post(
                url,
                json={"devicetype": "hue_cleaner#homeassistant"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if we get the expected response (either error 101 or success)
                    return (
                        len(data) > 0 and
                        (data[0].get("error", {}).get("type") == 101 or
                         "success" in data[0])
                    )
        except Exception:
            pass
        return False

    async def _test_api_key(self, hue_ip: str, api_key: str) -> bool:
        """Test API key validity."""
        try:
            session = aiohttp_client.async_get_clientsession(self.hass)
            url = f"https://{hue_ip}/clip/v2/resource/entertainment_configuration"
            
            async with session.get(
                url,
                headers={"hue-application-key": api_key},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                return response.status == 200
        except Exception:
            pass
        return False

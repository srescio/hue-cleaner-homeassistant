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
from homeassistant.helpers import issue_registry

from .const import DOMAIN, HUE_API_BASE

_LOGGER = logging.getLogger(__name__)

# Step 1: IP Input
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)

# Step 2: API Key Generation (no input needed)
STEP_API_KEY_DATA_SCHEMA = vol.Schema({})

# Step 3: Retry API Key (with back button)
STEP_RETRY_API_KEY_SCHEMA = vol.Schema({
    vol.Optional("retry"): bool,
    vol.Optional("back"): bool,
})

# Step 4: Final Test (no input needed)
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
                # Test connection to Hue Hub
                if await self._test_connection(hue_ip):
                    self.hue_ip = hue_ip
                    return await self.async_step_api_key()
                else:
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors
        )



    async def async_step_api_key(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Handle API key generation."""
        if user_input is not None:
            # Try to get API key from hub
            api_key = await self._fetch_api_key(self.hue_ip)
            if api_key:
                self.api_key = api_key
                return await self.async_step_final_test()
            else:
                # No API key received, offer to retry
                return await self.async_step_retry_api_key()

        return self.async_show_form(
            step_id="api_key",
            data_schema=STEP_API_KEY_DATA_SCHEMA
        )

    async def async_step_final_test(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 4: Final test and create entry."""
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
            data_schema=STEP_FINAL_TEST_SCHEMA
        )

    async def async_step_retry_api_key(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 3: Retry API key generation."""
        if user_input is not None:
            # Check if user wants to go back
            if user_input.get("back"):
                return await self.async_step_api_key()
            
            # Check if user wants to retry
            if user_input.get("retry"):
                # Try to get API key from hub again
                api_key = await self._fetch_api_key(self.hue_ip)
                if api_key:
                    self.api_key = api_key
                    return await self.async_step_final_test()
                else:
                    # Still no API key, show error
                    return self.async_show_form(
                        step_id="retry_api_key",
                        data_schema=STEP_RETRY_API_KEY_SCHEMA,
                        errors={"base": "api_key_timeout"}
                    )

        return self.async_show_form(
            step_id="retry_api_key",
            data_schema=STEP_RETRY_API_KEY_SCHEMA
        )

    async def async_step_issue_repair(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle repair flow for issues."""
        if user_input is not None:
            # Get the issue context
            issue_id = self.context.get("issue_id", "")
            
            if "ip_change" in issue_id:
                # Handle IP change repair
                new_ip = user_input.get(CONF_HOST)
                if new_ip and self._is_valid_ip(new_ip):
                    if await self._test_connection(new_ip):
                        self.hue_ip = new_ip
                        return await self.async_step_api_key()
                    else:
                        return self.async_show_form(
                            step_id="issue_repair",
                            data_schema=STEP_USER_DATA_SCHEMA,
                            errors={"base": "cannot_connect"}
                        )
                else:
                    return self.async_show_form(
                        step_id="issue_repair",
                        data_schema=STEP_USER_DATA_SCHEMA,
                        errors={"base": "invalid_ip"}
                    )
            elif "api_key_expired" in issue_id:
                # Handle API key repair
                if await self._test_connection(self.hue_ip):
                    return await self.async_step_api_key()
                else:
                    return self.async_show_form(
                        step_id="issue_repair",
                        data_schema=STEP_USER_DATA_SCHEMA,
                        errors={"base": "cannot_connect"}
                    )

        # Show repair form
        issue_id = self.context.get("issue_id", "")
        if "ip_change" in issue_id:
            return self.async_show_form(
                step_id="issue_repair",
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "issue_description": "The Hue Hub IP address has changed. Please enter the new IP address."
                }
            )
        else:
            return self.async_show_form(
                step_id="issue_repair",
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "issue_description": "The Hue Hub connection failed. Please check the IP address and try again."
                }
            )

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

    async def _fetch_api_key(self, hue_ip: str) -> str | None:
        """Fetch API key from Hue Hub (user must press button first)."""
        try:
            session = aiohttp_client.async_get_clientsession(self.hass)
            url = f"http://{hue_ip}/api"
            
            payload = {
                "devicetype": "hue_cleaner#homeassistant",
                "generateclientkey": True
            }
            
            async with session.post(url, json=payload, ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        result = data[0]
                        if "success" in result and "username" in result["success"]:
                            return result["success"]["username"]
                        elif "error" in result:
                            # Error 101 means "link button not pressed"
                            if result["error"].get("type") == 101:
                                return None  # Continue polling
        except Exception:
            pass
        return None

    async def _test_api_key(self, hue_ip: str, api_key: str) -> bool:
        """Test API key validity."""
        try:
            session = aiohttp_client.async_get_clientsession(self.hass)
            url = f"http://{hue_ip}/clip/v2/resource/entertainment_configuration"
            
            async with session.get(
                url,
                headers={"hue-application-key": api_key},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                return response.status == 200
        except Exception:
            pass
        return False

#!/bin/bash
set -e

echo "Setting up Home Assistant development environment..."

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    ffmpeg \
    libturbojpeg0-dev \
    libpcap-dev \
    libjpeg-dev \
    zlib1g-dev

# Upgrade pip
pip install --upgrade pip

# Install Home Assistant
echo "Installing Home Assistant..."
pip install homeassistant

# Install development dependencies
echo "Installing development dependencies..."
pip install debugpy
pip install -r requirements_dev.txt

# Install pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

# Create symlink for custom component
echo "Creating symlink for custom component..."
mkdir -p /workspaces/hue-cleaner-homeassistant/config/custom_components
rm -f /workspaces/hue-cleaner-homeassistant/config/custom_components/hue_cleaner
ln -s /workspaces/hue-cleaner-homeassistant/custom_components/hue_cleaner /workspaces/hue-cleaner-homeassistant/config/custom_components/hue_cleaner

# Install HACS (only if not already installed)
if [ ! -d "/workspaces/hue-cleaner-homeassistant/config/custom_components/hacs" ]; then
  echo "Installing HACS..."
  HACS_VERSION=$(curl -s https://api.github.com/repos/hacs/integration/releases/latest | grep "tag_name" | cut -d '"' -f 4)
  echo "Downloading HACS version ${HACS_VERSION}..."
  wget -q -O /tmp/hacs.zip "https://github.com/hacs/integration/releases/download/${HACS_VERSION}/hacs.zip"
  unzip -q /tmp/hacs.zip -d /workspaces/hue-cleaner-homeassistant/config/custom_components/hacs
  rm /tmp/hacs.zip
  echo "HACS installed successfully!"
else
  echo "HACS already installed, skipping..."
fi

# Create redirect panel JS file if it doesn't exist
if [ ! -f "/workspaces/hue-cleaner-homeassistant/config/www/redirect-panel.js" ]; then
  echo "Creating redirect panel JavaScript..."
  mkdir -p /workspaces/hue-cleaner-homeassistant/config/www
  cat > /workspaces/hue-cleaner-homeassistant/config/www/redirect-panel.js << 'EOF'
class RedirectPanel extends HTMLElement {
  connectedCallback() {
    const url = this.config.url;
    if (url) {
      window.location.href = url;
    }
  }

  setConfig(config) {
    this.config = config;
  }
}

customElements.define('redirect-panel', RedirectPanel);
EOF
  echo "Redirect panel created!"
else
  echo "Redirect panel already exists, skipping..."
fi

# Add panel_custom to configuration.yaml if not present
if ! grep -q "panel_custom:" /workspaces/hue-cleaner-homeassistant/config/configuration.yaml; then
  echo "Adding custom sidebar links to configuration.yaml..."
  cat >> /workspaces/hue-cleaner-homeassistant/config/configuration.yaml << 'EOF'

# Custom sidebar links
panel_custom:
  - name: dev-integrations
    sidebar_title: "Integrations"
    sidebar_icon: mdi:puzzle
    url_path: config/integrations
    module_url: /local/redirect-panel.js
    config:
      url: /config/integrations
  - name: dev-entities
    sidebar_title: "Entities"
    sidebar_icon: mdi:format-list-bulleted
    url_path: config/entities
    module_url: /local/redirect-panel.js
    config:
      url: /config/entities
  - name: dev-logs
    sidebar_title: "Logs"
    sidebar_icon: mdi:math-log
    url_path: config/logs
    module_url: /local/redirect-panel.js
    config:
      url: /config/logs
EOF
  echo "Custom sidebar links configured!"
else
  echo "Custom sidebar links already configured, skipping..."
fi

# Print helpful URLs
echo ""
echo "===================================="
echo "Useful development URLs:"
echo "===================================="
echo "  Integrations: http://localhost:8123/config/integrations"
echo "  Devices:      http://localhost:8123/config/devices/dashboard"
echo "  Entities:     http://localhost:8123/config/entities"
echo "  Logs:         http://localhost:8123/config/logs"
echo "  Dev Tools:    http://localhost:8123/developer-tools/state"
echo "===================================="
echo ""
echo "Tip: Use the custom sidebar links for quick access!"

echo ""
echo "Setup complete!"
echo "=================="
echo "You can now start Home Assistant with: hass -c config"
echo ""
echo "Quick commands:"
echo "  - Start HA: hass -c config"
echo "  - View URLs: ./open-integrations.sh"
echo "=================="


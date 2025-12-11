#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paths - Crucial for the Python "relative path" logic
INSTALL_DIR="$HOME/.local/share/pokefact"
BIN_DIR="$HOME/.local/bin"
EXECUTABLE="$BIN_DIR/pokefact"
ART_REPO="https://gitlab.com/phoneybadger/pokemon-colorscripts.git"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      PokeFact Universal Installer      ${NC}"
echo -e "${BLUE}========================================${NC}"

# --- 1. DETECT OS & INSTALL SYSTEM DEPENDENCIES ---
echo -e "${GREEN}[*] Checking System Dependencies...${NC}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}[!] Error: Homebrew is required for macOS.${NC}"
        exit 1
    fi
    echo "    -> macOS detected. Installing mpv, python, git..."
    brew install mpv python3 git

elif [ -f /etc/arch-release ]; then
    # Arch Linux
    echo "    -> Arch Linux detected. Installing dependencies..."
    sudo pacman -S --noconfirm mpv python git base-devel

elif [ -f /etc/debian_version ]; then
    # Ubuntu / Kali / Debian
    echo "    -> Debian/Ubuntu detected. Installing dependencies..."
    sudo apt update && sudo apt install -y mpv python3 python3-venv git

elif [ -f /etc/fedora-release ]; then
    # Fedora
    echo "    -> Fedora detected. Installing dependencies..."
    sudo dnf install -y mpv python3 git

else
    echo -e "${RED}[!] Unknown OS. Attempting to proceed, but dependencies might be missing.${NC}"
fi

# --- 2. CLEAN & PREPARE DIRECTORIES ---
echo -e "${GREEN}[*] Setting up install directory at $INSTALL_DIR...${NC}"

# Wipe old installs to prevent conflicts
rm -rf "$INSTALL_DIR"

# Create the specific structure the Python script expects:
#   ~/.local/share/pokefact/
#       ├── src/              <-- Script goes here
#       └── pokemon-colorscripts/  <-- Art goes here
mkdir -p "$INSTALL_DIR/src"
mkdir -p "$BIN_DIR"

# --- 3. INSTALL SOURCE CODE ---
echo -e "${GREEN}[*] Copying project files...${NC}"
if [ ! -f "src/pokefact.py" ]; then
   echo -e "${RED}[!] Error: src/pokefact.py not found in current directory!${NC}"
   exit 1
fi

cp src/pokefact.py "$INSTALL_DIR/src/"
cp requirements.txt "$INSTALL_DIR/"

# --- 4. DOWNLOAD ART ASSETS ---
echo -e "${GREEN}[*] Downloading ASCII Art database...${NC}"
# Cloning into the root install dir so it sits next to 'src'
git clone --depth 1 "$ART_REPO" "$INSTALL_DIR/pokemon-colorscripts" > /dev/null 2>&1

# --- 5. SETUP PYTHON ENVIRONMENT ---
echo -e "${GREEN}[*] Setting up isolated Python environment...${NC}"
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

# Upgrade pip first to avoid errors
pip install --upgrade pip > /dev/null 2>&1
echo "    -> Installing libraries (rich, requests)..."
pip install -q -r "$INSTALL_DIR/requirements.txt"

# --- 6. CREATE LAUNCHER ---
echo -e "${GREEN}[*] Creating 'pokefact' command...${NC}"
cat <<EOF > "$EXECUTABLE"
#!/bin/bash
# Launch the script using the isolated virtual environment
"$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/src/pokefact.py" "\$@"
EOF
chmod +x "$EXECUTABLE"

# --- 7. PATH VERIFICATION ---
# Check if ~/.local/bin is actually in the user's PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${RED}[!] Warning: $HOME/.local/bin is not in your PATH.${NC}"
    echo "    To fix this permanently, run this command:"
    
    SHELL_NAME=$(basename "$SHELL")
    if [ "$SHELL_NAME" = "zsh" ]; then
        echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc"
    elif [ "$SHELL_NAME" = "bash" ]; then
        echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc"
    else
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
fi

echo -e "${GREEN}[✔] Installation Complete! Type 'pokefact' to start.${NC}"

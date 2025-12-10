#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Install Locations
INSTALL_DIR="$HOME/.local/share/pokefact"
BIN_DIR="$HOME/.local/bin"
EXECUTABLE="$BIN_DIR/pokefact"
ART_REPO="https://gitlab.com/phoneybadger/pokemon-colorscripts.git"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      PokeFact Universal Installer      ${NC}"
echo -e "${BLUE}========================================${NC}"

# --- 1. OS & DEPENDENCY DETECTION ---
echo -e "${GREEN}[*] Checking System Dependencies...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}[!] Error: Homebrew is required for macOS.${NC}"
        exit 1
    fi
    brew install mpv python3
elif [ -f /etc/arch-release ]; then
    # Arch Linux
    sudo pacman -S --noconfirm mpv python git
elif [ -f /etc/debian_version ]; then
    # Ubuntu / Kali
    sudo apt update && sudo apt install -y mpv python3 python3-venv git
elif [ -f /etc/fedora-release ]; then
    # Fedora
    sudo dnf install -y mpv python3 git
fi

# --- 2. SETUP DIRECTORIES ---
echo -e "${GREEN}[*] Setting up install directory...${NC}"
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/src"  # Create src folder to match dev structure
mkdir -p "$BIN_DIR"

# Copy source code into the src subfolder
# This ensures the relative path "../pokemon-colorscripts" works correctly
cp src/pokefact.py "$INSTALL_DIR/src/"
cp requirements.txt "$INSTALL_DIR/"

# --- 3. DOWNLOAD ART ASSETS ---
echo -e "${GREEN}[*] Downloading Art Assets...${NC}"
# We clone into the root install dir, sitting next to the 'src' folder
git clone --depth 1 "$ART_REPO" "$INSTALL_DIR/pokemon-colorscripts" > /dev/null 2>&1

# Note: We do NOT need to chmod +x the shell script anymore 
# because Python reads the text files directly now.

# --- 4. PYTHON SETUP ---
echo -e "${GREEN}[*] Installing Python libraries...${NC}"
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"
pip install -q -r "$INSTALL_DIR/requirements.txt"

# --- 5. CREATE LAUNCHER ---
echo -e "${GREEN}[*] Creating executable...${NC}"
cat <<EOF > "$EXECUTABLE"
#!/bin/bash
# Execute the python script located in the src folder
"$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/src/pokefact.py" "\$@"
EOF
chmod +x "$EXECUTABLE"

# --- 6. PATH CHECK ---
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${RED}[!] Warning: $HOME/.local/bin is not in your PATH.${NC}"
    echo "    Add this to your .zshrc: export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo -e "${GREEN}[✔] Done! Type 'pokefact' to start.${NC}"

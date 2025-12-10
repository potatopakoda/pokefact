#!/bin/bash
INSTALL_DIR="$HOME/.local/share/pokefact"
EXECUTABLE="$HOME/.local/bin/pokefact"

echo "Uninstalling PokeFact..."
rm -rf "$INSTALL_DIR"
rm -f "$EXECUTABLE"
echo "Done."

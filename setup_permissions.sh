#!/bin/bash
# Make all scripts executable

echo "Setting executable permissions on all scripts..."

chmod +x start_ws_quick.sh
chmod +x restart-frontend.sh
chmod +x start-frontend.sh
chmod +x quick_reference.sh
chmod +x make_executable.sh

echo "✅ All scripts are now executable!"
echo ""
echo "You can now run:"
echo "  ./start_ws_quick.sh     - Start everything"
echo "  ./quick_reference.sh    - Show quick commands"
echo ""
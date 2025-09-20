#!/bin/bash
# Debug script to check for frontend compilation errors

echo "🔍 FRONTEND DEBUG CHECK"
echo "======================="
echo ""

# Check if the enhanced component exists
if [ -f "frontend/src/components/EnhancedUserCommandCenter.tsx" ]; then
    echo "✅ EnhancedUserCommandCenter.tsx exists"
else
    echo "❌ EnhancedUserCommandCenter.tsx NOT FOUND"
fi

# Check if control center page is using it
if grep -q "EnhancedUserCommandCenter" "frontend/src/pages/control-center/ControlCenterPage.tsx"; then
    echo "✅ ControlCenterPage imports EnhancedUserCommandCenter"
else
    echo "❌ ControlCenterPage NOT importing EnhancedUserCommandCenter"
fi

# Check for TypeScript/compilation errors
echo ""
echo "Checking for compilation errors..."
cd frontend

# Try to build to see errors
echo ""
echo "Running type check..."
npx tsc --noEmit 2>&1 | head -20

echo ""
echo "📋 Current frontend process:"
ps aux | grep -E "vite|npm" | grep -v grep

echo ""
echo "🔧 To see live compilation errors:"
echo "  1. cd frontend"
echo "  2. npm run dev"
echo "  3. Check the terminal for red error messages"
#!/bin/bash
# Batch move test files to organized directories

echo "🧹 Moving test files to organized directories..."

# Move WebSocket test files
mv test_*ws*.py tests/websocket/ 2>/dev/null
mv test_websocket*.py tests/websocket/ 2>/dev/null
mv test_*ws*.html tests/websocket/ 2>/dev/null

# Move API test files  
mv test_api*.py tests/api/ 2>/dev/null
mv test_*api*.py tests/api/ 2>/dev/null
mv test_api*.html tests/api/ 2>/dev/null
mv test_odds*.py tests/api/ 2>/dev/null
mv test_sports*.py tests/api/ 2>/dev/null

# Move frontend HTML test files
mv test_*.html tests/frontend/ 2>/dev/null
mv debug_*.html tests/frontend/ 2>/dev/null

# Move integration test files
mv test_integration*.py tests/integration/ 2>/dev/null
mv test_comprehensive*.py tests/integration/ 2>/dev/null
mv test_cross_system*.py tests/integration/ 2>/dev/null
mv test_workflow*.py tests/integration/ 2>/dev/null

# Move verification scripts
mv verify_*.py tests/verification/ 2>/dev/null
mv validate_*.py tests/verification/ 2>/dev/null
mv check_*.py tests/verification/ 2>/dev/null

# Move debug scripts
mv debug_*.py tests/debug/ 2>/dev/null

# Move remaining test files to unit tests
mv test_*.py tests/unit/ 2>/dev/null

# Count remaining test files in root
echo "📊 Checking for remaining test files in root..."
remaining=$(ls test_*.* verify_*.* check_*.* debug_*.* 2>/dev/null | wc -l)

if [ "$remaining" -eq 0 ]; then
    echo "✅ All test files organized successfully!"
else
    echo "⚠️  $remaining test files remaining in root directory"
    ls test_*.* verify_*.* check_*.* debug_*.* 2>/dev/null
fi

echo ""
echo "📁 Test directory structure:"
echo "tests/"
echo "├── api/         - API test files"
echo "├── debug/       - Debug scripts"
echo "├── frontend/    - Frontend/HTML tests"
echo "├── integration/ - Integration tests"
echo "├── unit/        - Unit tests"
echo "├── verification/ - Verification scripts"
echo "└── websocket/   - WebSocket tests"

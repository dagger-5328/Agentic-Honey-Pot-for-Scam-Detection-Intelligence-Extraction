#!/bin/bash
# Cleanup script to remove unnecessary files for a fresh project

echo "Cleaning up GUVI-related files..."

# Files to remove
files_to_remove=(
    "guvi_api_server.py"
    "test_guvi_api.py"
    "GUVI_QUICKSTART.md"
)

for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        echo "Removing $file"
        rm "$file"
        echo "✅ $file removed"
    else
        echo "ℹ️  $file not found (already removed)"
    fi
done

echo ""
echo "🎉 Cleanup complete!"
echo "The project is now fresh and ready for use."
echo ""
echo "Next steps:"
echo "  pip install -r requirements.txt"
echo "  python main.py --demo"
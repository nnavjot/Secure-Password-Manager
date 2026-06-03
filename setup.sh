

set -e

echo "=== SecureVault Setup ==="


python3 -m venv venv
source venv/bin/activate


pip install flask bcrypt cryptography


mkdir -p instance


python3 - <<'EOF'
from app import create_app
app = create_app()
print("Database initialised successfully.")
EOF

echo ""
echo "=== Setup complete ==="
echo "Run the app with:"
echo "  source venv/bin/activate && python app.py"

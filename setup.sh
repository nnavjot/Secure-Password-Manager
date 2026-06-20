
set -e
GREEN='\033[0;32m'; NC='\033[0m'
info() { echo -e "${GREEN}[+]${NC} $1"; }

cd "$(dirname "$0")"

PYTHON=$(command -v python3 || command -v python)
$PYTHON -c "import sys; assert sys.version_info>=(3,8)" 2>/dev/null \
  || { echo "Python 3.8+ is required."; exit 1; }
info "Python OK"

[ -d venv ] || $PYTHON -m venv venv
source venv/bin/activate
info "Virtual environment ready"


pip install --upgrade pip -q
pip install -r requirements.txt -q
info "Dependencies installed (Flask, bcrypt, cryptography)"


info "Starting application..."
echo ""
echo "  Open your browser at:  http://127.0.0.1:5000"
echo "  Press Ctrl+C to stop."
echo ""
python -c "from app import init_db; init_db()"
python app.py

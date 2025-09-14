#!/bin/bash

# ML Pipeline Setup Script for M3 MacBook Pro
# Sets up the complete ML stack for the Unified Intelligence System

set -e  # Exit on any error

echo "🧠 Setting up ML Pipeline for M3 MacBook Pro..."
echo "================================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is optimized for macOS (M3 MacBook Pro)"
    echo "   For other systems, manually install the requirements from ml/requirements.txt"
    exit 1
fi

# Check for Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "⚠️  Warning: This script is optimized for Apple Silicon (M3)"
    echo "   Continuing anyway, but performance may not be optimal"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo "🔍 Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    echo "   Found Python $PYTHON_VERSION"

    # Check if version is 3.9 or higher using comparison
    major=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    minor=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [[ $major -gt 3 ]] || [[ $major -eq 3 && $minor -ge 9 ]]; then
        echo "   ✅ Python version is compatible"
    else
        echo "   ❌ Python 3.9+ required, found $PYTHON_VERSION"
        echo "   Please install Python 3.9+ using Homebrew: brew install python@3.11"
        exit 1
    fi
else
    echo "❌ Python 3 not found. Install with: brew install python@3.11"
    exit 1
fi

# Check for Homebrew
echo "🔍 Checking for Homebrew..."
if ! command_exists brew; then
    echo "❌ Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "   ✅ Homebrew found"
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
brew update
brew install git curl wget cmake pkg-config

# Create and activate virtual environment
echo "🐍 Setting up Python virtual environment..."
cd "$(dirname "$0")"

if [ ! -d "venv_ml" ]; then
    python3 -m venv venv_ml
    echo "   Created virtual environment: venv_ml"
else
    echo "   Using existing virtual environment: venv_ml"
fi

source venv_ml/bin/activate
echo "   ✅ Virtual environment activated"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Apple ML Stack first (for M3 optimization)
echo "🍎 Installing Apple ML Stack for M3..."

# Install MLX (Apple's ML framework for M-series)
echo "   Installing MLX..."
pip install mlx

# Install PyTorch for Apple Silicon
echo "   Installing PyTorch with Metal support..."
pip install torch torchvision torchaudio

# Install TensorFlow for Apple Silicon
echo "   Installing TensorFlow with Metal support..."
pip install tensorflow-macos tensorflow-metal

# Install Core ML Tools
echo "   Installing Core ML Tools..."
pip install coremltools

# Install main ML requirements
echo "📚 Installing ML pipeline requirements..."
if [ -f "ml/requirements.txt" ]; then
    pip install -r ml/requirements.txt
else
    echo "❌ ml/requirements.txt not found"
    exit 1
fi

# Create necessary directories
echo "📁 Creating ML directories..."
mkdir -p ml/models/cache
mkdir -p ml/data/raw
mkdir -p ml/data/processed
mkdir -p ml/logs
mkdir -p ml/experiments

# Set up HuggingFace cache directory
export HF_HOME="$(pwd)/ml/models/cache/huggingface"
mkdir -p "$HF_HOME"

echo "   ✅ Created ML directory structure"

# Download and cache some essential models
echo "📥 Pre-downloading essential ML models..."
python3 -c "
import os
os.environ['HF_HOME'] = '$HF_HOME'

try:
    from transformers import pipeline

    print('   Downloading DistilBERT for sentiment analysis...')
    sentiment = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
    print('   ✅ DistilBERT cached')

    print('   Downloading FinBERT for financial analysis...')
    finbert = pipeline('sentiment-analysis', model='ProsusAI/finbert')
    print('   ✅ FinBERT cached')

    print('   Downloading Twitter RoBERTa for social sentiment...')
    twitter_sentiment = pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment-latest')
    print('   ✅ Twitter RoBERTa cached')

except Exception as e:
    print(f'   ⚠️  Warning: Could not pre-download models: {e}')
    print('   Models will be downloaded on first use')
"

# Test ML installation
echo "🧪 Testing ML installation..."
python3 -c "
import sys
print('   Testing core imports...')

try:
    import mlx.core as mx
    print('   ✅ MLX available')
except ImportError:
    print('   ⚠️  MLX not available')

try:
    import torch
    print(f'   ✅ PyTorch {torch.__version__} available')
    if torch.backends.mps.is_available():
        print('   ✅ Metal Performance Shaders (MPS) available')
    else:
        print('   ⚠️  MPS not available')
except ImportError:
    print('   ❌ PyTorch not available')

try:
    import tensorflow as tf
    print(f'   ✅ TensorFlow {tf.__version__} available')
    if len(tf.config.list_physical_devices('GPU')) > 0:
        print('   ✅ TensorFlow Metal support available')
    else:
        print('   ⚠️  TensorFlow Metal not detected')
except ImportError:
    print('   ❌ TensorFlow not available')

try:
    import sklearn
    print(f'   ✅ Scikit-learn {sklearn.__version__} available')
except ImportError:
    print('   ❌ Scikit-learn not available')

try:
    from transformers import pipeline
    print('   ✅ HuggingFace Transformers available')
except ImportError:
    print('   ❌ HuggingFace Transformers not available')

print('   ML installation test completed!')
"

# Set up environment variables
echo "🔧 Setting up environment..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    touch .env
fi

# Add ML-specific environment variables
if ! grep -q "ML_MODELS_PATH" .env; then
    echo "ML_MODELS_PATH=$(pwd)/ml/models/cache" >> .env
fi

if ! grep -q "HF_HOME" .env; then
    echo "HF_HOME=$(pwd)/ml/models/cache/huggingface" >> .env
fi

if ! grep -q "PYTORCH_ENABLE_MPS_FALLBACK" .env; then
    echo "PYTORCH_ENABLE_MPS_FALLBACK=1" >> .env
fi

# Add to Django settings if needed
echo "⚙️  Updating Django settings..."
if ! grep -q "ml_intelligence" backend/settings.py; then
    echo "
# Add ml_intelligence to INSTALLED_APPS
INSTALLED_APPS += ['ml_intelligence']

# ML Configuration
ML_MODELS_PATH = os.path.join(BASE_DIR, 'ml', 'models', 'cache')
HUGGINGFACE_CACHE_DIR = os.path.join(ML_MODELS_PATH, 'huggingface')

# Optional: Add HuggingFace API token (get from https://huggingface.co/settings/tokens)
# HUGGINGFACE_API_TOKEN = 'your_token_here'
" >> backend/settings.py
fi

# Create activation script
echo "📝 Creating activation script..."
cat > activate_ml.sh << 'EOF'
#!/bin/bash
# Activate ML environment

echo "🧠 Activating ML Pipeline Environment..."
source venv_ml/bin/activate

export ML_MODELS_PATH="$(pwd)/ml/models/cache"
export HF_HOME="$(pwd)/ml/models/cache/huggingface"
export PYTORCH_ENABLE_MPS_FALLBACK=1

echo "✅ ML Environment activated"
echo "   Python: $(which python)"
echo "   ML Models: $ML_MODELS_PATH"
echo "   HF Cache: $HF_HOME"

# Test ML service
python -c "
try:
    from ml_intelligence.ml_service import MLService
    service = MLService.get_instance()
    if service and service.is_available():
        print('✅ ML Service ready')
    else:
        print('⚠️  ML Service not ready - run: python manage.py migrate')
except Exception as e:
    print(f'⚠️  ML Service error: {e}')
"
EOF

chmod +x activate_ml.sh

echo ""
echo "🎉 ML Pipeline Setup Complete!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo "1. Activate the ML environment:"
echo "   source activate_ml.sh"
echo ""
echo "2. Run Django migrations:"
echo "   python manage.py migrate"
echo ""
echo "3. Optional - Add HuggingFace API token to .env:"
echo "   HUGGINGFACE_API_TOKEN=your_token_here"
echo "   Get token from: https://huggingface.co/settings/tokens"
echo ""
echo "4. Test the ML integration:"
echo "   python manage.py shell"
echo "   >>> from ml_intelligence.ml_service import MLService"
echo "   >>> service = MLService.get_instance()"
echo "   >>> print(service.is_available())"
echo ""
echo "🚀 Your M3 MacBook Pro is now ready for ML-powered intelligence!"
echo ""
echo "💡 Features available:"
echo "   • Local ML processing with Apple MLX optimization"
echo "   • HuggingFace integration for advanced models"
echo "   • Sports → Crypto pattern recognition"
echo "   • Personal decision tracking (Digital Twin)"
echo "   • Cross-domain transfer learning"
echo ""
echo "🔧 To start development:"
echo "   source activate_ml.sh"
echo "   python manage.py runserver"
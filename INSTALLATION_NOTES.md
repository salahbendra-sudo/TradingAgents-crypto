# DeepSeek Integration - Installation Notes

## Fixed Requirements Issue

The installation error you encountered has been fixed. The issue was with the specific torch version `torch==2.9.0+cpu` which is not available for all Python versions.

## Updated Requirements

The requirements.txt has been updated to use flexible version requirements:
- `torch>=2.9.0` (instead of `torch==2.9.0+cpu`)
- `transformers>=4.57.1` (instead of `transformers==4.57.1`)

## Installation Instructions

### Option 1: Install all requirements
```bash
pip install -r requirements.txt
```

### Option 2: Install DeepSeek dependencies only
```bash
pip install langchain-deepseek torch>=2.9.0 transformers>=4.57.1
```

### Option 3: If you still encounter torch installation issues
```bash
# Install CPU-only torch (recommended for most systems)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install the rest
pip install -r requirements.txt
```

## What's Included

- **DeepSeek LLM Provider**: Full integration with DeepSeek API
- **Local Embeddings**: Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings when DeepSeek is selected
- **Memory System**: Full memory functionality with real embeddings
- **Web Interface**: DeepSeek appears as an option in the provider dropdown

## Usage

1. Start the web application:
   ```bash
   python web_app.py
   ```

2. In the web interface:
   - Select "DeepSeek" as the LLM Provider
   - Enter your DeepSeek API key
   - Choose between `deepseek-chat` and `deepseek-reasoner` models
   - Run trading analysis as usual

## Troubleshooting

If you encounter any issues:
1. Make sure you have a valid DeepSeek API key
2. Check that torch and transformers installed correctly
3. The system will fall back to dummy embeddings if local model fails to load

## Features

✅ Full DeepSeek LLM integration  
✅ Local embedding generation  
✅ Memory operations with similarity matching  
✅ No API errors for embeddings  
✅ Compatible with existing trading analysis workflows
# DeepSeek LLM Integration

This document explains how to use DeepSeek LLM with the TradingAgents-crypto project.

## Overview

DeepSeek is now fully integrated as a supported LLM provider in the TradingAgents framework. You can use DeepSeek models for both quick-thinking (shallow) and deep-thinking tasks.

## Setup

### 1. Install Dependencies

The `langchain-deepseek` package has been added to the requirements files:
- `requirements.txt`
- `requirements_web.txt`

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Get DeepSeek API Key

1. Sign up for a DeepSeek account at [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. Generate an API key from your account dashboard
3. Set the API key as an environment variable:
   ```bash
   export DEEPSEEK_API_KEY="your-api-key-here"
   ```

## Usage

### Using the CLI

When running the CLI, you can now select DeepSeek as your LLM provider:

1. Run the CLI:
   ```bash
   python -m cli.main
   ```

2. Select "DeepSeek" as your LLM provider
3. Choose from available DeepSeek models:
   - **Quick-Thinking Models**:
     - `deepseek-chat` - Latest chat model
     - `deepseek-coder` - Code generation model
     - `deepseek-v2` - Latest version
   - **Deep-Thinking Models**:
     - `deepseek-chat` - Latest chat model
     - `deepseek-coder` - Code generation model
     - `deepseek-v2` - Latest version
     - `deepseek-v2-r1` - Reasoning model

### Programmatic Usage

You can also use DeepSeek programmatically by setting the configuration:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

config = {
    "llm_provider": "deepseek",
    "deep_think_llm": "deepseek-chat",
    "quick_think_llm": "deepseek-chat",
    "backend_url": "https://api.deepseek.com/v1",
    "api_key": "your-deepseek-api-key"
}

graph = TradingAgentsGraph(config=config)
```

## Available Models

### DeepSeek Models
- `deepseek-chat` - General purpose chat model
- `deepseek-coder` - Specialized for code generation
- `deepseek-v2` - Latest version with improved capabilities
- `deepseek-v2-r1` - Enhanced reasoning model

## Configuration

When using DeepSeek, the following configuration parameters are used:

- `llm_provider`: Set to `"deepseek"`
- `backend_url`: `"https://api.deepseek.com/v1"`
- `api_key`: Your DeepSeek API key
- `deep_think_llm`: Model for deep thinking tasks
- `quick_think_llm`: Model for quick thinking tasks

## Benefits of DeepSeek

- **Cost-effective**: Often more affordable than other commercial LLMs
- **High performance**: Competitive performance on reasoning tasks
- **Open weights**: More transparent than closed-source alternatives
- **Strong coding capabilities**: Excellent for financial analysis and data processing

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure your API key is valid and has sufficient credits
   - Check that the API key is properly set in environment variables

2. **Model Not Found**:
   - Verify the model name is correct
   - Check DeepSeek's documentation for current available models

3. **Rate Limiting**:
   - DeepSeek may have rate limits based on your account tier
   - Implement retry logic if needed

### Getting Help

- DeepSeek API Documentation: [https://platform.deepseek.com/api-docs/](https://platform.deepseek.com/api-docs/)
- Project Issues: [GitHub Issues](https://github.com/salahbendra-sudo/TradingAgents-crypto/issues)
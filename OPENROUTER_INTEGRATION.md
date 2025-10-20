# OpenRouter Integration Guide

This guide explains how to use OpenRouter models with TradingAgents-crypto.

## Overview

OpenRouter is a unified API that provides access to multiple AI models from different providers through a single interface. It supports models from OpenAI, Anthropic, Google, Meta, Mistral, DeepSeek, and many others.

## Setup

### 1. Get OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/) and create an account
2. Go to your [API Keys](https://openrouter.ai/keys) page
3. Create a new API key
4. Your OpenRouter API key will start with `sk-or-`

### 2. Configure TradingAgents

#### Web Interface
1. Select "OpenRouter" as the LLM Provider
2. The backend URL will automatically update to `https://openrouter.ai/api/v1`
3. Enter your OpenRouter API key
4. Select your preferred models for quick and deep thinking

#### CLI Interface
When running the CLI, select:
- Provider: "Openrouter"
- Backend URL: `https://openrouter.ai/api/v1`
- Enter your OpenRouter API key when prompted

#### Environment Variables (Optional)
You can also set environment variables:
```bash
export OPENROUTER_API_KEY=your_openrouter_api_key
export OPENAI_API_KEY=your_openrouter_api_key  # For compatibility
```

## Available Models

### Quick-Thinking Models (Fast, Cost-Effective)
- **Meta: Llama 4 Scout (Free)** - Free model for basic tasks
- **Meta: Llama 3.3 8B Instruct (Free)** - Lightweight and fast
- **Google: Gemini 2.0 Flash Exp (Free)** - Fast Gemini model
- **Meta: Llama 3.1 8B Instruct** - Reliable 8B parameter model
- **Google: Gemini 2.0 Flash** - Fast and capable
- **OpenAI: GPT-4o Mini** - OpenAI's fastest model

### Deep-Thinking Models (Advanced Reasoning)
- **DeepSeek V3 (Free)** - 685B parameter mixture-of-experts
- **Meta: Llama 3.1 70B Instruct** - High-quality reasoning
- **Meta: Llama 3.3 70B Instruct** - Latest Meta model
- **Google: Gemini 2.0 Flash Thinking** - Advanced reasoning capabilities
- **Google: Gemini 2.5 Pro** - Google's most advanced model
- **Anthropic: Claude 3.5 Sonnet** - Excellent reasoning and analysis
- **OpenAI: GPT-4o** - OpenAI's flagship model
- **OpenAI: o3-mini** - Advanced reasoning model

## Model Selection Tips

### For Quick Analysis
- Use **Meta: Llama 3.3 8B Instruct (Free)** for cost-effective analysis
- Use **Google: Gemini 2.0 Flash** for balanced speed and quality
- Use **OpenAI: GPT-4o Mini** for the fastest responses

### For Deep Analysis
- Use **DeepSeek V3 (Free)** for free advanced analysis
- Use **Anthropic: Claude 3.5 Sonnet** for complex reasoning tasks
- Use **Google: Gemini 2.5 Pro** for comprehensive analysis
- Use **OpenAI: o3-mini** for advanced reasoning

## Cost Considerations

- **Free Models**: Llama 4 Scout, Llama 3.3 8B, Gemini 2.0 Flash Exp, DeepSeek V3
- **Cost-Effective**: Llama 3.1 8B, Gemini 2.0 Flash
- **Premium**: Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro

Check [OpenRouter Pricing](https://openrouter.ai/models) for current rates.

## Features

### Supported Capabilities
- ✅ Text generation and analysis
- ✅ Tool calling (function calling)
- ✅ Streaming responses
- ✅ Multiple model providers
- ✅ Cost tracking

### Limitations
- Some models may have different context windows
- Response formats may vary between providers
- Rate limits may apply based on the model

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify your API key starts with `sk-or-`
   - Check that the API key is correctly entered

2. **Model Not Found**
   - Ensure the model name is correctly formatted
   - Check if the model is available on OpenRouter

3. **Rate Limiting**
   - Some free models have usage limits
   - Consider upgrading to paid models for higher limits

4. **Context Window Issues**
   - Different models have different context limits
   - Reduce the amount of data being processed if needed

### Getting Help

- OpenRouter Documentation: https://openrouter.ai/docs
- Model Information: https://openrouter.ai/models
- Support: https://openrouter.ai/support

## Example Configuration

```python
# Example config for OpenRouter
config = {
    "llm_provider": "openrouter",
    "backend_url": "https://openrouter.ai/api/v1",
    "api_key": "sk-or-...",
    "quick_think_llm": "meta-llama/llama-3.3-8b-instruct:free",
    "deep_think_llm": "deepseek/deepseek-chat-v3-0324:free"
}
```

## Benefits of Using OpenRouter

1. **Single API**: Access multiple providers through one interface
2. **Cost Comparison**: Easily compare costs between different models
3. **Model Diversity**: Choose from a wide range of models
4. **Free Options**: Several high-quality free models available
5. **Unified Format**: Consistent API format across all models
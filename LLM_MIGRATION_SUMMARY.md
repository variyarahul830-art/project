# LLM Service Migration to Hugging Face Inference API

## Migration Completed ✅

The LLM service has been successfully migrated from local Ollama to Hugging Face Inference API.

### Files Modified

#### 1. `backend/services/llm_service.py` (COMPLETELY REFACTORED)
**Changes:**
- ✅ Replaced `__init__` parameters:
  - OLD: `use_api`, `api_provider`, `api_url`, `model_name`, `huggingface_token`
  - NEW: `huggingface_token` (required), `model_name` (optional, defaults to Llama-2-7b-chat-hf)
  
- ✅ Added HuggingFace API URL generation:
  ```python
  self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
  ```

- ✅ Replaced `_generate_with_ollama()` with `_generate_with_huggingface()`:
  - Bearer token authentication: `Authorization: Bearer {token}`
  - Proper JSON payload with HF API format
  - Response parsing for HF API format
  - Error handling for connection issues
  - Fallback to `_create_simple_answer()` on failure

- ✅ Added `_create_prompt()` method:
  - Creates well-formatted prompts with context
  - Format: "Based on context... QUESTION: ... ANSWER:"

- ✅ Updated `generate_answer_with_context()`:
  - Now only calls `_generate_with_huggingface()`
  - Simplified error handling

- ✅ Kept `_build_context()` and `_create_simple_answer()` methods
  - These work with both Ollama and HF APIs

#### 2. `backend/routes/chat.py` (LLM INITIALIZATION UPDATED)
**Changes:**
- ✅ Updated LLMService initialization call (lines ~152-160):
  - OLD: Multiple parameters including `use_api`, `api_provider`, `api_url`
  - NEW: Only `huggingface_token` and `model_name` parameters
  - Added validation to ensure HUGGINGFACE_TOKEN is configured
  - Graceful fallback if token is not set

#### 3. `backend/config.py` (ALREADY HAD NECESSARY CONFIG)
**Status:** ✅ No changes needed
- Already defines: `HUGGINGFACE_TOKEN` (from env var)
- Already defines: `LLM_MODEL` (defaults to "openai/gpt-oss-20b")
- Already uses `.env` for loading environment variables

---

## Configuration Required

### Environment Variables (add to `.env` file in backend directory)

```bash
# Hugging Face API Token (required)
HUGGINGFACE_TOKEN=hf_your_token_here

# LLM Model (optional - defaults shown)
LLM_MODEL=meta-llama/Llama-2-7b-chat-hf
# Or use other options:
# LLM_MODEL=openai/gpt-oss-20b
# LLM_MODEL=NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
```

### How to Get a Hugging Face Token

1. Go to: https://huggingface.co/settings/tokens
2. Create a new token with "read" access
3. Copy the token and add to your `.env` file

---

## API Endpoints Used

### Hugging Face Inference API
- **Endpoint:** `https://api-inference.huggingface.co/models/{model_name}`
- **Authentication:** Bearer token in Authorization header
- **Method:** POST
- **Headers:**
  ```json
  {
    "Authorization": "Bearer {token}",
    "Content-Type": "application/json"
  }
  ```
- **Payload:**
  ```json
  {
    "inputs": "prompt text here",
    "parameters": {
      "max_new_tokens": 512,
      "temperature": 0.7,
      "top_p": 0.95,
      "do_sample": true
    }
  }
  ```

---

## Supported Models

### Recommended Models
- **`meta-llama/Llama-2-7b-chat-hf`** (DEFAULT) - Good balance of speed and quality
- **`openai/gpt-oss-20b`** - Better quality, slower
- **`NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO`** - Excellent quality, larger model

### Model Parameters in Code
Edit `backend/config.py` or `.env` file:
```python
LLM_MODEL=meta-llama/Llama-2-7b-chat-hf  # Change this to use different models
```

---

## What Was Removed

✅ **Completely Removed:**
- Ollama API dependency
- `_generate_with_ollama()` method
- Local model serving requirement
- All Ollama-specific configuration

---

## Testing the Migration

### 1. Test Configuration
```bash
cd backend
cat .env  # Verify HUGGINGFACE_TOKEN is set
```

### 2. Test Backend Startup
```bash
python main.py
# Should start without Ollama errors
```

### 3. Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "hello"}'
```

### 4. Expected Behavior
- **If node found:** Returns from knowledge graph
- **If not found:** Falls back to RAG:
  1. Generates embedding for question
  2. Searches Milvus for similar PDF chunks
  3. Calls Hugging Face API with context
  4. Returns LLM-generated answer

---

## Error Handling

The system now handles:
- ✅ Missing HuggingFace token → Returns error message
- ✅ Invalid token → HF API returns 401/403
- ✅ Model not found → HF API returns error
- ✅ Connection timeout → Falls back to simple answer
- ✅ API rate limit → Falls back to simple answer

---

## Benefits of Migration

| Aspect | Ollama | Hugging Face |
|--------|--------|-------------|
| Setup | Requires local service | Cloud-based, no setup |
| Models | Limited, local only | 100k+ models available |
| Quality | Mistral model | Llama-2, GPT-OSS, etc |
| Scaling | Limited by hardware | Unlimited (cloud) |
| Cost | Free (hardware) | Varies by usage |
| Latency | Fast (local) | ~1-5s (network) |

---

## Rollback Instructions (if needed)

If you need to revert to Ollama:
1. Restore `backend/services/llm_service.py` from git
2. Restore `backend/routes/chat.py` from git
3. Update `.env` to add Ollama settings
4. Restart backend

---

## Next Steps

1. ✅ Set HUGGINGFACE_TOKEN in `.env`
2. ✅ Test backend startup
3. ✅ Test chat endpoint with your knowledge graph
4. ✅ Verify RAG answers are generated correctly
5. ✅ (Optional) Switch to different HF model if desired

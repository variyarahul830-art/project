# Quick Start: LLM Service with Hugging Face

## 1. Get Your Token

```
1. Visit: https://huggingface.co/settings/tokens
2. Click "New token"
3. Set name: "Chatbot"
4. Select access: "Read"
5. Copy the token
```

## 2. Add to Environment

Create or edit `backend/.env`:
```bash
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
LLM_MODEL=meta-llama/Llama-2-7b-chat-hf
```

## 3. Start Backend

```bash
cd backend
python main.py
```

## 4. Test Chat

```bash
# Test with a query in your knowledge graph
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "hello"}'

# If "hello" is a node in your graph, it should return connected nodes
# If not found in graph, it will use RAG to search PDFs and generate an answer
```

## Model Options

### Fast & Good (Default)
- `meta-llama/Llama-2-7b-chat-hf` - Balances speed and quality

### Better Quality (Slower)
- `openai/gpt-oss-20b` - Better answers, slower responses
- `NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO` - Excellent quality

### Switch Models
Edit `backend/config.py` line 46:
```python
LLM_MODEL: str = os.getenv("LLM_MODEL", "YOUR_MODEL_HERE")
```

Or override in `.env`:
```bash
LLM_MODEL=openai/gpt-oss-20b
```

## Troubleshooting

### Error: "Cannot connect to Hugging Face API"
- Check internet connection
- Verify token is valid (try in HF web interface)
- Check if model exists and is public

### Error: "HUGGINGFACE_TOKEN not configured"
- Add `HUGGINGFACE_TOKEN=hf_...` to `.env` in backend directory
- Restart backend: `python main.py`

### Error: "Model not found"
- Check model name is correct (case-sensitive)
- Visit https://huggingface.co/models to find available models
- Model must support text generation and be public or accessible with your token

### Slow Responses
- This is normal for first query (model loading)
- Subsequent queries are faster
- Consider switching to faster model (Llama-2-7b)

## API Response Examples

### Success (from knowledge graph)
```json
{
  "success": true,
  "question": "hello",
  "answers": ["hi", "hello there"],
  "source": "knowledge_graph",
  "count": 2
}
```

### Success (from RAG)
```json
{
  "success": true,
  "question": "what is machine learning?",
  "answer": "Machine learning is a subset of AI that...",
  "source": "rag",
  "chunks_used": 3
}
```

### Error
```json
{
  "success": false,
  "message": "LLM service not properly configured. Please set HUGGINGFACE_TOKEN."
}
```

## Rate Limits

Hugging Face free tier allows:
- Reasonable usage for development
- If hitting rate limits, consider:
  1. Upgrading HF account
  2. Using smaller models
  3. Caching responses

## Next Steps

1. Verify backend starts without errors
2. Test with "hi" query (should find graph nodes)
3. Test with unrelated query (should use RAG)
4. Try different models if needed

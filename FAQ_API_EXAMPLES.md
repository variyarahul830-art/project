# FAQ API Documentation & Examples

## Complete API Reference with Examples

### Base URL
```
http://localhost:8000/api/faq
```

---

## 1. Create FAQ
**Create a new FAQ entry**

```http
POST /api/faq/
Content-Type: application/json

{
  "question": "How do I reset my password?",
  "answer": "To reset your password, click the 'Forgot Password' link on the login page and follow the email instructions.",
  "category": "Account"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "question": "How do I reset my password?",
  "answer": "To reset your password, click the 'Forgot Password' link on the login page and follow the email instructions.",
  "category": "Account",
  "created_at": "2024-01-23T10:30:00",
  "updated_at": "2024-01-23T10:30:00"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/faq/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I reset my password?",
    "answer": "Click the Forgot Password link on login page.",
    "category": "Account"
  }'
```

---

## 2. Get All FAQs
**Retrieve all FAQs (optionally filtered by category)**

```http
GET /api/faq/
```

**With Category Filter:**
```http
GET /api/faq/?category=Account
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "question": "How do I reset my password?",
    "answer": "Click the Forgot Password link on login page.",
    "category": "Account",
    "created_at": "2024-01-23T10:30:00",
    "updated_at": "2024-01-23T10:30:00"
  },
  {
    "id": 2,
    "question": "How do I change my email?",
    "answer": "Go to Account Settings and click 'Change Email'.",
    "category": "Account",
    "created_at": "2024-01-23T11:00:00",
    "updated_at": "2024-01-23T11:00:00"
  }
]
```

**cURL Examples:**
```bash
# Get all FAQs
curl "http://localhost:8000/api/faq/"

# Get FAQs in specific category
curl "http://localhost:8000/api/faq/?category=Account"
```

---

## 3. Get FAQ by ID
**Retrieve a specific FAQ by its ID**

```http
GET /api/faq/{id}
```

**Example:**
```http
GET /api/faq/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "question": "How do I reset my password?",
  "answer": "Click the Forgot Password link on login page.",
  "category": "Account",
  "created_at": "2024-01-23T10:30:00",
  "updated_at": "2024-01-23T10:30:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "FAQ with ID 999 not found"
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/faq/1"
```

---

## 4. Get All Categories
**Get list of all unique FAQ categories**

```http
GET /api/faq/categories
```

**Response (200 OK):**
```json
[
  "Account",
  "Technical",
  "Billing",
  "General",
  "Pricing"
]
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/faq/categories"
```

---

## 5. Search FAQ - Exact Match
**Find an FAQ by exact question match (case-insensitive)**

```http
GET /api/faq/search/exact?question={question}
```

**Example:**
```http
GET /api/faq/search/exact?question=How%20do%20I%20reset%20my%20password?
```

**Response (200 OK) - Found:**
```json
{
  "id": 1,
  "question": "How do I reset my password?",
  "answer": "Click the Forgot Password link on login page.",
  "category": "Account",
  "created_at": "2024-01-23T10:30:00",
  "updated_at": "2024-01-23T10:30:00"
}
```

**Response (404 Not Found) - No Match:**
```json
{
  "detail": "No matching FAQ found"
}
```

**cURL Examples:**
```bash
# Simple example
curl "http://localhost:8000/api/faq/search/exact?question=How%20do%20I%20login?"

# With special characters (URL encoded)
curl "http://localhost:8000/api/faq/search/exact?question=What%27s%20your%20refund%20policy%3F"
```

---

## 6. Search FAQ - Partial Match
**Find FAQs containing keywords (partial matching)**

```http
GET /api/faq/search/partial?question={search_term}
```

**Example:**
```http
GET /api/faq/search/partial?question=password
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "question": "How do I reset my password?",
    "answer": "Click the Forgot Password link on login page.",
    "category": "Account",
    "created_at": "2024-01-23T10:30:00",
    "updated_at": "2024-01-23T10:30:00"
  },
  {
    "id": 3,
    "question": "How do I change my password?",
    "answer": "Go to Account Settings and select Change Password.",
    "category": "Account",
    "created_at": "2024-01-23T11:30:00",
    "updated_at": "2024-01-23T11:30:00"
  }
]
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/faq/search/partial?question=password"
```

---

## 7. Update FAQ
**Update an existing FAQ**

```http
PUT /api/faq/{id}
Content-Type: application/json

{
  "question": "Updated question?",
  "answer": "Updated answer...",
  "category": "Updated Category"
}
```

**Example (Update only answer):**
```http
PUT /api/faq/1
Content-Type: application/json

{
  "answer": "New answer text with more details..."
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "question": "How do I reset my password?",
  "answer": "New answer text with more details...",
  "category": "Account",
  "created_at": "2024-01-23T10:30:00",
  "updated_at": "2024-01-23T12:00:00"
}
```

**cURL Example:**
```bash
curl -X PUT "http://localhost:8000/api/faq/1" \
  -H "Content-Type: application/json" \
  -d '{
    "answer": "Updated answer with new information..."
  }'
```

---

## 8. Delete FAQ
**Delete an FAQ**

```http
DELETE /api/faq/{id}
```

**Response (204 No Content):**
```
(empty body)
```

**Response (404 Not Found):**
```json
{
  "detail": "FAQ with ID 999 not found"
}
```

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/api/faq/1"
```

---

## Integration with Chat API

When a user asks a question in the chat, the FAQ system is checked before the LLM:

### Chat Request:
```http
POST /api/chat/
Content-Type: application/json

{
  "question": "How do I reset my password?"
}
```

### Response if FAQ Match Found:
```json
{
  "success": true,
  "question": "How do I reset my password?",
  "answer": "Click the Forgot Password link on login page.",
  "source": "faq",
  "faq_id": 1,
  "category": "Account"
}
```

### Response if Partial FAQ Match:
```json
{
  "success": true,
  "question": "reset password",
  "answer": "Click the Forgot Password link on login page.",
  "source": "faq",
  "faq_id": 1,
  "category": "Account",
  "match_type": "partial"
}
```

### Response if No FAQ Match (Falls Back to RAG/LLM):
```json
{
  "success": true,
  "question": "What advanced features does your product have?",
  "answer": "Based on our documentation... [LLM generated response]",
  "source": "rag",
  "chunks_used": 3,
  "source_documents": [...]
}
```

---

## Sample Test Data

### FAQ 1: Account
```json
{
  "question": "How do I reset my password?",
  "answer": "Click the 'Forgot Password' button on the login page, enter your email, and follow the instructions sent to your inbox.",
  "category": "Account"
}
```

### FAQ 2: Account
```json
{
  "question": "How do I change my email?",
  "answer": "Go to Account Settings, click 'Edit Profile', and update your email address. You'll receive a confirmation email.",
  "category": "Account"
}
```

### FAQ 3: Technical
```json
{
  "question": "What browsers are supported?",
  "answer": "We support Chrome, Firefox, Safari, and Edge. For best experience, use the latest version of your browser.",
  "category": "Technical"
}
```

### FAQ 4: General
```json
{
  "question": "How does your system work?",
  "answer": "Our system uses AI-powered chat with three tiers: knowledge graphs for structured data, FAQs for common questions, and AI models for complex queries.",
  "category": "General"
}
```

### FAQ 5: Billing
```json
{
  "question": "What is your pricing?",
  "answer": "We offer flexible plans starting from free tier. Check our pricing page for detailed information and to find the plan that works for you.",
  "category": "Billing"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Description of what went wrong"
}
```

### Common Status Codes:
- `200` - Success (GET, PUT)
- `201` - Created (POST)
- `204` - No Content (DELETE success)
- `400` - Bad Request (validation error)
- `404` - Not Found (FAQ doesn't exist)
- `500` - Server Error (database issue)

---

## Testing with Postman

1. **Create collection**: "FAQ API"
2. **Set base URL**: `http://localhost:8000`
3. **Create requests**:
   - POST `/api/faq/`
   - GET `/api/faq/`
   - GET `/api/faq/{id}`
   - PUT `/api/faq/{id}`
   - DELETE `/api/faq/{id}`
   - GET `/api/faq/search/exact?question=...`
   - GET `/api/faq/search/partial?question=...`

---

## Rate Limiting & Performance

- **FAQ lookups**: ~10-50ms per request
- **No external API calls**: Instant responses
- **Database indexes**: Optimized for question searching
- **Case-insensitive**: Flexible matching

---

## Best Practices

1. **Use categories** to organize FAQs by topic
2. **Keep answers concise** but informative
3. **Use clear question phrasing** that matches user queries
4. **Update regularly** as product changes
5. **Monitor chat logs** for common questions to add as FAQs
6. **Test search** to ensure good matching
7. **Use partial matching** for phrases, not full questions

---

**FAQ API is ready to use! 🎉**

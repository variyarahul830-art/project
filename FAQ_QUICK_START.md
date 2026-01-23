# FAQ System - Quick Start Guide

## 🚀 Setup Instructions

### 1. Database Setup
The FAQ table will be created automatically when you start the backend (SQLAlchemy handles it).

### 2. Start Backend
```bash
cd backend
python -m uvicorn main:app --reload
```

The FAQ routes will be available at:
- API Docs: `http://localhost:8000/docs`
- FAQ endpoints: `http://localhost:8000/api/faq/`

### 3. Start Frontend  
```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` and you'll see the new **📚 FAQs** button in the sidebar.

## 📝 Adding Your First FAQ

### Option 1: Using Frontend UI
1. Click the **📚 FAQs** button in sidebar
2. Click **➕ Add FAQ**
3. Fill in:
   - **Question**: "What is your service?"
   - **Answer**: "We provide AI-powered chatbot services..."
   - **Category**: "General"
4. Click **Save FAQ**

### Option 2: Using API (curl)
```bash
curl -X POST "http://localhost:8000/api/faq/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I get started?",
    "answer": "Visit our website and sign up for a free account.",
    "category": "Getting Started"
  }'
```

## 🧪 Testing the System

### Test Chat with FAQ
1. Go to **💬 Chat** tab
2. Ask a question that matches an FAQ, e.g., "What is your service?"
3. You should get the FAQ answer immediately

### Response will look like:
```json
{
  "success": true,
  "question": "What is your service?",
  "answer": "We provide AI-powered chatbot services...",
  "source": "faq",
  "faq_id": 1,
  "category": "General"
}
```

## 🔍 FAQ Search Priority

When you ask a question, the system checks in this order:

1. **Knowledge Graph** → Exact/partial node match
2. **FAQs** → Exact/partial question match  ← NEW!
3. **Documents** → RAG search + LLM generation

This means FAQs are checked **before** using the expensive LLM!

## 📊 FAQ Management Features

### View FAQs
- Click **📚 FAQs** in sidebar
- See all FAQs in a beautiful card layout
- Each card shows question, answer, category, and update date

### Filter by Category
- Use the dropdown to filter FAQs by category
- Great for organizing different types of questions

### Edit FAQ
- Click the **✏️** button on any FAQ card
- Form pre-fills with current data
- Make changes and save

### Delete FAQ
- Click the **🗑️** button on any FAQ card
- Confirm deletion
- FAQ is removed from system

## 💡 Pro Tips

1. **Categories**: Use categories to organize FAQs (e.g., "Billing", "Technical", "General")

2. **Exact vs Partial Matching**:
   - Exact: User question must match exactly (case-insensitive)
   - Partial: FAQ matches if it contains key words from user question

3. **Performance**:
   - FAQs are instant (database lookup only)
   - No LLM calls needed = faster + cheaper
   - Perfect for repetitive questions

4. **Best Practices**:
   - Keep answers concise and clear
   - Use consistent categories
   - Review and update FAQs regularly
   - Common questions should go in FAQs

## 🐛 Troubleshooting

### FAQs not showing in chat?
- Check if FAQ was saved (refresh page)
- Make sure question/answer are not empty
- Verify database table was created

### API returns 404?
- Ensure backend is running on port 8000
- Check that FAQ ID exists
- Use `/api/faq/` to list all FAQs

### Frontend won't display FAQs button?
- Refresh the page (Ctrl+Shift+R for hard refresh)
- Check browser console for errors
- Ensure Sidebar component loaded correctly

## 📚 API Reference

### Create FAQ
```
POST /api/faq/
Body: {
  "question": "string (required)",
  "answer": "string (required)", 
  "category": "string (optional)"
}
```

### Get All FAQs
```
GET /api/faq/?category=General
```

### Search FAQ (Exact)
```
GET /api/faq/search/exact?question=How%20do%20I%20login?
```

### Search FAQ (Partial)
```
GET /api/faq/search/partial?question=password
```

### Update FAQ
```
PUT /api/faq/{faq_id}
Body: {
  "question": "string (optional)",
  "answer": "string (optional)",
  "category": "string (optional)"
}
```

### Delete FAQ
```
DELETE /api/faq/{faq_id}
```

### Get Categories
```
GET /api/faq/categories
Returns: ["General", "Technical", ...]
```

## 🎯 Example FAQs to Add

```
1. Question: "Hello"
   Answer: "Hi! How can I help you today?"
   Category: "Greeting"

2. Question: "What is your service?"
   Answer: "We provide AI-powered chatbot services with knowledge graph integration."
   Category: "General"

3. Question: "How do I upload documents?"
   Answer: "Go to the Documents tab and drag-and-drop your PDF files."
   Category: "Technical"

4. Question: "How does it work?"
   Answer: "Our system uses a knowledge graph, FAQs, and AI-powered document search."
   Category: "General"

5. Question: "Is it free?"
   Answer: "We offer a free tier with limited features."
   Category: "Pricing"
```

## ✨ What's New

- **3-tier response system**: Knowledge Graph → FAQs → RAG/LLM
- **Instant FAQ responses**: No AI generation needed
- **Cost savings**: Fewer LLM API calls
- **Easy management**: Beautiful UI for managing FAQs
- **Smart search**: Both exact and partial matching
- **Category organization**: Organize FAQs by topic
- **Consistent answers**: Pre-approved FAQ responses

---

**Happy FAQ managing! 🎉**

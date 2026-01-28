/**
 * API Service Layer - Chatbot
 * Reusable fetch helpers for chatbot API endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============== Chat Operations ==============

/**
 * Send a question and get response from the chatbot
 * @param {string} question - The user's question/source node text
 * @param {number} workflowId - The workflow ID
 * @param {string} sessionId - Optional session ID for chat history
 * @param {string} userId - Optional user ID for chat history
 * @returns {Promise} Promise with the response
 */
export async function chat(question, workflowId, sessionId = null, userId = null) {
  try {
    const body = { question, workflow_id: workflowId };
    if (sessionId) body.session_id = sessionId;
    if (userId) body.user_id = userId;
    
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Failed to send question: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to send question');
  }
}

/**
 * Send a direct chat message with session management
 * @param {string} question - The user's question
 * @param {string} sessionId - Optional session ID for chat history
 * @param {string} userId - Optional user ID for chat history
 * @returns {Promise} Promise with the response
 */
export async function sendDirectChatMessage(question, sessionId = null, userId = null) {
  try {
    const body = { question };
    if (sessionId) body.session_id = sessionId;
    if (userId) body.user_id = userId;
    
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to send message');
  }
}

// ============== PDF Operations ==============

/**
 * Upload a PDF file to MinIO and store metadata in PostgreSQL
 * @param {File} file - The PDF file to upload
 * @param {string} description - Optional description of the PDF
 */
export async function uploadPDF(file, description = '') {
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    const response = await fetch(`${API_BASE_URL}/api/pdf/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to upload PDF: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to upload PDF');
  }
}

/**
 * Get all uploaded PDF documents
 */
export async function getPDFDocuments() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/pdf/documents`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to get PDF documents: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to get PDF documents');
  }
}

/**
 * Delete a PDF document
 * @param {number} pdfId - The PDF document ID
 */
export async function deletePDF(pdfId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/pdf/documents/${pdfId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to delete PDF: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to delete PDF');
  }
}

/**
 * Get a download link for a PDF document
 * @param {number} pdfId - The PDF document ID
 */
export async function getPDFDownloadLink(pdfId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/pdf/documents/${pdfId}/download`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to get download link: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to get download link');
  }
}

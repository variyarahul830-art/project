/**
 * API Service - Uses Backend Endpoints
 * All requests go through: Frontend → Backend → Hasura
 * Backend handles JWT verification and data isolation
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get authorization header with JWT token
 */
function getAuthHeader() {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

/**
 * Handle API errors
 */
function handleError(response) {
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

// ============== SESSIONS ==============

export async function getSessions() {
  const response = await fetch(`${API_BASE_URL}/api/sessions/`, {
    method: 'GET',
    headers: getAuthHeader(),
  });
  return handleError(response);
}

export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
    method: 'GET',
    headers: getAuthHeader(),
  });
  return handleError(response);
}

export async function createSession(title = 'New Chat', category = 'General') {
  const response = await fetch(`${API_BASE_URL}/api/sessions/`, {
    method: 'POST',
    headers: getAuthHeader(),
    body: JSON.stringify({ title, category }),
  });
  return handleError(response);
}

export async function updateSession(sessionId, title, category = 'General') {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
    method: 'PUT',
    headers: getAuthHeader(),
    body: JSON.stringify({ title, category }),
  });
  return handleError(response);
}

export async function deleteSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
    method: 'DELETE',
    headers: getAuthHeader(),
  });
  return handleError(response);
}

// ============== MESSAGES ==============

export async function getMessages(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/messages`, {
    method: 'GET',
    headers: getAuthHeader(),
  });
  return handleError(response);
}

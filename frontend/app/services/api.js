/**
 * API Service Layer - Knowledge Graph Chatbot
 * Reusable fetch helpers for graph-based chatbot API endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============== Node Operations ==============

/**
 * Create a new node
 * @param {string} text - The node text/concept
 * @param {number} workflowId - The workflow ID
 */
export async function createNode(text, workflowId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph/nodes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, workflow_id: workflowId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to create node: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to create node');
  }
}

/**
 * Get all nodes
 */
export async function getAllNodes() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph/nodes`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to get nodes: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to get nodes');
  }
}

/**
 * Delete a node
 */
export async function deleteNode(nodeId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph/nodes/${nodeId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete node: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to delete node');
  }
}

// ============== Edge Operations ==============

/**
 * Create a new edge between nodes
 * @param {number} sourceNodeId - Source node ID
 * @param {number} targetNodeId - Target node ID
 * @param {number} workflowId - The workflow ID
 */
export async function createEdge(sourceNodeId, targetNodeId, workflowId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph/edges`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        source_node_id: sourceNodeId, 
        target_node_id: targetNodeId,
        workflow_id: workflowId 
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to create edge: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to create edge');
  }
}

/**
 * Get all edges
 */
export async function getAllEdges() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph/edges`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to get edges: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to get edges');
  }
}

/**
 * Delete an edge
 */
export async function deleteEdge(edgeId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph/edges/${edgeId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete edge: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to delete edge');
  }
}

// ============== Graph Operations ==============

/**
 * Get all nodes and edges (complete graph)
 */
export async function getGraph() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/graph/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to get graph: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to get graph');
  }
}

// ============== Chat Operations ==============

/**
 * Send a question and get target nodes from the knowledge graph
 * @param {string} question - The user's question/source node text
 * @param {number} workflowId - The workflow ID
 * @returns {Promise} Promise with the target nodes
 */
export async function chat(question, workflowId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, workflow_id: workflowId }),
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
 * Send a direct chat message without session management
 * @param {string} question - The user's question
 * @returns {Promise} Promise with the response
 */
export async function sendDirectChatMessage(question) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
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
 * Get a specific PDF document by ID
 * @param {number} pdfId - The PDF document ID
 */
export async function getPDFById(pdfId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/pdf/documents/${pdfId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to get PDF: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to get PDF');
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
 * Get download link for a PDF document
 * @param {number} pdfId - The PDF document ID
 */
export async function getPDFDownloadLink(pdfId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/pdf/documents/${pdfId}/download`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to get download link: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to get download link');
  }
}

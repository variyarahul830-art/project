/**
 * Hasura GraphQL Client
 * Provides utility functions to query Hasura GraphQL API from frontend
 */

const HASURA_URL = process.env.NEXT_PUBLIC_HASURA_URL || "http://localhost:8081/v1/graphql";
const HASURA_ADMIN_SECRET = process.env.NEXT_PUBLIC_HASURA_ADMIN_SECRET || "myadminsecret";

/**
 * Execute GraphQL query/mutation against Hasura
 */
export async function executeGraphQL(query, variables = {}) {
  try {
    const response = await fetch(HASURA_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-hasura-admin-secret": HASURA_ADMIN_SECRET,
      },
      body: JSON.stringify({
        query,
        variables,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (result.errors) {
      console.error("GraphQL Error:", result.errors);
      throw new Error(`GraphQL Error: ${result.errors[0]?.message || "Unknown error"}`);
    }

    return result.data;
  } catch (error) {
    console.error("Hasura Client Error:", error);
    throw error;
  }
}

// ==================== WORKFLOWS ====================

export async function getWorkflows() {
  const query = `
    query GetWorkflows {
      workflows(order_by: {created_at: desc}) {
        id
        name
        description
        created_at
        updated_at
        nodes {
          id
          text
        }
        edges {
          id
          source_node_id
          target_node_id
        }
      }
    }
  `;
  return executeGraphQL(query);
}

export async function getWorkflow(id) {
  const query = `
    query GetWorkflow($id: Int!) {
      workflows_by_pk(id: $id) {
        id
        name
        description
        created_at
        updated_at
        nodes {
          id
          text
        }
        edges {
          id
          source_node_id
          target_node_id
        }
      }
    }
  `;
  return executeGraphQL(query, { id });
}

export async function createWorkflow(name, description = "") {
  const query = `
    mutation CreateWorkflow($name: String!, $description: String) {
      insert_workflows_one(object: {name: $name, description: $description}) {
        id
        name
        description
        created_at
      }
    }
  `;
  return executeGraphQL(query, { name, description });
}

export async function updateWorkflow(id, name, description) {
  const query = `
    mutation UpdateWorkflow($id: Int!, $name: String!, $description: String) {
      update_workflows_by_pk(pk_columns: {id: $id}, _set: {name: $name, description: $description}) {
        id
        name
        description
        updated_at
      }
    }
  `;
  return executeGraphQL(query, { id, name, description });
}

export async function deleteWorkflow(id) {
  const query = `
    mutation DeleteWorkflow($id: Int!) {
      delete_workflows_by_pk(id: $id) {
        id
      }
    }
  `;
  return executeGraphQL(query, { id });
}

// ==================== NODES ====================

export async function getNodes(workflowId) {
  const query = `
    query GetNodes($workflow_id: Int!) {
      nodes(where: {workflow_id: {_eq: $workflow_id}}) {
        id
        text
        workflow_id
        created_at
      }
    }
  `;
  return executeGraphQL(query, { workflow_id: workflowId });
}

export async function createNode(workflowId, text) {
  const query = `
    mutation CreateNode($workflow_id: Int!, $text: String!) {
      insert_nodes_one(object: {workflow_id: $workflow_id, text: $text}) {
        id
        text
        workflow_id
        created_at
      }
    }
  `;
  return executeGraphQL(query, { workflow_id: workflowId, text });
}

export async function updateNode(id, text) {
  const query = `
    mutation UpdateNode($id: Int!, $text: String!) {
      update_nodes_by_pk(pk_columns: {id: $id}, _set: {text: $text}) {
        id
        text
        updated_at
      }
    }
  `;
  return executeGraphQL(query, { id, text });
}

export async function deleteNode(id) {
  const query = `
    mutation DeleteNode($id: Int!) {
      delete_nodes_by_pk(id: $id) {
        id
      }
    }
  `;
  return executeGraphQL(query, { id });
}

// ==================== EDGES ====================

export async function getEdges(workflowId) {
  const query = `
    query GetEdges($workflow_id: Int!) {
      edges(where: {workflow_id: {_eq: $workflow_id}}) {
        id
        workflow_id
        source_node_id
        target_node_id
        created_at
      }
    }
  `;
  return executeGraphQL(query, { workflow_id: workflowId });
}

export async function createEdge(workflowId, sourceNodeId, targetNodeId) {
  const query = `
    mutation CreateEdge($workflow_id: Int!, $source_node_id: Int!, $target_node_id: Int!) {
      insert_edges_one(object: {workflow_id: $workflow_id, source_node_id: $source_node_id, target_node_id: $target_node_id}) {
        id
        workflow_id
        source_node_id
        target_node_id
        created_at
      }
    }
  `;
  return executeGraphQL(query, { workflow_id: workflowId, source_node_id: sourceNodeId, target_node_id: targetNodeId });
}

export async function deleteEdge(id) {
  const query = `
    mutation DeleteEdge($id: Int!) {
      delete_edges_by_pk(id: $id) {
        id
      }
    }
  `;
  return executeGraphQL(query, { id });
}

// ==================== FAQs ====================

export async function getFAQs(category = null) {
  let query;
  if (category) {
    query = `
      query GetFAQs($category: String!) {
        faqs(where: {category: {_eq: $category}}, order_by: {created_at: desc}) {
          id
          question
          answer
          category
          created_at
          updated_at
        }
      }
    `;
    return executeGraphQL(query, { category });
  } else {
    query = `
      query GetFAQs {
        faqs(order_by: {created_at: desc}) {
          id
          question
          answer
          category
          created_at
          updated_at
        }
      }
    `;
    return executeGraphQL(query);
  }
}

export async function createFAQ(question, answer, category = null) {
  const query = `
    mutation CreateFAQ($question: String!, $answer: String!, $category: String) {
      insert_faqs_one(object: {question: $question, answer: $answer, category: $category}) {
        id
        question
        answer
        category
        created_at
      }
    }
  `;
  return executeGraphQL(query, { question, answer, category });
}

export async function updateFAQ(id, question, answer, category) {
  const query = `
    mutation UpdateFAQ($id: Int!, $question: String!, $answer: String!, $category: String) {
      update_faqs_by_pk(pk_columns: {id: $id}, _set: {question: $question, answer: $answer, category: $category}) {
        id
        question
        answer
        category
        updated_at
      }
    }
  `;
  return executeGraphQL(query, { id, question, answer, category });
}

export async function deleteFAQ(id) {
  const query = `
    mutation DeleteFAQ($id: Int!) {
      delete_faqs_by_pk(id: $id) {
        id
      }
    }
  `;
  return executeGraphQL(query, { id });
}

export async function getFAQCategories() {
  const query = `
    query GetFAQCategories {
      faqs(distinct_on: category, order_by: {category: asc}) {
        category
      }
    }
  `;
  return executeGraphQL(query);
}

// ==================== CHAT SESSIONS ====================

export async function createChatSession(userId, title = "New Chat Session", category = "General") {
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const query = `
    mutation CreateChatSession($sessionId: String!, $userId: String!, $title: String!, $category: String!) {
      insert_chat_sessions_one(object: {session_id: $sessionId, user_id: $userId, title: $title, category: $category}) {
        id
        session_id
        user_id
        title
        category
        total_messages
        is_active
        created_at
        updated_at
      }
    }
  `;
  return executeGraphQL(query, { sessionId, userId, title, category });
}

export async function getUserChatSessions(userId) {
  const query = `
    query GetUserChatSessions($userId: String!) {
      chat_sessions(where: {user_id: {_eq: $userId}, is_active: {_eq: true}}, order_by: {updated_at: desc}) {
        id
        session_id
        user_id
        title
        category
        total_messages
        is_active
        created_at
        updated_at
      }
    }
  `;
  return executeGraphQL(query, { userId });
}

export async function getChatSession(sessionId) {
  const query = `
    query GetChatSession($sessionId: String!) {
      chat_sessions(where: {session_id: {_eq: $sessionId}}) {
        id
        session_id
        user_id
        title
        category
        total_messages
        is_active
        created_at
        updated_at
      }
    }
  `;
  return executeGraphQL(query, { sessionId });
}

export async function getChatMessages(sessionId) {
  const query = `
    query GetChatMessages($sessionId: String!) {
      chat_messages(where: {session_id: {_eq: $sessionId}}, order_by: {timestamp: asc}) {
        id
        message_id
        session_id
        user_id
        question
        answer
        source
        timestamp
      }
    }
  `;
  return executeGraphQL(query, { sessionId });
}

export async function addChatMessage(sessionId, userId, role, content) {
  const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const query = `
    mutation AddChatMessage($messageId: String!, $sessionId: String!, $userId: String!, $role: String!, $content: String!) {
      insert_chat_messages_one(object: {message_id: $messageId, session_id: $sessionId, user_id: $userId, role: $role, content: $content}) {
        id
        message_id
        session_id
        user_id
        role
        content
        timestamp
      }
    }
  `;
  const result = await executeGraphQL(query, { messageId, sessionId, userId, role, content });
  
  // Update session's total_messages count
  if (result.insert_chat_messages_one) {
    const countQuery = `
      query CountSessionMessages($sessionId: String!) {
        chat_messages_aggregate(where: {session_id: {_eq: $sessionId}}) {
          aggregate {
            count
          }
        }
      }
    `;
    const countResult = await executeGraphQL(countQuery, { sessionId });
    const totalMessages = countResult?.chat_messages_aggregate?.aggregate?.count || 0;
    
    const updateQuery = `
      mutation UpdateSessionMessageCount($sessionId: String!, $totalMessages: Int!) {
        update_chat_sessions(where: {session_id: {_eq: $sessionId}}, _set: {total_messages: $totalMessages}) {
          affected_rows
        }
      }
    `;
    await executeGraphQL(updateQuery, { sessionId, totalMessages });
  }
  
  return result;
}

export async function updateChatSession(sessionId, title, category) {
  const query = `
    mutation UpdateChatSession($sessionId: String!, $title: String!, $category: String!) {
      update_chat_sessions(where: {session_id: {_eq: $sessionId}}, _set: {title: $title, category: $category}) {
        affected_rows
        returning {
          id
          session_id
          title
          category
          updated_at
        }
      }
    }
  `;
  return executeGraphQL(query, { sessionId, title, category });
}

export async function deleteChatSession(sessionId) {
  const query = `
    mutation DeleteChatSession($sessionId: String!) {
      update_chat_sessions(where: {session_id: {_eq: $sessionId}}, _set: {is_active: false}) {
        affected_rows
      }
    }
  `;
  return executeGraphQL(query, { sessionId });
}

export async function clearChatMessages(sessionId) {
  const query = `
    mutation ClearChatMessages($sessionId: String!) {
      delete_chat_messages(where: {session_id: {_eq: $sessionId}}) {
        affected_rows
      }
    }
  `;
  const result = await executeGraphQL(query, { sessionId });
  
  // Reset total_messages count
  if (result.delete_chat_messages) {
    const updateQuery = `
      mutation UpdateSessionMessageCount($sessionId: String!) {
        update_chat_sessions(where: {session_id: {_eq: $sessionId}}, _set: {total_messages: 0}) {
          affected_rows
        }
      }
    `;
    await executeGraphQL(updateQuery, { sessionId });
  }
  
  return result;
}

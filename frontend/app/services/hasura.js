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



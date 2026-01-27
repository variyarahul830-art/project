from fastapi import APIRouter, HTTPException, status
from schemas import NodeCreate, EdgeCreate
from services import hasura_client

router = APIRouter(prefix="/api/graph", tags=["Graph"])

# Node Endpoints

@router.post("/nodes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_node(node: NodeCreate):
    """
    Create a new node in the knowledge graph
    
    - **text**: The node text/concept (required, must be unique)
    """
    try:
        # Check if node already exists
        if await hasura_client.node_exists(node.workflow_id, node.text):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A node with this text already exists"
            )
        
        # Create new node
        db_node = await hasura_client.create_node(node.workflow_id, node.text)
        
        return {
            "success": True,
            "message": "Node created successfully",
            "data": db_node.to_dict()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create node: {str(e)}"
        )

@router.get("/nodes", response_model=dict)
async def get_all_nodes():
    """Get all nodes in the graph"""
    nodes = await hasura_client.get_all_nodes()
    return {
        "success": True,
        "count": len(nodes),
        "data": [node.to_dict() for node in nodes]
    }

@router.get("/nodes/{node_id}", response_model=dict)
async def get_node(node_id: int):
    """Get a specific node by ID"""
    node = await hasura_client.get_node_by_id(node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    return {
        "success": True,
        "data": node.to_dict()
    }

@router.delete("/nodes/{node_id}", response_model=dict)
async def delete_node(node_id: int):
    """Delete a node and all its connected edges"""
    if not await hasura_client.delete_node(node_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    return {
        "success": True,
        "message": "Node deleted successfully"
    }

# Edge Endpoints

@router.post("/edges", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_edge(edge: EdgeCreate):
    """
    Create a new edge between two nodes
    
    - **source_node_id**: ID of the source node
    - **target_node_id**: ID of the target node
    """
    try:
        # Validate nodes exist
        source = await hasura_client.get_node_by_id(edge.source_node_id)
        target = await hasura_client.get_node_by_id(edge.target_node_id)
        if not source or not target:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source or target node does not exist"
            )
        # Enforce same workflow
        if source.get("workflow_id") != target.get("workflow_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and target nodes must belong to the same workflow"
            )
        # Check duplicate edge
        if await hasura_client.edge_exists(edge.workflow_id, edge.source_node_id, edge.target_node_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Edge already exists between these nodes"
            )

        db_edge = await hasura_client.create_edge(
            edge.workflow_id,
            edge.source_node_id,
            edge.target_node_id,
        )
        
        return {
            "success": True,
            "message": "Edge created successfully",
            "data": db_edge.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create edge: {str(e)}"
        )

@router.get("/edges", response_model=dict)
async def get_all_edges():
    """Get all edges in the graph"""
    edges = await hasura_client.get_all_edges()
    return {
        "success": True,
        "count": len(edges),
        "data": [edge.to_dict() for edge in edges]
    }

@router.delete("/edges/{edge_id}", response_model=dict)
async def delete_edge(edge_id: int):
    """Delete an edge"""
    if not await hasura_client.delete_edge(edge_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edge not found"
        )
    return {
        "success": True,
        "message": "Edge deleted successfully"
    }

# Graph Endpoints

@router.get("/", response_model=dict)
async def get_graph():
    """Get complete graph data (all nodes and edges)"""
    graph_data = await hasura_client.get_graph_data()
    return {
        "success": True,
        "nodes": [node.to_dict() for node in graph_data["nodes"]],
        "edges": [edge.to_dict() for edge in graph_data["edges"]]
    }

@router.get("/traverse/{node_id}", response_model=dict)
async def traverse_graph(node_id: int):
    """Get all target nodes connected to a source node"""
    source_node = await hasura_client.get_node_by_id(node_id)
    if not source_node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source node not found"
        )
    
    target_nodes = await hasura_client.get_target_nodes(node_id)
    
    return {
        "success": True,
        "source_node": source_node,
        "target_nodes": target_nodes,
    }

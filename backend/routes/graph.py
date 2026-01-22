from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from schemas import NodeCreate, EdgeCreate
import crud

router = APIRouter(prefix="/api/graph", tags=["Graph"])

# Node Endpoints

@router.post("/nodes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    """
    Create a new node in the knowledge graph
    
    - **text**: The node text/concept (required, must be unique)
    """
    try:
        # Check if node already exists
        if crud.node_exists(db, node.text, node.workflow_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A node with this text already exists"
            )
        
        # Create new node
        db_node = crud.create_node(db, node)
        
        return {
            "success": True,
            "message": "Node created successfully",
            "data": db_node.to_dict()
        }
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A node with this text already exists"
        )

@router.get("/nodes", response_model=dict)
async def get_all_nodes(db: Session = Depends(get_db)):
    """Get all nodes in the graph"""
    nodes = crud.get_all_nodes(db)
    return {
        "success": True,
        "count": len(nodes),
        "data": [node.to_dict() for node in nodes]
    }

@router.get("/nodes/{node_id}", response_model=dict)
async def get_node(node_id: int, db: Session = Depends(get_db)):
    """Get a specific node by ID"""
    node = crud.get_node_by_id(db, node_id)
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
async def delete_node(node_id: int, db: Session = Depends(get_db)):
    """Delete a node and all its connected edges"""
    if not crud.delete_node(db, node_id):
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
async def create_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    """
    Create a new edge between two nodes
    
    - **source_node_id**: ID of the source node
    - **target_node_id**: ID of the target node
    """
    try:
        db_edge = crud.create_edge(db, edge)
        
        return {
            "success": True,
            "message": "Edge created successfully",
            "data": db_edge.to_dict()
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Edge already exists between these nodes"
        )

@router.get("/edges", response_model=dict)
async def get_all_edges(db: Session = Depends(get_db)):
    """Get all edges in the graph"""
    edges = crud.get_all_edges(db)
    return {
        "success": True,
        "count": len(edges),
        "data": [edge.to_dict() for edge in edges]
    }

@router.delete("/edges/{edge_id}", response_model=dict)
async def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    """Delete an edge"""
    if not crud.delete_edge(db, edge_id):
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
async def get_graph(db: Session = Depends(get_db)):
    """Get complete graph data (all nodes and edges)"""
    graph_data = crud.get_graph_data(db)
    return {
        "success": True,
        "nodes": [node.to_dict() for node in graph_data["nodes"]],
        "edges": [edge.to_dict() for edge in graph_data["edges"]]
    }

@router.get("/traverse/{node_id}", response_model=dict)
async def traverse_graph(node_id: int, db: Session = Depends(get_db)):
    """Get all target nodes connected to a source node"""
    source_node = crud.get_node_by_id(db, node_id)
    if not source_node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source node not found"
        )
    
    target_nodes = crud.get_target_nodes(db, node_id)
    
    return {
        "success": True,
        "source_node": source_node.to_dict(),
        "target_nodes": [node.to_dict() for node in target_nodes]
    }

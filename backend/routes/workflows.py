from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import WorkflowCreate
import crud

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow"""
    try:
        db_workflow = crud.create_workflow(db, workflow)
        return {
            "success": True,
            "message": "Workflow created successfully",
            "data": db_workflow.to_dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=dict)
async def get_all_workflows(db: Session = Depends(get_db)):
    """Get all workflows"""
    try:
        workflows = crud.get_all_workflows(db)
        return {
            "success": True,
            "count": len(workflows),
            "data": [w.to_dict() for w in workflows]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{workflow_id}", response_model=dict)
async def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Get a specific workflow"""
    workflow = crud.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return {
        "success": True,
        "data": workflow.to_dict()
    }

@router.get("/{workflow_id}/nodes", response_model=dict)
async def get_workflow_nodes(workflow_id: int, db: Session = Depends(get_db)):
    """Get all nodes in a workflow"""
    workflow = crud.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    nodes = crud.get_workflow_nodes(db, workflow_id)
    return {
        "success": True,
        "count": len(nodes),
        "data": [n.to_dict() for n in nodes]
    }

@router.get("/{workflow_id}/edges", response_model=dict)
async def get_workflow_edges(workflow_id: int, db: Session = Depends(get_db)):
    """Get all edges in a workflow"""
    workflow = crud.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    edges = crud.get_workflow_edges(db, workflow_id)
    return {
        "success": True,
        "count": len(edges),
        "data": [e.to_dict() for e in edges]
    }

@router.delete("/{workflow_id}", response_model=dict)
async def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Delete a workflow"""
    workflow = crud.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    if crud.delete_workflow(db, workflow_id):
        return {
            "success": True,
            "message": "Workflow deleted successfully"
        }
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete workflow"
    )

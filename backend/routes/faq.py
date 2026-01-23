from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import crud
from schemas import FAQCreate, FAQResponse, FAQUpdate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/faq", tags=["FAQ"])


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(faq_data: FAQCreate, db: Session = Depends(get_db)):
    """Create a new FAQ"""
    try:
        faq = crud.create_faq(
            db=db,
            question=faq_data.question,
            answer=faq_data.answer,
            category=faq_data.category
        )
        logger.info(f"✅ FAQ created: {faq.id}")
        return faq
    except Exception as e:
        logger.error(f"❌ Error creating FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create FAQ: {str(e)}"
        )


@router.get("/", response_model=list[FAQResponse])
async def get_all_faqs(category: str = None, db: Session = Depends(get_db)):
    """Get all FAQs, optionally filtered by category"""
    try:
        faqs = crud.get_all_faqs(db=db, category=category)
        logger.info(f"✅ Retrieved {len(faqs)} FAQs")
        return faqs
    except Exception as e:
        logger.error(f"❌ Error retrieving FAQs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve FAQs: {str(e)}"
        )


@router.get("/categories", response_model=list[str])
async def get_faq_categories(db: Session = Depends(get_db)):
    """Get all unique FAQ categories"""
    try:
        categories = crud.get_faq_categories(db=db)
        return categories
    except Exception as e:
        logger.error(f"❌ Error retrieving categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}"
        )


@router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(faq_id: int, db: Session = Depends(get_db)):
    """Get FAQ by ID"""
    try:
        faq = crud.get_faq_by_id(db=db, faq_id=faq_id)
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID {faq_id} not found"
            )
        return faq
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve FAQ: {str(e)}"
        )


@router.get("/search/exact", response_model=FAQResponse)
async def search_faq_exact(question: str, db: Session = Depends(get_db)):
    """Search for FAQ by exact question match"""
    try:
        faq = crud.search_faq_by_question(db=db, question_text=question)
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching FAQ found"
            )
        logger.info(f"✅ Found exact FAQ match for: {question[:50]}...")
        return faq
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error searching FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search FAQ: {str(e)}"
        )


@router.get("/search/partial", response_model=list[FAQResponse])
async def search_faq_partial(question: str, db: Session = Depends(get_db)):
    """Search for FAQs by partial question match"""
    try:
        faqs = crud.search_faq_partial(db=db, question_text=question)
        logger.info(f"✅ Found {len(faqs)} partial FAQ matches for: {question[:50]}...")
        return faqs
    except Exception as e:
        logger.error(f"❌ Error searching FAQs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search FAQs: {str(e)}"
        )


@router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(faq_id: int, faq_data: FAQUpdate, db: Session = Depends(get_db)):
    """Update an FAQ"""
    try:
        faq = crud.update_faq(
            db=db,
            faq_id=faq_id,
            question=faq_data.question,
            answer=faq_data.answer,
            category=faq_data.category
        )
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID {faq_id} not found"
            )
        logger.info(f"✅ FAQ updated: {faq_id}")
        return faq
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update FAQ: {str(e)}"
        )


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    """Delete an FAQ"""
    try:
        success = crud.delete_faq(db=db, faq_id=faq_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID {faq_id} not found"
            )
        logger.info(f"✅ FAQ deleted: {faq_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete FAQ: {str(e)}"
        )

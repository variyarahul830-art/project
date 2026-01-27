from fastapi import APIRouter, HTTPException, status
from services import hasura_client
from schemas import FAQCreate, FAQResponse, FAQUpdate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/faq", tags=["FAQ"])


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(faq_data: FAQCreate):
    """Create a new FAQ"""
    try:
        faq = await hasura_client.create_faq(
            question=faq_data.question,
            answer=faq_data.answer,
            category=faq_data.category,
        )
        logger.info(f"✅ FAQ created: {faq['id']}")
        return FAQResponse.model_validate(faq)
    except Exception as e:
        logger.error(f"❌ Error creating FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create FAQ: {str(e)}"
        )


@router.get("/", response_model=list[FAQResponse])
async def get_all_faqs(category: str = None):
    """Get all FAQs, optionally filtered by category"""
    try:
        faqs = await hasura_client.get_faqs(category=category)
        logger.info(f"✅ Retrieved {len(faqs)} FAQs")
        return [FAQResponse.model_validate(f) for f in faqs]
    except Exception as e:
        logger.error(f"❌ Error retrieving FAQs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve FAQs: {str(e)}"
        )


@router.get("/categories", response_model=list[str])
async def get_faq_categories():
    """Get all unique FAQ categories"""
    try:
        categories = await hasura_client.get_faq_categories()
        return categories
    except Exception as e:
        logger.error(f"❌ Error retrieving categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}"
        )


@router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(faq_id: int):
    """Get FAQ by ID"""
    try:
        faq = await hasura_client.get_faq_by_id(faq_id=faq_id)
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID {faq_id} not found"
            )
        return FAQResponse.model_validate(faq)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve FAQ: {str(e)}"
        )


@router.get("/search/exact", response_model=FAQResponse)
async def search_faq_exact(question: str):
    """Search for FAQ by exact question match"""
    try:
        faq = await hasura_client.search_faq_exact(question)
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching FAQ found"
            )
        logger.info(f"✅ Found exact FAQ match for: {question[:50]}...")
        return FAQResponse.model_validate(faq)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error searching FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search FAQ: {str(e)}"
        )


@router.get("/search/partial", response_model=list[FAQResponse])
async def search_faq_partial(question: str):
    """Search for FAQs by partial question match"""
    try:
        faqs = await hasura_client.search_faq_partial(question)
        logger.info(f"✅ Found {len(faqs)} partial FAQ matches for: {question[:50]}...")
        return [FAQResponse.model_validate(f) for f in faqs]
    except Exception as e:
        logger.error(f"❌ Error searching FAQs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search FAQs: {str(e)}"
        )


@router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(faq_id: int, faq_data: FAQUpdate):
    """Update an FAQ"""
    try:
        faq = await hasura_client.update_faq(
            faq_id=faq_id,
            question=faq_data.question,
            answer=faq_data.answer,
            category=faq_data.category,
        )
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID {faq_id} not found"
            )
        logger.info(f"✅ FAQ updated: {faq_id}")
        return FAQResponse.model_validate(faq)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update FAQ: {str(e)}"
        )


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(faq_id: int):
    """Delete an FAQ"""
    try:
        success = await hasura_client.delete_faq(faq_id=faq_id)
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

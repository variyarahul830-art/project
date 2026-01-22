"""
PDF Text Extraction Service using OCR
Extracts text from PDF files with page tracking using Tesseract OCR
"""

import io
import pytesseract
import fitz
from typing import List, Dict, Any
import logging
import os
from PIL import Image

logger = logging.getLogger(__name__)

# Add Tesseract to PATH before importing
if os.name == 'nt':  # Windows
    tesseract_dir = r'C:\Program Files\Tesseract-OCR'
    if tesseract_dir not in os.environ['PATH']:
        os.environ['PATH'] += f';{tesseract_dir}'
        logger.info(f"✅ Added Tesseract to PATH: {tesseract_dir}")

# Configure Tesseract path
def setup_tesseract():
    """Configure Tesseract path for different OS"""
    if os.name == 'nt':  # Windows
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
            logger.info(f"✅ Tesseract configured at: {tesseract_path}")
            try:
                version = pytesseract.get_tesseract_version()
                logger.info(f"✅ Tesseract version: {version}")
                return True
            except Exception as e:
                logger.error(f"⚠️ Tesseract found but error getting version: {str(e)}")
                return False
        else:
            logger.error(f"❌ Tesseract not found at: {tesseract_path}")
            logger.error(f"❌ Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    else:
        # For Linux/Mac
        pytesseract.pytesseract.pytesseract_cmd = 'tesseract'
        logger.info("Tesseract configured for Linux/Mac")
        return True

setup_tesseract()


class PDFProcessor:
    """Service for extracting text from PDF files"""
    
    @staticmethod
    def _extract_text_from_page_ocr(page) -> str:
        """
        Try to extract text from a PDF page using OCR
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            Extracted text or empty string if OCR fails
        """
        try:
            # Render page as image with 2x zoom for better quality
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Extract text using Tesseract OCR
            text = pytesseract.image_to_string(img)
            if text.strip():
                logger.info(f"🔍 OCR extraction successful - extracted {len(text.strip())} chars")
            else:
                logger.warning(f"🔍 OCR extraction returned empty text")
            return text.strip()
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {str(e)}")
            return ""
    
    @staticmethod
    def _extract_text_from_page_direct(page) -> str:
        """
        Extract text directly from PDF page (for text-based PDFs)
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            Extracted text or empty string if not available
        """
        try:
            text = page.get_text()
            return text.strip()
        except Exception as e:
            logger.debug(f"Direct text extraction failed: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text_with_pages(pdf_content: bytes) -> List[Dict[str, Any]]:
        """
        Extract text from PDF with page information using OCR only (TESTING MODE)
        
        Args:
            pdf_content: Raw PDF file content as bytes
            
        Returns:
            List of dicts with keys: 'text', 'page_number', 'page_count'
        """
        try:
            logger.info(f"Extracting text from PDF ({len(pdf_content)} bytes)...")
            
            # Open PDF from bytes
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            total_pages = len(pdf_document)
            logger.info(f"Total pages in PDF: {total_pages}")
            
            pages_data = []
            
            for page_num in range(total_pages):
                try:
                    page = pdf_document[page_num]
                    
                    # ===== TESTING: Using OCR Only (Direct extraction commented out) =====
                    # Try direct text extraction first (for text-based PDFs)
                    # text = PDFProcessor._extract_text_from_page_direct(page)
                    
                    # Always use OCR for testing
                    logger.info(f"📄 Page {page_num + 1}: Using OCR for testing...")
                    text = PDFProcessor._extract_text_from_page_ocr(page)
                    if text:
                        logger.info(f"✅ Page {page_num + 1}: Successfully extracted via OCR ({len(text)} chars)")
                    # ======================================================================
                    
                    if text:  # Only add non-empty pages
                        pages_data.append({
                            'text': text,
                            'page_number': page_num + 1,
                            'page_count': total_pages
                        })
                    else:
                        logger.warning(f"⚠️ No text extracted from page {page_num + 1}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    continue
            
            pdf_document.close()
            logger.info(f"✅ Successfully extracted {len(pages_data)} pages with text")
            return pages_data
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    @staticmethod
    def extract_full_text(pdf_content: bytes) -> str:
        """
        Extract full text from PDF as a single string using OCR only (TESTING MODE)
        
        Args:
            pdf_content: Raw PDF file content as bytes
            
        Returns:
            Full extracted text
        """
        try:
            # Open PDF from bytes
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            full_text = []
            for page_num in range(len(pdf_document)):
                try:
                    page = pdf_document[page_num]
                    
                    # ===== TESTING: Using OCR Only (Direct extraction commented out) =====
                    # Try direct text extraction first
                    # text = PDFProcessor._extract_text_from_page_direct(page)
                    
                    # Always use OCR for testing
                    logger.info(f"📄 Page {page_num + 1}: Using OCR for testing...")
                    text = PDFProcessor._extract_text_from_page_ocr(page)
                    if text:
                        logger.info(f"✅ Page {page_num + 1}: Successfully extracted via OCR ({len(text)} chars)")
                    # ======================================================================
                    
                    if text:
                        full_text.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    continue
            
            pdf_document.close()
            return "\n\n".join(full_text)
            
        except Exception as e:
            raise Exception(f"Error processing PDF with OCR: {str(e)}")

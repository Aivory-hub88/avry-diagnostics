"""
Document Parser Service - Extracts text from various document formats
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DocumentParser:
    """
    Parses documents and extracts text content.
    Supports PDF, DOCX, CSV, TXT formats.
    """
    
    def parse(self, content: bytes, content_type: str, filename: str) -> Optional[str]:
        """
        Parse document content based on type.
        
        Args:
            content: File content as bytes
            content_type: MIME type
            filename: Original filename
            
        Returns:
            Extracted text content or None if parsing fails
        """
        try:
            if content_type == 'text/plain':
                return self._parse_txt(content)
            elif content_type == 'text/csv':
                return self._parse_csv(content)
            elif content_type == 'application/pdf':
                return self._parse_pdf(content)
            elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return self._parse_docx(content)
            else:
                logger.warning(f"Unsupported content type: {content_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing {filename}: {str(e)}")
            return None
    
    def _parse_txt(self, content: bytes) -> str:
        """Parse plain text file."""
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    return content.decode(encoding)
                except:
                    continue
            return ""
    
    def _parse_csv(self, content: bytes) -> str:
        """Parse CSV file."""
        import csv
        import io
        
        try:
            text = content.decode('utf-8')
            reader = csv.reader(io.StringIO(text))
            rows = list(reader)
            
            # Convert to readable format
            result = []
            for row in rows:
                result.append(" | ".join(row))
            
            return "\n".join(result)
        except Exception as e:
            logger.error(f"CSV parsing error: {str(e)}")
            return ""
    
    def _parse_pdf(self, content: bytes) -> str:
        """Parse PDF file."""
        try:
            # Try using PyPDF2
            import PyPDF2
            import io
            
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            
            return "\n\n".join(text_parts)
            
        except ImportError:
            logger.warning("PyPDF2 not installed. PDF parsing unavailable.")
            return "[PDF parsing requires PyPDF2 library]"
        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")
            return ""
    
    def _parse_docx(self, content: bytes) -> str:
        """Parse DOCX file."""
        try:
            # Try using python-docx
            import docx
            import io
            
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            return "\n\n".join(text_parts)
            
        except ImportError:
            logger.warning("python-docx not installed. DOCX parsing unavailable.")
            return "[DOCX parsing requires python-docx library]"
        except Exception as e:
            logger.error(f"DOCX parsing error: {str(e)}")
            return ""

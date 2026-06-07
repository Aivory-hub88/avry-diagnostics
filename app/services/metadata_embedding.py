"""
Metadata embedding service for Blueprint PDFs.
"""

import io
from typing import Optional
from datetime import datetime

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("Warning: PyPDF2 not installed. PDF metadata embedding will be limited.")

from app.models.blueprint import BlueprintMetadata


class MetadataEmbeddingService:
    """
    Embeds and extracts metadata in Blueprint PDFs.
    
    Two embedding methods:
    1. Visible text in footer (human-readable) - handled by PDF renderer
    2. PDF metadata properties (machine-readable) - handled here
    """
    
    def __init__(self):
        """Initialize metadata embedding service."""
        if not PYPDF2_AVAILABLE:
            print("Warning: Install PyPDF2 for full metadata support: pip install PyPDF2")
    
    def embed_metadata(
        self,
        pdf_bytes: bytes,
        blueprint_id: str,
        schema_version: str,
        system_name: str = "AI System"
    ) -> bytes:
        """
        Embed metadata in PDF for extraction.
        
        Embeds as PDF metadata properties using PyPDF2.
        
        Args:
            pdf_bytes: Original PDF bytes
            blueprint_id: Blueprint identifier
            schema_version: Schema version (e.g., "aivory-v1")
            system_name: System name for title
            
        Returns:
            PDF bytes with embedded metadata
        """
        if not PYPDF2_AVAILABLE:
            # Return original PDF if PyPDF2 not available
            return pdf_bytes
        
        try:
            # Read PDF
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf_writer = PdfWriter()
            
            # Copy all pages
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Add metadata
            metadata = {
                '/Title': f'{system_name} - AI Blueprint',
                '/Author': 'Aivory',
                '/Subject': 'AI System Blueprint',
                '/Keywords': f'blueprint_id:{blueprint_id},schema_version:{schema_version}',
                '/Creator': 'Aivory Blueprint Generator v1.0',
                '/Producer': 'Aivory',
                '/CreationDate': datetime.utcnow().strftime('D:%Y%m%d%H%M%S')
            }
            
            pdf_writer.add_metadata(metadata)
            
            # Write to bytes
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            return output_buffer.read()
            
        except Exception as e:
            print(f"Error embedding metadata: {e}")
            # Return original PDF on error
            return pdf_bytes
    
    def extract_metadata(
        self,
        pdf_bytes: bytes
    ) -> Optional[dict]:
        """
        Extract embedded metadata from PDF.
        
        Tries multiple extraction methods:
        1. Read PDF metadata properties
        2. Parse keywords field for blueprint_id and schema_version
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Dict with blueprint_id and schema_version, or None if not found
        """
        if not PYPDF2_AVAILABLE:
            return None
        
        try:
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            
            # Get metadata
            metadata = pdf_reader.metadata
            
            if not metadata:
                return None
            
            # Extract from Keywords field
            keywords = metadata.get('/Keywords', '')
            
            if 'blueprint_id:' in keywords and 'schema_version:' in keywords:
                # Parse keywords
                parts = keywords.split(',')
                blueprint_id = None
                schema_version = None
                
                for part in parts:
                    if 'blueprint_id:' in part:
                        blueprint_id = part.split('blueprint_id:')[1].strip()
                    elif 'schema_version:' in part:
                        schema_version = part.split('schema_version:')[1].strip()
                
                if blueprint_id and schema_version:
                    return {
                        'blueprint_id': blueprint_id,
                        'schema_version': schema_version
                    }
            
            return None
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return None
    
    def detect_schema_type(
        self,
        pdf_bytes: bytes
    ) -> str:
        """
        Detect Blueprint schema type from PDF.
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Schema type: "aivory-v1", "external-known", or "external-unknown"
        """
        metadata = self.extract_metadata(pdf_bytes)
        
        if not metadata:
            return "external-unknown"
        
        schema_version = metadata.get('schema_version', '')
        
        if schema_version == "aivory-v1":
            return "aivory-v1"
        elif schema_version:
            return "external-known"
        else:
            return "external-unknown"

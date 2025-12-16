import PyPDF2
import docx
import os
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Extract text from various document formats for AI context."""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text content
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Trang {page_num + 1} ---\n"
                    text += page_text
                
                logger.info(f"Extracted {len(text)} chars from PDF: {file_path}")
                return text
                
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
        
        Returns:
            Extracted text content
        """
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            logger.info(f"Extracted {len(text)} chars from DOCX: {file_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting DOCX {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """
        Read plain text file.
        
        Args:
            file_path: Path to TXT file
        
        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            logger.info(f"Read {len(text)} chars from TXT: {file_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error reading TXT {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Auto-detect file type and extract text.
        
        Args:
            file_path: Path to document
        
        Returns:
            Extracted text
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return ""
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return DocumentProcessor.extract_from_pdf(file_path)
        elif ext == '.docx':
            return DocumentProcessor.extract_from_docx(file_path)
        elif ext == '.txt':
            return DocumentProcessor.extract_from_txt(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return ""
    
    @staticmethod
    def chunk_text(text: str, max_chars: int = 10000) -> list[str]:
        """
        Split long text into chunks for context window.
        
        Args:
            text: Long text
            max_chars: Maximum characters per chunk
        
        Returns:
            List of text chunks
        """
        chunks = []
        while len(text) > max_chars:
            # Find last sentence boundary before max_chars
            split_point = text.rfind('.', 0, max_chars)
            if split_point == -1:
                split_point = max_chars
            
            chunks.append(text[:split_point + 1])
            text = text[split_point + 1:]
        
        if text:
            chunks.append(text)
        
        return chunks


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with sample file (if exists)
    sample_text = DocumentProcessor.extract_text("sample_lesson.pdf")
    if sample_text:
        print(f"Extracted text preview:\n{sample_text[:500]}")
        
        chunks = DocumentProcessor.chunk_text(sample_text, max_chars=1000)
        print(f"\nSplit into {len(chunks)} chunks")

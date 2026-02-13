import os
from google import genai
from typing import List, Optional, Dict
import logging
import re
import time
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_TRANSCRIPT_ENTRIES = 50
MAX_ANSWER_WORDS = 45
DEFAULT_MODEL = "gemini-flash-latest"
RAG_CHUNK_SIZE = 500
TRANSCRIPT_DECAY_HOURS = 1

# Load config.env
config_path = Path(__file__).parent / "config.env"
if config_path.exists():
    load_dotenv(config_path)

class AITeachingAssistant:
    """
    AI Teaching Assistant using Google Gemini API.
    Provides context-aware answers based on lecture materials and teacher transcript.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI assistant with Gemini API + RAG.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.is_demo_mode = False
        
        if not self.api_key or self.api_key == "paste_your_api_key_here":
            logger.warning("Gemini API key missing or invalid. AI Assistant running in DEMO mode.")
            self.is_demo_mode = True
            self.client = None
        else:
            try:
                # Force API version v1 to avoid v1beta 404 issues
                self.client = genai.Client(
                    api_key=self.api_key
                )
                logger.info(f"AI Teaching Assistant initialized (v1 API)")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}. Switching to DEMO mode.")
                self.is_demo_mode = True
                self.client = None
        
        # Initialize ChromaDB for RAG (SAFENED VERSION)
        try:
            import chromadb
            from chromadb.config import Settings
            data_dir = Path(__file__).parent / "data" / "vector_db"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=str(data_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name="lecture_content",
                metadata={"description": "Lecture materials for RAG"}
            )
            self.rag_enabled = True
            logger.info(f"Vector DB initialized: {self.collection.count()} chunks loaded")
        except Exception as e:
            logger.warning(f"RAG disabled: {e}")
            self.rag_enabled = False
            self.collection = None
        
        # Initialize defaults
        self.grade_level = "Trung hoc"
        self.teacher_transcript = []
        self.cached_content = None
        self.cache_timestamp = 0
    
    def load_lecture(self, content: str, filename: str = "lecture.txt"):
        """Load lecture content into vector database for RAG."""
        if not self.rag_enabled:
            logger.warning("RAG disabled, skipping indexing")
            return

        if not content or len(content) < 50:
            logger.warning("Content too short to index")
            return
        
        chunks = self._chunk_text(content, max_chars=RAG_CHUNK_SIZE)
        
        try:
            self.collection.delete(where={"source": filename})
        except Exception as e:
            logger.warning(f"Could not clear old content for {filename}: {e}")
        
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_id": i} for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        self.cached_content = None
        logger.info(f"Indexed {len(chunks)} chunks from {filename}")

    def _chunk_text(self, text: str, max_chars: int = RAG_CHUNK_SIZE) -> List[str]:
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para: continue
            if len(current_chunk) + len(para) < max_chars:
                current_chunk += para + "\n\n"
            else:
                if current_chunk: chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        if current_chunk: chunks.append(current_chunk.strip())
        return chunks

    def add_teacher_speech(self, text: str, importance: float = 0.5):
        if any(kw in text.lower() for kw in ["định nghĩa", "công thức", "quan trọng", "chú ý"]):
            importance = 1.0
        self.teacher_transcript.append({'text': text, 'timestamp': time.time(), 'importance': importance})
        if len(self.teacher_transcript) > MAX_TRANSCRIPT_ENTRIES:
            self.teacher_transcript.pop(0)

    def get_recent_transcript(self, last_n_minutes: int = 10) -> str:
        cutoff_time = time.time() - (last_n_minutes * 60)
        recent = [e['text'] for e in self.teacher_transcript if e['timestamp'] > cutoff_time]
        return " ".join(recent[-20:]) if recent else ""

    def _retrieve_context(self, question: str, n_results: int = 3) -> str:
        if not self.rag_enabled or self.collection.count() == 0:
            return "Chưa có tài liệu bài giảng."
        try:
            results = self.collection.query(query_texts=[question], n_results=n_results)
            if results and results['documents'] and results['documents'][0]:
                return "\n\n".join(results['documents'][0])
            return "Chưa có tài liệu bài giảng."
        except Exception as e:
            logger.error(f"RAG error: {e}")
            return "Chưa có tài liệu bài giảng."

    def ask_question(self, question: str, student_id: str = "unknown") -> str:
        logger.info(f"Student {student_id} asked: {question}")
        if self.is_demo_mode:
            return "ERROR: Gemini API Key missing."
        
        try:
            relevant_context = self._retrieve_context(question)
            recent_transcript = self.get_recent_transcript()
            
            prompt = f"Ban la tro giang AI Viet Nam. Hoc sinh hoi: {question}\nContext: {relevant_context}\nTranscript: {recent_transcript}\nTra loi cuc ky ngan gon (<40 tu)."
            
            response = self.client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return "Xin loi em, AI dang ban. Hay hoi giao vien nhe!"

    def detect_visual_aids(self, question: str) -> Dict[str, any]:
        question_lower = question.lower()
        shape_keywords = {
            r'vuong|square': {'type': 'shape', 'param': 'square'},
            r'tron|circle': {'type': 'shape', 'param': 'circle'},
            r'lap phuong|cube': {'type': 'shape', 'param': 'cube'},
        }
        for pattern, info in shape_keywords.items():
            if re.search(pattern, question_lower):
                return {'has_visual': True, 'visual_type': info['type'], 'visual_param': info['param']}
        return {'has_visual': False, 'visual_type': None, 'visual_param': None}

    def ask_question_with_visual(self, question: str, student_id: str = "unknown") -> Dict[str, str]:
        text_answer = self.ask_question(question, student_id)
        visual_info = self.detect_visual_aids(question)
        return {'text': text_answer, 'visual_type': visual_info['visual_type'], 
                'visual_param': visual_info['visual_param'], 'has_visual': visual_info['has_visual']}

    def clear_context(self):
        self.teacher_transcript = []
        self.cached_content = None
        if not self.rag_enabled: return
        try:
            all_ids = self.collection.get()['ids']
            if all_ids: self.collection.delete(ids=all_ids)
        except Exception as e: logger.warning(f"Clear DB error: {e}")

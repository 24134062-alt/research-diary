import os
from google import genai
from typing import List, Optional, Dict
import logging
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        Args:
            api_key: Google AI API key. If None, reads from GEMINI_API_KEY env var.
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
                    api_key=self.api_key, 
                    http_options={'api_version': 'v1'}
                )
                logger.info(f"AI Teaching Assistant initialized (v1 API)")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}. Switching to DEMO mode.")
                self.is_demo_mode = True
                self.client = None
        
        # Initialize ChromaDB for RAG
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
        
        # Initialize defaults
        self.grade_level = "Trung hoc"
        self.teacher_transcript = []  # Will store {text, timestamp, importance}
        self.cached_content = None  # For prompt caching
        self.cache_timestamp = 0
        
        logger.info(f"Vector DB initialized: {self.collection.count()} chunks loaded")
    
    def load_lecture(self, content: str, filename: str = "lecture.txt"):
        """Load lecture content into vector database for RAG."""
        if not content or len(content) < 50:
            logger.warning("Content too short to index")
            return
        
        # Chunk content into paragraphs/sections
        chunks = self._chunk_text(content, max_chars=500)
        
        # Clear old content for this file
        try:
            self.collection.delete(where={"source": filename})
        except:
            pass
        
        # Add chunks to vector DB
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_id": i} for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        
        # Invalidate cache
        self.cached_content = None
        
        logger.info(f"Indexed {len(chunks)} chunks from {filename} into vector DB")
    
    def _chunk_text(self, text: str, max_chars: int = 500) -> List[str]:
        """Split text into semantic chunks."""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) < max_chars:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text[:max_chars]]
    
    def add_teacher_speech(self, text: str, importance: float = 0.5):
        """Add teacher's speech with importance scoring."""
        # Auto-detect importance
        if any(kw in text.lower() for kw in ["định nghĩa", "công thức", "quan trọng", "chú ý"]):
            importance = 1.0
        elif "ví dụ" in text.lower():
            importance = 0.7
        
        self.teacher_transcript.append({
            'text': text,
            'timestamp': time.time(),
            'importance': importance
        })
        
        # Keep top 50 by importance and recency
        if len(self.teacher_transcript) > 50:
            # Sort by importance * recency_weight
            now = time.time()
            scored = []
            for entry in self.teacher_transcript:
                recency = 1.0 - min(0.9, (now - entry['timestamp']) / 3600)  # Decay over 1 hour
                score = entry['importance'] * recency
                scored.append((score, entry))
            
            scored.sort(reverse=True)
            self.teacher_transcript = [e for _, e in scored[:50]]
        
        logger.debug(f"Added teacher speech (importance={importance}): {text[:50]}...")
    
    def get_recent_transcript(self, last_n_minutes: int = 10) -> str:
        """Get recent teacher transcript by actual time."""
        cutoff_time = time.time() - (last_n_minutes * 60)
        recent = [e['text'] for e in self.teacher_transcript if e['timestamp'] > cutoff_time]
        return " ".join(recent[-20:]) if recent else ""
    
    def _route_model(self, question: str, subject: str = "math") -> str:
        """Route question to best model based on complexity."""
        question_lower = question.lower()
        
        # Complex math/reasoning → Pro
        if any(kw in question_lower for kw in ["chứng minh", "giải thích tại sao", "phân tích"]):
            return "gemini-1.5-pro"
        
        # Default: Flash (fast and cheap)
        return "gemini-1.5-flash"
    
    def _retrieve_context(self, question: str, n_results: int = 3) -> str:
        """Retrieve relevant context from vector DB."""
        if self.collection.count() == 0:
            return "Chưa có tài liệu bài giảng."
        
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=min(n_results, self.collection.count())
            )
            
            if results and results['documents'] and results['documents'][0]:
                return "\n\n".join(results['documents'][0])
            return "Chưa có tài liệu bài giảng."
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return "Chưa có tài liệu bài giảng."
    
    def ask_question(self, question: str, student_id: str = "unknown") -> str:
        """
        Ask AI a question with RAG-optimized context.
        
        Args:
            question: Student's question text
            student_id: ID of student asking (for logging)
        
        Returns:
            AI's answer text (concise, < 40 words)
        """
        logger.info(f"Student {student_id} asked: {question}")
        
        if self.is_demo_mode:
            return "ERROR: Gemini API Key missing. Please set GEMINI_API_KEY in .env to use the AI Assistant."
        
        try:
            # 1. Route to best model
            model_name = self._route_model(question)
            
            # 2. Retrieve relevant context via RAG (instead of full lecture)
            relevant_context = self._retrieve_context(question, n_results=3)
            
            # 3. Get recent teacher transcript
            recent_transcript = self.get_recent_transcript()
            
            # 4. Build optimized prompt (much shorter!)
            prompt = f"""
Ban la tro giang AI Viet Nam than thien va thong minh, ho tro hoc sinh {self.grade_level}.

QUAN TRONG - VAI TRO CUA BAN:
- Ban CHI LA AI tro giang, CHI tra loi cau hoi hoc tap
- Ban KHONG CO kha nang gui tin nhan, thong bao, dieu khien thiet bi
- Ban KHONG BAO GIO noi "da gui", "da thong bao", "da nhan" vi ban khong lam duoc dieu do

NOI DUNG LIEN QUAN (tu tai lieu):
{relevant_context}

GIAO VIEN VUA GIANG (10 phut gan nhat):
{recent_transcript if recent_transcript else "Chua co transcript."}

HOC SINH/GIAO VIEN HOI:
{question}

HUONG DAN TRA LOI:
- CUC KY NGAN GON: toi da 40 tu
- Uu tien cau tra loi truc tiep, than thien
- Dung so/ky hieu thay chu khi duoc (vd: "2+2=4")
- Neu chao hoi: dap lai than thien va hoi "Em can ho tro gi?"
- Neu cau hoi ve bai tap/kien thuc: tra loi truc tiep
- Neu yeu cau gui tin nhan/thong bao: noi "Em chi ho tro hoc tap thoi a. De gui thong bao, thay/co dung nut Broadcast nhe!"
- Neu cau hoi ngoai pham vi hoc tap (game, phim): nhac nhe nhang "Minh tap trung hoc bai nhe!"

TRA LOI (than thien, ngan gon):
"""
            
            # 5. Call Gemini API with optimized prompt
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            answer = response.text.strip()
            
            # 6. Smart length limiting (cut at sentence boundary)
            words = answer.split()
            if len(words) > 45:
                # Try to cut at last sentence
                sentences = answer.split('.')
                truncated = ""
                for s in sentences:
                    if len(truncated.split()) + len(s.split()) < 45:
                        truncated += s + "."
                    else:
                        break
                answer = truncated if truncated else " ".join(words[:45]) + "..."
            
            logger.info(f"AI answered via {model_name} ({len(answer)} chars): {answer}")
            return answer
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "Xin loi em, AI dang ban. Hay hoi giao vien nhe!"
    
    def detect_visual_aids(self, question: str) -> Dict[str, any]:
        """
        Detect if question requires visual aids (3D shapes, molecules, etc.)
        
        Returns:
            dict with keys: 'has_visual', 'visual_type', 'visual_param'
        """
        question_lower = question.lower()
        
        # Shape keywords mapping
        shape_keywords = {
            # 2D Shapes
            r'(hinh\s+)?vuong|square': {'type': 'shape', 'param': 'square'},
            r'(hinh\s+)?tron|circle': {'type': 'shape', 'param': 'circle'},

            # 3D Shapes
            r'(hinh\s+)?lap\s+phuong|hinh\s+khoi\s+vuong|cube': {'type': 'shape', 'param': 'cube'},
            r'(hinh\s+)?chop|pyramid': {'type': 'shape', 'param': 'pyramid'},
            r'(hinh\s+)?cau|sphere|qua\s+cau': {'type': 'shape', 'param': 'sphere'},
            r'(hinh\s+)?tru|cylinder': {'type': 'shape', 'param': 'cylinder'},
            r'(hinh\s+)?non|cone': {'type': 'shape', 'param': 'cone'},
            r'hinh\s+hop|rectangular\s+prism': {'type': 'shape', 'param': 'prism'},
            
            # Molecules
            r'h2o|nuoc|phan\s+tu\s+nuoc|water': {'type': 'molecule', 'param': 'h2o'},
            r'co2|cacbon\s+dioxide|khi\s+cacbonic': {'type': 'molecule', 'param': 'co2'},
            r'ch4|metan|methane': {'type': 'molecule', 'param': 'ch4'},
            
            # Coordinate system
            r'he\s+truc|truc\s+toa\s+do|coordinate': {'type': 'coordinate', 'param': 'xyz'},
        }
        
        for pattern, visual_info in shape_keywords.items():
            if re.search(pattern, question_lower):
                logger.info(f"Visual aid detected: {visual_info['type']} - {visual_info['param']}")
                return {
                    'has_visual': True,
                    'visual_type': visual_info['type'],
                    'visual_param': visual_info['param']
                }
        
        return {'has_visual': False, 'visual_type': None, 'visual_param': None}
    
    def ask_question_with_visual(self, question: str, student_id: str = "unknown") -> Dict[str, str]:
        """
        Ask question and detect if visual aids needed.
        
        Returns:
            dict with keys: 'text', 'visual_type', 'visual_param'
        """
        # Get text answer
        text_answer = self.ask_question(question, student_id)
        
        # Detect visual
        visual_info = self.detect_visual_aids(question)
        
        return {
            'text': text_answer,
            'visual_type': visual_info['visual_type'],
            'visual_param': visual_info['visual_param'],
            'has_visual': visual_info['has_visual']
        }
    
    def clear_context(self):
        """Clear all context (for new lesson)."""
        try:
            # Delete all from vector DB
            all_ids = self.collection.get()['ids']
            if all_ids:
                self.collection.delete(ids=all_ids)
        except:
            pass
        
        self.teacher_transcript = []
        self.cached_content = None
        logger.info("Context cleared for new lesson (vector DB + cache + transcript)")
    
    def set_grade_level(self, grade: str):
        """Set grade level for age-appropriate responses."""
        self.grade_level = grade
        logger.info(f"Grade level set to: {grade}")


# Quick test
if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    ai = AITeachingAssistant()
    
    # Load sample lecture
    ai.load_lecture("""
    Bai 5: Phuong trinh bac nhat
    Phuong trinh bac nhat co dang: ax + b = 0
    Nghiem: x = -b/a (voi a khac 0)
    Vi du: 2x + 4 = 0 => x = -4/2 = -2
    """)
    
    # Add teacher speech
    ai.add_teacher_speech("Chu y cac em, phuong trinh bac nhat rat quan trong")
    ai.add_teacher_speech("De giai phuong trinh, ta can chuyen ve va rut gon")
    
    # Ask question
    answer = ai.ask_question("Em khong hieu cach giai phuong trinh 3x + 6 = 0")
    print(f"AI: {answer}")

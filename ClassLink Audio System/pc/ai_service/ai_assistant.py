import os
from google import genai
from typing import List, Optional, Dict
import logging
import re
from pathlib import Path
from dotenv import load_dotenv

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
        Initialize AI assistant with Gemini API.
        
        Args:
            api_key: Google AI API key. If None, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
        
        # New google-genai package
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"  # Free tier, fast
        
        # Context storage
        self.lecture_content = ""
        self.teacher_transcript = []
        self.grade_level = "trung học"
        
        logger.info(f"AI Teaching Assistant initialized with {self.model_name}")
    
    def load_lecture(self, content: str):
        """Load lecture content into AI context."""
        self.lecture_content = content
        logger.info(f"Loaded lecture content: {len(content)} characters")
    
    def add_teacher_speech(self, text: str):
        """Add teacher's speech to transcript for context."""
        self.teacher_transcript.append(text)
        
        # Keep only last 50 entries to manage context size
        if len(self.teacher_transcript) > 50:
            self.teacher_transcript = self.teacher_transcript[-50:]
        
        logger.debug(f"Added teacher speech: {text[:50]}...")
    
    def get_recent_transcript(self, last_n_minutes: int = 10) -> str:
        """Get recent teacher transcript (approximated by last N entries)."""
        # Approximate: assume each entry is ~30 seconds, last 10 min = 20 entries
        recent_count = min(20, len(self.teacher_transcript))
        return " ".join(self.teacher_transcript[-recent_count:])
    
    def ask_question(self, question: str, student_id: str = "unknown") -> str:
        """
        Ask AI a question with full context.
        
        Args:
            question: Student's question text
            student_id: ID of student asking (for logging)
        
        Returns:
            AI's answer text (concise, < 40 words)
        """
        logger.info(f"Student {student_id} asked: {question}")
        
        # Build context-aware prompt
        recent_transcript = self.get_recent_transcript()
        
        prompt = f"""
Ban la tro giang Viet Nam thong minh, ho tro hoc sinh {self.grade_level}.

BAI GIANG HOM NAY:
{self.lecture_content if self.lecture_content else "Chua co tai lieu bai giang."}

GIAO VIEN VUA GIANG (10 phut gan nhat):
{recent_transcript if recent_transcript else "Chua co transcript."}

HOC SINH HOI:
{question}

HUONG DAN TRA LOI:
- CUC KY NGAN GON: toi da 40 tu
- Uu tien cau tra loi truc tiep
- Dung so/ky hieu thay chu khi duoc (vd: "2+2=4")
- Neu cau hoi ngoai pham vi bai giang, tra loi: "Cau hoi nay em nen hoi giao vien nhe!"

TRA LOI (chi noi dung, khong giai thich):
"""
        
        try:
            # Call Gemini API with new package
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            answer = response.text.strip()
            
            # Enforce length limit (fallback safety)
            words = answer.split()
            if len(words) > 45:
                answer = " ".join(words[:45]) + "..."
            
            logger.info(f"AI answered ({len(answer)} chars): {answer}")
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
        self.lecture_content = ""
        self.teacher_transcript = []
        logger.info("Context cleared for new lesson")
    
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

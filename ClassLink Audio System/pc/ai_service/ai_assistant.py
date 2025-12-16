import os
import google.generativeai as genai
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Context storage
        self.lecture_content = ""
        self.teacher_transcript = []
        self.grade_level = "trung học"
        
        logger.info("AI Teaching Assistant initialized with Gemini Pro")
    
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
Bạn là trợ giảng Việt Nam thông minh, hỗ trợ học sinh {self.grade_level}.

📚 BÀI GIẢNG HÔM NAY:
{self.lecture_content if self.lecture_content else "Chưa có tài liệu bài giảng được upload."}

🎤 GIÁO VIÊN VỪA GIẢNG (10 phút gần nhất):
{recent_transcript if recent_transcript else "Chưa có transcript."}

❓ HỌC SINH HỎI:
{question}

HƯỚNG DẪN TRẢ LỜI:
- CỰC KỲ NGẮN GỌN: tối đa 40 từ (hiển thị trên màn hình nhỏ OLED 128x64px)
- Ưu tiên câu trả lời trực tiếp, bỏ lời mở đầu kiểu "Theo như bài giảng..."
- Dùng số/ký hiệu thay chữ khi được (vd: "2+2=4" thay "hai cộng hai bằng bốn")
- Nếu liên quan đến bài giảng, dẫn chiếu cụ thể
- Nếu câu hỏi ngoài phạm vi bài giảng, trả lời: "Câu hỏi này em nên hỏi giáo viên nhé!"

TRẢ LỜI (chỉ nội dung, không giải thích):
"""
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            # Enforce length limit (fallback safety)
            words = answer.split()
            if len(words) > 45:
                answer = " ".join(words[:45]) + "..."
            
            logger.info(f"AI answered ({len(answer)} chars): {answer}")
            return answer
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "Xin lỗi em, AI đang bận. Hãy hỏi giáo viên nhé!"
    
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
    # Example usage
    ai = AITeachingAssistant()
    
    # Load sample lecture
    ai.load_lecture("""
    Bài 5: Phương trình bậc nhất
    Phương trình bậc nhất có dạng: ax + b = 0
    Nghiệm: x = -b/a (với a khác 0)
    Ví dụ: 2x + 4 = 0 => x = -4/2 = -2
    """)
    
    # Add teacher speech
    ai.add_teacher_speech("Chú ý các em, phương trình bậc nhất rất quan trọng")
    ai.add_teacher_speech("Để giải phương trình, ta cần chuyển vế và rút gọn")
    
    # Ask question
    answer = ai.ask_question("Em không hiểu cách giải phương trình 3x + 6 = 0")
    print(f"AI: {answer}")

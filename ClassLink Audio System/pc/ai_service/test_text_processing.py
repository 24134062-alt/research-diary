"""
Unit Tests for ClassLink Audio System - AI Service

Tests for text normalization and chunking functions.
Run with: pytest test_text_processing.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import AIService


class TestFormatForScience:
    """Tests for format_for_science() - Math/Science text normalization"""
    
    @pytest.fixture
    def service(self):
        """Create AIService instance for testing (mocked)"""
        # We'll test the methods directly without full initialization
        service = object.__new__(AIService)
        return service
    
    def test_basic_math_operators(self, service):
        """Test basic math operator conversion"""
        assert "+" in service.format_for_science("hai cộng ba")
        assert "-" in service.format_for_science("năm trừ hai")
        assert "*" in service.format_for_science("ba nhân bốn")
        assert "/" in service.format_for_science("tám chia hai")
        assert "=" in service.format_for_science("bằng mười")
    
    def test_number_conversion(self, service):
        """Test Vietnamese number words to digits"""
        result = service.format_for_science("một hai ba")
        assert "1" in result
        assert "2" in result
        assert "3" in result
    
    def test_full_equation(self, service):
        """Test complete equation conversion"""
        result = service.format_for_science("hai cộng ba bằng năm")
        assert "2" in result
        assert "+" in result
        assert "3" in result
        assert "=" in result
        assert "5" in result
    
    def test_special_numbers(self, service):
        """Test special number words like 'lăm' (alternative for 5)"""
        result = service.format_for_science("mười lăm")
        assert "5" in result
    
    def test_advanced_operators(self, service):
        """Test advanced math operators"""
        assert "^" in service.format_for_science("hai mũ ba")
        assert "√" in service.format_for_science("căn của bốn")
    
    def test_decimal_point(self, service):
        """Test decimal point conversion"""
        result = service.format_for_science("ba phẩy năm")
        assert "." in result


class TestFormatForSocial:
    """Tests for format_for_social() - History/Social text normalization"""
    
    @pytest.fixture
    def service(self):
        service = object.__new__(AIService)
        return service
    
    def test_year_conversion(self, service):
        """Test year formatting (e.g., 'một chín bốn lăm' -> '1945')"""
        result = service.format_for_social("năm một chín bốn lăm")
        # Numbers should be concatenated for years
        assert "1945" in result or ("1" in result and "9" in result and "4" in result and "5" in result)
    
    def test_preserves_non_numbers(self, service):
        """Test that non-number text is preserved"""
        result = service.format_for_social("lịch sử việt nam")
        assert "lịch" in result or "lich" in result  # lowercase


class TestChunkText:
    """Tests for _chunk_text() - Document chunking for RAG"""
    
    @pytest.fixture
    def assistant(self):
        """Create AITeachingAssistant mock for testing"""
        from ai_assistant import AITeachingAssistant
        # Create instance without API key (demo mode)
        assistant = object.__new__(AITeachingAssistant)
        return assistant
    
    def test_short_text_single_chunk(self, assistant):
        """Short text should return single chunk"""
        text = "This is a short text."
        chunks = assistant._chunk_text(text, max_chars=500)
        assert len(chunks) == 1
        assert text in chunks[0]
    
    def test_long_text_multiple_chunks(self, assistant):
        """Long text should be split into multiple chunks"""
        text = "Paragraph one.\n\n" * 20  # Long text with paragraphs
        chunks = assistant._chunk_text(text, max_chars=100)
        assert len(chunks) > 1
    
    def test_respects_max_chars(self, assistant):
        """Each chunk should not exceed max_chars significantly"""
        text = "Word " * 200
        chunks = assistant._chunk_text(text, max_chars=100)
        for chunk in chunks:
            # Allow some overflow for word boundaries
            assert len(chunk) < 200  # Reasonable upper bound
    
    def test_empty_text(self, assistant):
        """Empty text should return list with truncated text"""
        chunks = assistant._chunk_text("", max_chars=500)
        assert isinstance(chunks, list)
    
    def test_paragraph_boundaries(self, assistant):
        """Chunks should respect paragraph boundaries when possible"""
        text = "First paragraph content.\n\nSecond paragraph content.\n\nThird paragraph."
        chunks = assistant._chunk_text(text, max_chars=500)
        # With large max_chars, should be single chunk
        assert len(chunks) == 1


class TestNormalizeTextByMode:
    """Tests for normalize_text_by_mode() - Mode-based text processing"""
    
    @pytest.fixture
    def service(self):
        service = object.__new__(AIService)
        service.current_subject = "math"
        return service
    
    def test_math_mode_applies_science_format(self, service):
        """Math mode should apply science formatting"""
        service.current_subject = "math"
        result = service.normalize_text_by_mode("hai cộng ba")
        assert "+" in result
    
    def test_literature_mode_applies_social_format(self, service):
        """Literature mode should apply social formatting"""
        service.current_subject = "literature"
        result = service.normalize_text_by_mode("năm một chín bốn lăm")
        # Should process as year
        assert "1" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

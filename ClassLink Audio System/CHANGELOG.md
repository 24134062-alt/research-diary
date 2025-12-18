# CHANGELOG

All notable changes to ClassLink Audio System will be documented in this file.

## [2024-12-18] - Web Dashboard UI Update

### Added
- **Notification Badge**: Added notification badge to "Giám Sát & Trợ Lý AI" button
  - Shows count of new student messages when modal is closed
  - Badge clears when modal is opened
  - Badge animates with pulse effect for visibility

- **Mic Remote Panel**: New panel on dashboard showing teacher's mic transcription
  - Real-time display of teacher's voice-to-text from Mic Remote device
  - "Đang thu" status indicator
  - Clear transcription button
  - Broadcast TTS status tags

- **AI Processing Pipeline Documentation**: Updated ARCHITECTURE.md with detailed dual-AI system
  - AI Hỗ Trợ Giáo Viên: Text preprocessing (STT error correction, text normalization, content filtering)
  - AI Trợ Giảng: Question answering for students

### Changed
- `index.html`: Added chat-badge span, mic-transcription-area panel
- `app.js`: Added `updateChatBadge()`, `clearMicTranscription()`, `addMicTranscription()` functions

### Files Modified
- `box/raspberry/api/app/static/index.html`
- `box/raspberry/api/app/static/app.js`
- `ARCHITECTURE.md`

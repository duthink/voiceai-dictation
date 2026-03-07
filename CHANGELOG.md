# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-03-07

### Added

- Initial release
- GPU-accelerated Whisper transcription via faster-whisper (float16)
- Toggle-key dictation with configurable hotkey (default: F9)
- Chunked streaming transcription with overlap buffering
- Word-level deduplication to prevent repeated text at chunk boundaries
- Automatic X11/Wayland detection with xdotool/ydotool fallback
- Self-test utility (`voiceai-selftest`)
- One-command installer (`install.sh`)
- Support for all Whisper models (distil-large-v3, large-v3-turbo, large-v3, small, etc.)
- VAD filtering to skip silence
- CPU fallback mode

### Known Issues

- INT8 quantization crashes on RTX 50-series (Blackwell) GPUs — use float16
- CTranslate2 CUDA kernels not yet optimized for sm_120 compute capability
- On Wayland/GNOME, xdotool fails silently — ydotool is required

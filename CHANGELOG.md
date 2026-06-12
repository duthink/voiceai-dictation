# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-06-12

### Added

- User-editable hotwords file (`~/.config/voiceai/hotwords.txt`) — biases the Whisper decoder toward recognising specific words (brand names, proper nouns, domain terms); re-read on every transcription, no restart needed; created automatically on first run with `VoiceAI` pre-populated
- User-editable corrections file (`~/.config/voiceai/corrections.txt`) — deterministic post-transcription find-and-replace for known mis-transcriptions; format is `wrong phrase = correct phrase`, case-insensitive match, longest phrase wins; re-read on every transcription, no restart needed; created automatically on first run with common patterns pre-populated (e.g. `PingDink = pingd.in`, `Ping Ding = pingd.in`, `pinged in = pingd.in`, `Dutink = duthink`, `do think = duthink`)

### Fixed

- Whisper hallucinations ("Just so", "Hmm", etc.) injected during silence or near-silence: added `condition_on_previous_text=False` to prevent hallucination chaining between chunks, raised `no_speech_threshold` to 0.6, and added a post-transcription filter for known filler phrases
- Overlap-boundary duplicate text: `condition_on_previous_text=False` also prevents the model from re-generating overlap content based on prior output
- VAD tuned for dictation: added `min_speech_duration_ms=150` to ignore noise bursts, increased `speech_pad_ms` to 400 ms to prevent early word cut-off
- Startup now prints paths to both config files so they are always easy to locate
- Repeated words at chunk boundaries caused by punctuation mismatch: dedup now strips punctuation before word comparison so "clients." and "clients" are treated as the same word

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

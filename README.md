# 🎙 VoiceAI Dictation

**Local, privacy-first, GPU-accelerated voice-to-text for Linux.**

Press a key. Speak. Text appears at your cursor. No cloud. No telemetry. No subscriptions.

Works in VS Code, Brave, terminals, Slack — any app with a text input.

---

## How it works

1. Press **F9** (configurable) to start recording
2. Speak naturally — transcribed text streams into the focused text field every few seconds
3. Press **F9** again to stop

That's it. Audio never leaves your machine. The Whisper model runs entirely on your GPU.

## What's under the hood

| Component | Tool | Why |
|-----------|------|-----|
| **STT engine** | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 4× faster than OpenAI Whisper, same accuracy |
| **Model** | `distil-large-v3` | ~2.4 GB VRAM, within 1% WER of large-v3 |
| **Text injection** | xdotool / ydotool | Types into any focused window (X11 + Wayland) |
| **Hotkey** | pynput | Global keyboard listener with debounce |
| **Audio** | sounddevice + PipeWire | Low-latency mic capture, 16 kHz mono |

**Overlap buffering** eliminates the word-splitting problem that plagues chunked transcription. Each audio chunk shares 0.8 seconds of context with the next one, and word-level deduplication ensures nothing gets typed twice.

## Requirements

- **OS:** Ubuntu 22.04+ / Debian 12+ / Fedora 38+ (any Linux with PipeWire or PulseAudio)
- **GPU:** NVIDIA with CUDA support (tested on RTX 5070, 4070, 3060+)
- **VRAM:** 3 GB free minimum (distil-large-v3 uses ~2.4 GB in float16)
- **Python:** 3.10+
- **Display:** X11 (xdotool) or Wayland (ydotool)

### RTX 50-series (Blackwell) users

> **Important:** INT8 quantization is broken on RTX 50-series GPUs due to a
> CTranslate2/cuBLAS incompatibility. VoiceAI defaults to `float16` which works
> perfectly. Do not use `--compute-type int8` on these cards.

## Installation

### Quick install

```bash
git clone https://github.com/duthink/voiceai-dictation.git
cd voiceai-dictation
chmod +x install.sh
./install.sh
```

The installer handles system dependencies (`ffmpeg`, `portaudio`, `xdotool`), installs the Python package, and pre-downloads the Whisper model.

### Manual install

```bash
# System dependencies
sudo apt install -y ffmpeg portaudio19-dev libsndfile1 xdotool

# Create a virtual environment (or use conda/micromamba)
python3 -m venv .venv && source .venv/bin/activate

# Install
pip install -e .
```

### Install with micromamba / conda

```bash
# System dependencies
sudo apt install -y ffmpeg portaudio19-dev libsndfile1 xdotool

# Create environment
micromamba create -n voiceai python=3.12 -y
micromamba activate voiceai

# Clone and install
git clone https://github.com/duthink/voiceai-dictation.git
cd voiceai-dictation
pip install -e .
```

Once installed, run from anywhere without activating the environment:

```bash
# Recommended — no activation needed
micromamba run -n voiceai voiceai

# With flags
micromamba run -n voiceai voiceai --key f9 --chunk 4

# Or activate first, then just run
micromamba activate voiceai
voiceai
```

> **Tip:** The `-e .` (editable) install means any changes you make to the
> source files take effect immediately — no reinstall needed. And since the
> package is installed into the `voiceai` env, `micromamba run -n voiceai voiceai`
> works from any directory.

### Verify

```bash
voiceai-selftest
```

This checks your GPU, CUDA, microphone, text injection, and Whisper model.

## Usage

```bash
# Start with defaults (F9 toggle, 4s chunks, distil-large-v3)
voiceai

# Different hotkey
voiceai --key f8
voiceai --key pause
voiceai --key scroll_lock

# Faster response (shorter chunks)
voiceai --chunk 2

# Different model (smaller = faster, larger = more accurate)
voiceai --model small           # ~2 GB VRAM, fast
voiceai --model large-v3-turbo  # ~2.5 GB, multilingual
voiceai --model large-v3        # ~4.5 GB, max accuracy

# CPU mode (no GPU required, much slower)
voiceai --device cpu --compute-type float32

# All options
voiceai --key f9 --chunk 4 --overlap 0.8 --model distil-large-v3 \
        --compute-type float16 --lang en --beam-size 5
```

### Supported hotkeys

`f1`–`f12`, `scroll_lock`, `pause`

### Workflow tips

- **VS Code:** Click in the editor or Copilot Chat input, press F9, dictate your prompt or code comment
- **Brave/Chrome:** Click any text field (search bar, form, etc.), press F9
- **Terminal:** Works in any terminal emulator — great for composing git commit messages
- **Slack/Discord:** Click the message box, press F9, speak your message

## Configuration

All configuration is via CLI flags. There's no config file to manage.

| Flag | Default | Description |
|------|---------|-------------|
| `--key` | `f9` | Toggle key |
| `--chunk` | `4` | Seconds between transcription chunks |
| `--overlap` | `0.8` | Audio overlap between chunks (seconds) |
| `--model` | `distil-large-v3` | Whisper model |
| `--compute-type` | `float16` | Inference precision |
| `--lang` | `en` | Language code (BCP-47) |
| `--beam-size` | `5` | Beam search width |
| `--device` | `cuda` | `cuda` or `cpu` |
| `--no-vad` | off | Disable silence detection |

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Microphone  │────▶│   Recorder   │────▶│   Whisper    │────▶│   Injector   │
│  (PipeWire)  │     │  (chunks +   │     │  (GPU f16)   │     │  (xdotool/   │
│              │     │   overlap)   │     │              │     │   ydotool)   │
└─────────────┘     └──────────────┘     └──────┬───────┘     └──────────────┘
                                                │
                                         ┌──────▼───────┐
                                         │    Dedup     │
                                         │ (word-level  │
                                         │  overlap     │
                                         │  stripping)  │
                                         └──────────────┘
```

The hotkey listener runs in a background thread. When toggled on, the recorder captures audio into a ring buffer. Every `chunk` seconds, the buffer is drained (keeping an overlap tail), transcribed on the GPU, deduped against the previous chunk's text, and the new words are typed via xdotool/ydotool.

## Development

```bash
# Install with dev dependencies
./install.sh --dev

# Run tests
make test

# Lint
make lint

# Format
make format
```

## Troubleshooting

**No text appears in my app**
- Make sure the target text field is focused before pressing F9
- Test manually: `xdotool type "hello"` — if this doesn't work, xdotool isn't seeing your window
- On Wayland: install ydotool and ensure the ydotoold daemon is running

**"CUBLAS_STATUS_NOT_SUPPORTED" error**
- You're on an RTX 50-series GPU using INT8. Use the default `--compute-type float16`

**High latency / slow transcription**
- Try `--chunk 2` for faster feedback
- Use `--model small` for lighter inference (~2 GB VRAM)
- Ensure CUDA is working: `python -c "import torch; print(torch.cuda.is_available())"`

**Microphone not detected**
- Check with: `parecord --channels=1 --rate=16000 /tmp/test.wav` then `aplay /tmp/test.wav`
- If using Bluetooth headset, it may fall back to low-quality HSP — use a wired mic

**F9 not detected**
- Some laptops require Fn+F9. Check if your ASUS TUF has Fn-lock enabled
- Try a different key: `voiceai --key scroll_lock`

**IBus/Fcitx steals the hotkey**
- Disable IBus hotkey: `gsettings set org.freedesktop.ibus.general.hotkey triggers "[]"`

## Roadmap

- [ ] System tray indicator (recording/idle status)
- [ ] Ollama post-processing for grammar cleanup
- [ ] Wayland-native global shortcuts (xdg-desktop-portal)
- [ ] GNOME autostart .desktop file generator
- [ ] Audio feedback (beep on start/stop)
- [ ] Configurable text post-processing (capitalization, punctuation)

## License

MIT — see [LICENSE](LICENSE).

## Credits

Built on top of these excellent open-source projects:

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — CTranslate2-based Whisper inference
- [OpenAI Whisper](https://github.com/openai/whisper) — the original speech recognition model
- [pynput](https://github.com/moses-palmer/pynput) — cross-platform input monitoring
- [sounddevice](https://github.com/spatialaudio/python-sounddevice) — PortAudio bindings for Python

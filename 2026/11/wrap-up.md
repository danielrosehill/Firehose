# Firehose wrap-up for November 2026

13 repos, 3 datasets, 2 models created across 3 days.

## GitHub Repositories

13 repos created

- 2026-11-01: **[Audio Dataset Backup](https://github.com/danielrosehill/Audio-Dataset-Backup)** (GitHub, Tool): Gathers Daniel's Hugging Face audio datasets into a pinned, checksummed, disc-sized point-in-time archive (M-DISC / cloud)
- 2026-11-01: **[GitHub Discovery](https://github.com/danielrosehill/GitHub-Discovery)** (GitHub, Tool): Android app for discovering GitHub repos: browse topics, use desktop-grade advanced search operators on mobile, sort by newest or most starred, and star repos into Lists.
- 2026-11-02: **[Claude Konsole Setup](https://github.com/danielrosehill/Claude-Konsole-Setup)** (GitHub, Tool): Konsole settings for running Claude Code sessions: window-close protection, no single-tab prompt, split layout; apply.sh for other machines
- 2026-11-02: **[Daniel Handwriting Recognition](https://github.com/danielrosehill/Daniel-Handwriting-Recognition)** (GitHub, Tool): Fine-tuning a handwriting recognition (HTR) model on Daniel's handwriting: data collection plan, ground truth, training
- 2026-11-02: **[Laptop Search 1126](https://github.com/danielrosehill/Laptop-Search-1126)** (GitHub, Documentation): Laptop search, November 2026: requirements, spec notes and voice-note transcripts.
- 2026-11-02: **[Local TTS Plugin](https://github.com/danielrosehill/Local-TTS-Plugin)** (GitHub, Agent plugin): Local text-to-speech for Claude Code: Kokoro (CPU), NeuTTS Air (CPU cloning), Chatterbox (ROCm/CUDA). Installs, registers and runs local TTS models.
- 2026-11-02: **[Local UTC Widget](https://github.com/danielrosehill/Local-UTC-Widget)** (GitHub, Tool): Android home-screen widget: local time and UTC side by side, 24-hour, with optional date, UTC offset and font choice
- 2026-11-02: **[Transcription Pipeline](https://github.com/danielrosehill/Transcription-Pipeline)** (GitHub, Agent plugin): Agent skills for transcription in stages: retrieve, preprocess (EQ, denoise, VAD), transcribe (OpenRouter/Gemini, AssemblyAI, local Whisper/Parakeet), clean, label speakers, reshape, Typst PDF, save
- 2026-11-02: **[Useful User Manuals](https://github.com/danielrosehill/Useful-User-Manuals)** (GitHub, Tool): Turn bloated product manuals into useful ones: fetch, trim to your language, rewrite, or one-task how-to PDFs, always citing the original.
- 2026-11-03: **[ChatGPT Workspace Agents Claude Plugin](https://github.com/danielrosehill/ChatGPT-Workspace-Agents-Claude-Plugin)** (GitHub, Agent plugin): Builds and manages ChatGPT Workspace Agents from Claude Code by driving the agent builder in a browser, since OpenAI has no public API for creating them.
- 2026-11-03: **[Guava Health Plugin](https://github.com/danielrosehill/Guava-Health-Plugin)** (GitHub, Agent plugin): Unofficial plugin and Python CLI for the Guava Health API: logs medications, symptoms and readings, and reviews the data, including for dependents on a family plan.
- 2026-11-03: **[IP Cam Lockdown](https://github.com/danielrosehill/IP-Cam-Lockdown)** (GitHub, Documentation): Forensics and a playbook for running cheap AliExpress IP cameras local-only: how each one reaches the vendor cloud, and how to cut it off.
- 2026-11-03: **[Network Forensics Plugin](https://github.com/danielrosehill/Network-Forensics-Plugin)** (GitHub, Agent plugin): Skills for tracing what a device on a home network talks to, documenting it, blocking it at the firewall and verifying the lockdown.

## Datasets

3 datasets created

- 2026-11-02: **[Voice Command Sentences](https://huggingface.co/datasets/danielrosehill/Voice-Command-Sentences)** (Hugging Face, Audio dataset): One speaker reading desktop voice commands for a KDE Plasma voice-command agent: launching, switching to and closing apps (Konsole, Kate, Dolphin, Kdenlive, Audacity), browser and terminal tabs,...
- 2026-11-03: **[English Hebrew Mixed Sentences](https://huggingface.co/datasets/danielrosehill/English-Hebrew-Mixed-Sentences)** (Hugging Face, Training dataset): English sentences with Hebrew words and phrases mixed in, for training and evaluating speech-to-text for English speakers in Israel.
- 2026-11-03: **[Term Context Sentences](https://huggingface.co/datasets/danielrosehill/term-context-sentences)** (Hugging Face, Training dataset): Training data for writing short read-aloud sentences that use a given term in a given context, covering romanized Hebrew and Yiddish, Israeli names and tech vocabulary.

## AI Models

2 models created

- 2026-11-03: **[Contextual Sentence Creator](https://huggingface.co/danielrosehill/Contextual-Sentence-Creator)** (Hugging Face, Fine-tuned model): LoRA fine-tune of Granite 4.2 3B that returns natural sentences using a given term in a given context, for recording speech-recognition training data.
- 2026-11-03: **[Contextual Sentence Creator GGUF](https://huggingface.co/danielrosehill/Contextual-Sentence-Creator-GGUF)** (Hugging Face, Quantised model): GGUF builds of Contextual-Sentence-Creator in Q4_K_M and Q8_0, for running it with llama.cpp.

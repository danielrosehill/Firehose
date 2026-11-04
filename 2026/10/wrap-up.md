# Firehose wrap-up for October 2026

9 repos, 5 datasets, 3 models created across 4 days.

## GitHub Repositories

9 repos created

- 2026-10-28: **[Noise Pollution Analysis](https://github.com/danielrosehill/Noise-Pollution-Analysis)** (GitHub, Agent plugin): Agent skills to document home noise pollution and analyse recordings at the frequency level: hums, tones, low-frequency drone, cycling.
- 2026-10-28: **[Tech Graphics Benchmark](https://github.com/danielrosehill/Tech-Graphics-Benchmark)** (GitHub, Evaluation): Lightweight periodic check: can image models make colourful, stylised tech diagrams with exact text and correct arrows? Text-to-image and image-to-image.
- 2026-10-29: **[Keyclick Detector](https://github.com/danielrosehill/Keyclick-Detector)** (GitHub, Tool): Detects keyboard and mouse clicks at the start and end of voice-training recordings so they can be trimmed. Trained on real recorder takes.
- 2026-10-29: **[Rclone Manager](https://github.com/danielrosehill/Rclone-Manager)** (GitHub, Agent plugin): Agent skills for routine rclone admin: install, remotes, mounts, config backup and migration, docs lookup
- 2026-10-30: **[Podcast Light Edit Chain](https://github.com/danielrosehill/Podcast-Light-Edit-Chain)** (GitHub, Tool): One-command light edit for spoken-word recordings: cut ums with the Uhm frame classifier (no ASR), shorten long pauses, voice-fitted EQ, -16 LUFS. With a measured demo.
- 2026-10-31: **[AI Assistant Triage](https://github.com/danielrosehill/AI-Assistant-Triage)** (GitHub, Documentation): A public notebook of quick, point-in-time triage scorecards for conversational AI tools with native agentic capabilities, looked at through one lens: how well they integrate with external tools (MCP...
- 2026-10-31: **[Dictation Format Adapters](https://github.com/danielrosehill/Dictation-Format-Adapters)** (GitHub, Tool): Bounded catalogue of LoRA format adapters (shopping list, emails, blog outline, calendar JSON) on a 0.6B dictation cleanup model
- 2026-10-31: **[Flow Control](https://github.com/danielrosehill/Flow-Control)** (GitHub, Agent plugin): Stay in flow: capture and triage mid-thread ideas, requests and bugs into in-repo sprints and backlog, then carry on. Agent skills.
- 2026-10-31: **[OpenRouter Batch Notes](https://github.com/danielrosehill/OpenRouter-Batch-Notes)** (GitHub, Tool): Research notebook on batch inference via OpenRouter: Batch API mechanics, batch vs sync pricing, traps. Written by Claude Opus 5.5, 2026-10-31.

## Datasets

5 datasets created

- 2026-10-28: **[Tech Graphics Benchmark](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark)** (Hugging Face, Evaluation dataset): Test prompts for Tech-Graphics-Benchmark: can an image model make a characterful banner or a restyled diagram for a tech repo or blog post without getting the text or the arrows wrong?
- 2026-10-28: **[Tech Graphics Benchmark Ratings](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark-Ratings)** (Hugging Face, Evaluation dataset): Raw human evaluation data for Tech-Graphics-Benchmark: one JSON file per annotated generation, written by the annotation Space.
- 2026-10-28: **[Tech Graphics Benchmark Runs](https://huggingface.co/datasets/danielrosehill/Tech-Graphics-Benchmark-Runs)** (Hugging Face, Evaluation dataset): Every image generated for Tech-Graphics-Benchmark, one folder per round.
- 2026-10-29: **[ASR Cleanup Before After](https://huggingface.co/datasets/danielrosehill/ASR-Cleanup-Before-After)** (Hugging Face, Reference dataset): No description published.
- 2026-10-31: **[OR Batch Inference Models](https://huggingface.co/datasets/danielrosehill/OR-Batch-Inference-Models)** (Hugging Face, Reference dataset): Every model with a :batch id on OpenRouter on 2026-10-31 (71 models), with batch and sync prices, the providers that serve batch, and a price-tier label.

## AI Models

3 models created

- 2026-10-29: **[Hey Yossi microWakeWord](https://huggingface.co/danielrosehill/Hey-Yossi-microWakeWord)** (Hugging Face, Other): A custom "Hey Yossi" wake word for microWakeWord, trained 2026-10-29. It is a streaming, int8-quantised TFLite model of 61 KB.
- 2026-10-29: **[Hey Yossi openWakeWord](https://huggingface.co/danielrosehill/Hey-Yossi-openWakeWord)** (Hugging Face, Other): A custom "Hey Yossi" wake word for openWakeWord, trained 2026-10-29 for a personal voice assistant.
- 2026-10-29: **[S1 ASR Cleanup](https://huggingface.co/danielrosehill/S1-ASR-Cleanup)** (Hugging Face, Fine-tuned model): S1-ASR-Cleanup is a fine-tune of S1-mini by Superwhisper (superwhisper/s1-mini, Qwen3-0.6B) that cleans raw speech-to-text dictation the way one user edits his own.

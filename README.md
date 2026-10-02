# ⚔️ CK3 DNA Generator

Generate **Crusader Kings 3 portrait DNA codes** from any face photo using local AI — no cloud, no API keys, completely free.

![CK3 DNA Generator](https://img.shields.io/badge/Crusader%20Kings%203-DNA%20Generator-c8922a?style=for-the-badge&logo=data:image/png;base64,)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-0.84-0175c2?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-llava-black?style=for-the-badge)

---

## ✨ What it does

1. You load a face photo
2. The AI analyzes facial features (skin tone, eye color, hair, jaw, lips...)
3. The app generates a valid CK3 DNA code ready to paste in the Portrait Editor

---

## 🖥️ Requirements

- Windows 10/11 (64-bit)
- Python 3.10 or higher → [python.org](https://www.python.org/downloads/)
- Ollama → [ollama.com](https://ollama.com/download)
- Ollama runs locally and automatically uses a supported GPU when available; CPU works too. GPU support depends on the drivers and Ollama installation on each machine.

---

## 🚀 Installation

### 1. Install Ollama and download the vision model
```bash
ollama pull llava
```

### 2. Clone this repository
```bash
git clone https://github.com/YOUR_USERNAME/CK3-DNA-Generator.git
cd CK3-DNA-Generator
```

### 3. Create a virtual environment and install dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the app
```bash
python main.py
```

### Verify GPU usage

Generate DNA, then run `ollama ps` in another terminal. Its `PROCESSOR` column shows whether the model is using GPU or CPU. The app also displays Ollama's GPU/CPU allocation after each generation. If it reports CPU, install or update the GPU driver and restart Ollama.

---

## 🎮 How to use

1. Make sure Ollama is running (`ollama serve` in a terminal)
2. Launch the app with `python main.py`
3. Load a face photo (JPG, PNG or WEBP — frontal, well-lit photos work best)
4. Select **Female** or **Male**
5. Click **Generate DNA** and wait a few seconds
6. Click **Copy DNA**
7. In CK3: open the console with `~` → type `portrait_editor` → click **Paste Persistent DNA**

---

## 💡 Tips for best results

- Use **frontal portraits** with clear lighting
- Avoid heavy filters, sunglasses or extreme angles
- Close-up face shots work better than full-body photos
- The AI runs locally — your photos are never uploaded anywhere

---

## 🛠️ Tech stack

| Tool | Purpose |
|------|---------|
| [Flet](https://flet.dev) | Desktop UI framework |
| [Ollama](https://ollama.com) | Local AI inference |
| [LLaVA](https://llava-vl.github.io) | Vision-language model for face analysis |

---

## ⚠️ Disclaimer

This tool is a fan-made project and is **not affiliated with Paradox Interactive**. Crusader Kings 3 is a trademark of Paradox Interactive. Use this tool responsibly and in accordance with the game's modding guidelines.

---

## 📺 See it in action

Video tutorial coming soon on YouTube!

---

## 📄 License

MIT License — free to use, modify and share.

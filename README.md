# 1-Click IG Post (Streamlit)

Generates a brand-safe **image**, **caption**, and **hashtags** for Instagram/Facebook with a quick compliance check.
This README covers the **Streamlit app only** (no scheduling/Make).

---

## Features

* Service-specific image generation (no faces/procedures/text).
* Caption + 10 hashtags (local + niche), JSON-strict.
* Simple brand-safety heuristics (flags risky phrases).
* One-click downloads: image (`.png`) and caption (`.txt`).

---

## Requirements

* Python 3.9+
* OpenAI API key

---

## Setup

```bash
# 1) Create & activate a virtual environment
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\activate

# 2) Install dependencies
pip install streamlit openai pillow python-dotenv
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

Alternatively, set it in your shell:

```bash
# macOS/Linux
export OPENAI_API_KEY="sk-..."
# Windows (PowerShell)
setx OPENAI_API_KEY "sk-..."
```

---

## Run

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit.

---

## Usage

1. Select **Service** and **Tone**; provide **Angle/Hook** and **CTA**.
2. Click **Generate**.
3. Review the image, caption, hashtags, and safety status.
4. **Download** the image and caption for manual posting.

---

## Configuration

* `SERVICES`: dropdown items shown to users.
* `TONES`: tone presets.
* `LOCAL_TAGS`: default/local hashtags used to top up to 10.
* `RED_FLAGS`: phrases that trigger the warning banner.
* `generate_image_url(...)` / `generate_image(...)`: prompt logic tied to service/tone/caption.

> The image generator varies visuals by **service**, **tone**, and **caption/angle** while keeping clinic-safe constraints (no identifiable faces, no procedures, no text/logos).

---

## How It Works

* **Caption/Hashtags:** `chat.completions.create` with `response_format={"type":"json_object"}` for reliable JSON.
* **Image:** `images.generate` with a service-specific brief → returns a hosted URL (or base64, depending on function used).
* **Safety check:** simple substring search against `RED_FLAGS`.

---

## Troubleshooting

**VS Code shows “Import could not be resolved (Pylance)”**
Use Command Palette → **Python: Select Interpreter** → choose the `venv`.

**“Missing OPENAI\_API\_KEY”**
Add it to `.env` or export in shell, then restart `streamlit`.

**Model returns non-JSON**
Ensure `response_format={"type": "json_object"}` is set; fallback code still runs.

**Images look too similar**
Edit `SERVICE_BRIEFS`, `STYLE_VARIANTS`, and `PALETTE_VARIANTS` in the image function.

---

## Security Notes

* Don’t commit `.env` or API keys.
* Always review outputs for compliance before posting (heuristics are not a legal guarantee).

---

## Roadmap

* Posting via Instagram Graph API (requires Page/IG setup and permissions).
* Comment/DM autoresponder (pre-approved responses).
* Basic analytics (save runs to CSV/DB; track engagement externally).

---

## License

Internal demo use. Add a license if distributing.

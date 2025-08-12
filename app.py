import os, io, json, base64, datetime, random, textwrap
from dataclasses import dataclass
from typing import List
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# ---- Setup ----
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Use the official OpenAI SDK (>=1.0)
try:
    from openai import OpenAI
except Exception:
    st.stop()

if not OPENAI_API_KEY:
    st.error("Missing OPENAI_API_KEY. Set it in your environment and restart.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ---- App chrome ----
st.set_page_config(page_title="Arkansas Health & Aesthetics - 1-Click IG Post", page_icon="✨", layout="centered")
st.title("✨ Arkansas Health & Aesthetics — 1-Click IG Post")
st.caption("Generates a brand-safe image, caption, and hashtags for a quick demo.")

# ---- Presets ----
SERVICES = [
    "Chiropractic wellness",
    "Medical weight loss",
    "IV therapy / hydration",
    "Regenerative wellness (educational)",
    "General wellness tip"
]

TONES = ["Friendly", "Warm professional", "Educational"]

LOCAL_TAGS = [
    "bentonville", "northwestarkansas", "nwa", "arkansashealth", "arkansaswellness",
    "wellnessjourney", "selfcare", "healthyhabits", "cliniclife", "feelbetter"
]

RED_FLAGS = [
    "guarantee", "guaranteed", "cure", "100%", "before and after", "before/after",
    "dm for medical advice", "no side effects", "instant results"
]

@dataclass
class GenResult:
    caption: str
    hashtags: List[str]
    image: Image.Image

# ---- Helpers ----
def generate_caption_and_tags(service: str, angle: str, cta: str, tone: str) -> dict:
    system = (
        "You are a social media assistant for a medical clinic in Bentonville, Arkansas."
        " Write Instagram captions in a friendly, professional, compliant tone."
        " Avoid PHI, medical advice, guaranteed results, before/after claims,"
        " or unapproved indications. Prefer education, benefits, and lifestyle framing."
        " Keep to <125 characters. End with a gentle CTA. Return compact JSON."
    )
    user = (
        f"Service: {service}\n"
        f"Angle: {angle}\n"
        f"CTA: {cta}\n"
        f"Tone: {tone}\n"
        "Audience: adults in Northwest Arkansas.\n"
        "Return JSON with keys: caption (string), hashtags (array of 10, lowercase, niche+local mix)."
    )

    resp = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
    )
    content = resp.choices[0].message.content.strip()

    # Be forgiving if the model returns plain text; wrap it
    try:
        data = json.loads(content)
    except Exception:
        # Fallback: build hashtags by mixing local set
        tags = LOCAL_TAGS[:]
        data = {"caption": content, "hashtags": tags[:10]}

    # Ensure hashtag hygiene
    hashtags = []
    for h in data.get("hashtags", []):
        h = h.strip().lower().replace("#","")
        if h and h not in hashtags:
            hashtags.append(h)
    # Top up to 10 with locals
    for h in LOCAL_TAGS:
        if len(hashtags) >= 10:
            break
        if h not in hashtags:
            hashtags.append(h)

    data["hashtags"] = hashtags[:10]
    return data

def generate_image(service: str, angle: str, tone: str, caption: str = "") -> Image.Image:
    """
    Generates a brand-safe image tailored to the selected service and copy.
    No text/logos. Subtle randomness for variety.
    """

    # --- service-specific visual briefs (no people/procedures) ---
    SERVICE_BRIEFS = {
        "Medical weight loss": (
            "Modern kitchen or clinic nutrition display; fresh produce, water bottle, journal, "
            "measuring tape on table; calm, motivating wellness vibe."
        ),
        "Chiropractic wellness": (
            "Serene therapy room; chiropractic table, rolled towels, spine model as abstract decor; "
            "soft daylight; minimalist, clean lines."
        ),
        "IV therapy / hydration": (
            "Calm infusion lounge; IV stand and bag visible as objects (not attached to a person), "
            "cozy blanket on chair, citrus water on side table; spa-like atmosphere."
        ),
        "Regenerative wellness (educational)": (
            "Abstract cellular/leaf motifs with clean lab glassware on a tray; soft bokeh; "
            "scientific yet soothing aesthetic."
        ),
        "General wellness tip": (
            "Spa-like still life with plants, diffuser, folded towels, sunlight across a wood surface; "
            "balanced composition, airy feel."
        ),
    }

    # --- small style/palette variations to prevent repetition ---
    STYLE_VARIANTS = [
        "soft natural lighting, pastel neutrals, matte textures",
        "bright overcast lighting, airy whites, light wood accents",
        "warm morning light, gentle shadows, subtle film grain",
        "cool daylight, glass and steel accents, minimal reflections",
    ]
    PALETTE_VARIANTS = [
        "palette of sand beige, eucalyptus green, and off-white",
        "palette of pearl white, warm taupe, and sage",
        "palette of cool gray, linen, and pale teal",
        "palette of ivory, blush, and soft stone",
    ]

    # --- tie visuals to the copy without leaking claims ---
    caption_excerpt = " ".join(caption.split()[:14]) if caption else angle
    # Keep excerpt safe/neutral
    caption_excerpt = textwrap.shorten(caption_excerpt, width=120, placeholder="")

    base_constraints = (
        "Ad-safe, text-free, no logos, no needles in skin, no before/after, "
        "professional clinic photography, high detail."
    )

    brief = SERVICE_BRIEFS.get(service, SERVICE_BRIEFS["General wellness tip"])
    style = random.choice(STYLE_VARIANTS)
    palette = random.choice(PALETTE_VARIANTS)

    # Tone hint (very light influence)
    tone_hint = {
        "Friendly": "inviting, approachable composition",
        "Warm professional": "polished, trustworthy composition",
        "Educational": "clean, informational composition",
    }.get(tone, "inviting, approachable composition")

    prompt = (
        f"{brief} {base_constraints} {style}. {palette}. "
        f"Visual narrative aligned with this theme: '{caption_excerpt}'. "
        f"Overall tone: {tone_hint}."
    )

    img = client.images.generate(
        model="gpt-image-1",
        size="1024x1024",
        prompt=prompt
    )
    b64 = img.data[0].b64_json
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def compliance_flags(text: str) -> List[str]:
    t = text.lower()
    return [w for w in RED_FLAGS if w in t]

def render_copy_block(caption: str, hashtags: List[str]):
    joined = " ".join(f"#{h}" for h in hashtags)
    st.write("**Caption**")
    st.write(caption)
    st.write("**Hashtags**")
    st.code(joined)

def save_image(image: Image.Image) -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"post_image_{ts}.png"
    image.save(path, format="PNG")
    return path

# ---- UI ----
with st.form("gen"):
    col1, col2 = st.columns(2)
    with col1:
        service = st.selectbox("Service", SERVICES, index=1)
        tone = st.selectbox("Tone", TONES, index=1)
    with col2:
        angle = st.text_input("Angle/Hook", "Seasonal wellness tip")
        cta = st.text_input("CTA", "Book a consult this week")
    submitted = st.form_submit_button("Generate")

if submitted:
    with st.spinner("Drafting caption and hashtags…"):
        data = generate_caption_and_tags(service, angle, cta, tone)
    with st.spinner("Generating brand-safe image…"):
        image = generate_image(service, angle, tone, data["caption"])

    flags = compliance_flags(data["caption"])
    st.image(image, use_container_width=True)
    render_copy_block(data["caption"], data["hashtags"])

    if flags:
        st.warning("Review needed: potential risk phrases detected → " + ", ".join(flags))
    else:
        st.success("Brand-safety check passed (heuristic). Please still review before posting.")

    # Download helpers
    img_path = save_image(image)
    st.download_button("Download Image", data=open(img_path, "rb"), file_name=os.path.basename(img_path), mime="image/png")

    post_text = data["caption"] + "\n\n" + " ".join(f"#{h}" for h in data["hashtags"])
    st.download_button("Download Caption.txt", data=post_text.encode("utf-8"), file_name="caption.txt", mime="text/plain")

# ---- Footer ----
with st.expander("Notes & next steps"):
    st.markdown(
        "- This demo purposefully avoids scheduling. "
        "You can paste the content into IG/FB now.\n"
        "- Next step options: Make.com → Instagram Graph API; Runway for Reel ideas; comment autoresponder; metrics logging."
    )

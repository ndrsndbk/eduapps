# app.py
import os
import io
from datetime import datetime
import urllib.parse

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ----------------------------
# App config + light styling
# ----------------------------
st.set_page_config(page_title="Neuro Niche – Neurodiversity in Schools (Fundamentals)", page_icon="🧠")

# Brand colors
SAGE = "#DDE6D5"; TEAL = "#2E7D7C"; SAND = "#F3EEE6"; INK = "#0F172A"

st.markdown(f"""
<style>
html, body, [class*="css"] {{ background-color: {SAND} !important; }}
.stButton > button {{ border-radius: .75rem !important; height: 2.8rem !important; }}
.block-container {{ padding-top: 1.25rem !important; padding-bottom: 2rem !important; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Paths (auto-create on first run)
# ----------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
CERT_DIR = os.path.join(DATA_DIR, "certificates")
LOG_PATH = os.path.join(DATA_DIR, "completions.csv")
os.makedirs(CERT_DIR, exist_ok=True)

# ----------------------------
# Session state
# ----------------------------
if "step" not in st.session_state:    st.session_state.step = 0   # 0 = pre-start
if "started" not in st.session_state: st.session_state.started = False
if "answers" not in st.session_state: st.session_state.answers = {}
if "name" not in st.session_state:    st.session_state.name = ""
if "email" not in st.session_state:   st.session_state.email = ""
if "score" not in st.session_state:   st.session_state.score = 0
if "finished" not in st.session_state:st.session_state.finished = False

# ----------------------------
# Helpers: log + certificate
# ----------------------------
def save_completion(name: str, email: str, score: int):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = {"timestamp_utc": ts, "name": name, "email": email, "score": score}
    if os.path.exists(LOG_PATH):
        try:
            df = pd.read_csv(LOG_PATH)
        except Exception:
            df = pd.DataFrame(columns=["timestamp_utc", "name", "email", "score"])
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(LOG_PATH, index=False)

def _hex_to_rgb(hx): 
    hx = hx.lstrip("#"); return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))

def generate_certificate_bytes(name: str, score: int):
    """Create a PNG certificate (bytes) and save a copy to data/certificates."""
    W, H = (1654, 2339)  # A4 ~150dpi
    bg = Image.new("RGB", (W, H), _hex_to_rgb(SAND))
    draw = ImageDraw.Draw(bg)

    # Header ribbon
    header_h = int(H * 0.16)
    draw.rectangle([0, 0, W, header_h], fill=_hex_to_rgb(TEAL))

    # Footer line
    draw.line([(int(W*0.1), int(H*0.86)), (int(W*0.9), int(H*0.86))], fill=_hex_to_rgb(TEAL), width=3)

    # Fonts (fallback to default if DejaVu not available)
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=int(W*0.06))
        name_font  = ImageFont.truetype("DejaVuSans-Bold.ttf", size=int(W*0.08))
        label_font = ImageFont.truetype("DejaVuSans.ttf",      size=int(W*0.028))
        body_font  = ImageFont.truetype("DejaVuSans.ttf",      size=int(W*0.035))
        emoji_font = ImageFont.truetype("DejaVuSans.ttf",      size=int(header_h*0.28*1.2))
    except:
        title_font = name_font = label_font = body_font = emoji_font = ImageFont.load_default()

    # Small helper to center text horizontally
    def center_text(y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        x = (W - w) // 2
        draw.text((x, y), text, font=font, fill=fill)

    # Logo glyph: sage circle + 🧠
    circle_r = int(header_h * 0.28)
    cx0 = int(W * 0.1); cy0 = int(header_h / 2 - circle_r)
    draw.ellipse((cx0, cy0, cx0 + circle_r*2, cy0 + circle_r*2), fill=_hex_to_rgb(SAGE))
    eb = draw.textbbox((0, 0), "🧠", font=emoji_font)
    draw.text((cx0 + circle_r - (eb[2]-eb[0])//2, cy0 + circle_r - (eb[3]-eb[1])//2),
              "🧠", font=emoji_font, fill=(0, 0, 0))

    # Brand text
    draw.text((cx0 + circle_r*2 + 24, int(header_h*0.30)), "Neuro Niche", font=title_font, fill=(255, 255, 255))
    draw.text((cx0 + circle_r*2 + 24, int(header_h*0.62)), "Certificate of Completion", font=body_font, fill=(255, 255, 255))

    # Body text
    y = int(header_h + H*0.08)
    center_text(y, "Congratulations", title_font, _hex_to_rgb(INK)); y += int(H*0.06)
    learner = (st.session_state.name or "Learner").strip()
    center_text(y, learner, name_font, _hex_to_rgb(INK)); y += int(H*0.07)
    center_text(y, "has successfully completed", body_font, _hex_to_rgb(INK)); y += int(H*0.05)
    center_text(y, "Neuro-diversity in Schools — Fundamentals", body_font, _hex_to_rgb(INK)); y += int(H*0.05)
    center_text(y, f"Score: {score}/5", body_font, _hex_to_rgb(INK)); y += int(H*0.07)
    date_str = datetime.utcnow().strftime("%b %d, %Y (UTC)")
    draw.text((int(W*0.15), int(H*0.82)), f"Date: {date_str}", font=label_font, fill=_hex_to_rgb(INK))
    draw.text((int(W*0.60), int(H*0.82)), "Authorized by: Neuro Niche", font=label_font, fill=_hex_to_rgb(INK))

    # Return bytes + save copy
    buf = io.BytesIO(); bg.save(buf, format="PNG"); buf.seek(0)
    fname = f"neuro_niche_certificate_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
    with open(os.path.join(CERT_DIR, fname), "wb") as f:
        f.write(buf.getbuffer())
    buf.seek(0)
    return buf, fname

# ----------------------------
# Slides
# ----------------------------
def slide_intro():
    st.title("🧠 Neurodiversity in Schools — Fundamentals")
    st.write("A short, interactive lesson for educators (~5 minutes). Please enter your details to begin.")

    with st.form("start_form", clear_on_submit=False):
        name  = st.text_input("Your full name", value=st.session_state.name)
        email = st.text_input("Your email address", value=st.session_state.email)
        submitted = st.form_submit_button("Start lesson")

    st.session_state.name = name
    st.session_state.email = email

    if submitted:
        if name and email:
            st.session_state.started = True
            st.session_state.step = 1   # go to first slide explicitly
            st.success("Welcome! Let’s begin.")
        else:
            st.warning("Please enter your name and email before starting.")

def slide_1():
    st.header("1) What does neurodiversity mean?")
    st.write("Select the best definition.")
    choice = st.radio(
        "Neurodiversity refers to…",
        [
            "A medical disorder affecting a small number of people.",
            "The natural variation in human brains and minds across the population.",
            "A trend on social media about productivity hacks."
        ],
        index=0 if "s1" not in st.session_state.answers else
              [0,1,2][["A medical disorder affecting a small number of people.",
                       "The natural variation in human brains and minds across the population.",
                       "A trend on social media about productivity hacks."].index(st.session_state.answers["s1"])]
        if st.session_state.answers.get("s1") in [
            "A medical disorder affecting a small number of people.",
            "The natural variation in human brains and minds across the population.",
            "A trend on social media about productivity hacks."
        ] else 0
    )
    st.session_state.answers["s1"] = choice
    st.button("Next", on_click=lambda: st.session_state.update(step=2))

def slide_2():
    st.header("2) What neurodiversity is **not**")
    st.write("Choose the statements that are **incorrect** / stereotype-based.")
    opts = [
        "All neurodivergent students have the same needs.",
        "With the right supports and environment, many students can thrive.",
        "Neurodiversity is caused by bad parenting.",
        "You can 'see' neurodiversity just by looking at someone."
    ]
    default = st.session_state.answers.get("s2", [])
    selected = st.multiselect("Incorrect statements:", opts, default=default)
    st.session_state.answers["s2"] = selected
    st.button("Next", on_click=lambda: st.session_state.update(step=3))

def slide_3():
    st.header("3) What does neuro-inclusive mean?")
    st.write("Pick the best description.")
    opts = [
        "Expect conformity to one 'normal' way of thinking and behaving.",
        "Design environments, teaching, and supports so different learners can succeed.",
        "Exclude students unless they have a formal diagnosis."
    ]
    current = st.session_state.answers.get("s3")
    idx = opts.index(current) if current in opts else 0
    choice = st.selectbox("Neuro-inclusive schools…", opts, index=idx)
    st.session_state.answers["s3"] = choice
    st.button("Next", on_click=lambda: st.session_state.update(step=4))

def slide_4():
    st.header("4) How can schools be more inclusive?")
    st.write("Pick up to three actions you could take this term.")
    actions = [
        "Adopt Universal Design for Learning (multiple ways to engage/express).",
        "Improve sensory supports (quiet spaces, lighting, movement breaks).",
        "Use strengths-based IEP goals and flexible assessment options.",
        "Apply zero-tolerance discipline for all regulation difficulties."
    ]
    selected = st.multiselect(
        "Select actions:", actions,
        default=st.session_state.answers.get("s4", []), max_selections=3
    )
    st.session_state.answers["s4"] = selected
    st.button("Take Quiz", on_click=lambda: st.session_state.update(step=5))

def slide_5_quiz():
    st.header("5) Quick Check — 3 questions")
    q1 = st.radio("Q1: Which is closest to the definition of neurodiversity?",
                  ["A disorder category", "Human brain/mind diversity", "A new curriculum"],
                  index={"Human brain/mind diversity":1}.get(st.session_state.answers.get("q1"), 0))
    st.session_state.answers["q1"] = q1

    q2 = st.radio("Q2: Which statement is a **stereotype**?",
                  ["All neurodivergent students are the same",
                   "Environments influence participation",
                   "Strengths-based approaches help"],
                  index={"All neurodivergent students are the same":0}.get(st.session_state.answers.get("q2"), 0))
    st.session_state.answers["q2"] = q2

    q3 = st.radio("Q3: A **neuro-inclusive** classroom does what?",
                  ["Forces one standard of 'normal'",
                   "Designs for variability and offers choices",
                   "Excludes until diagnosis is provided"],
                  index={"Designs for variability and offers choices":1}.get(st.session_state.answers.get("q3"), 0))
    st.session_state.answers["q3"] = q3

    st.button("Finish & See Score", on_click=finish)

# ----------------------------
# Finish + share
# ----------------------------
def finish():
    score = 0
    if st.session_state.answers.get("s1") == "The natural variation in human brains and minds across the population.":
        score += 1

    wrong = {
        "All neurodivergent students have the same needs.",
        "Neurodiversity is caused by bad parenting.",
        "You can 'see' neurodiversity just by looking at someone."
    }
    s2 = set(st.session_state.answers.get("s2", []))
    if wrong.issubset(s2) and len(s2) == len(wrong):
        score += 1

    if st.session_state.answers.get("s3") == "Design environments, teaching, and supports so different learners can succeed.":
        score += 1

    if st.session_state.answers.get("q1") == "Human brain/mind diversity":
        score += 1
    if st.session_state.answers.get("q3") == "Designs for variability and offers choices":
        score += 1

    st.session_state.score = score
    st.session_state.finished = True
    save_completion(st.session_state.name, st.session_state.email, score)
    st.session_state.step = 6  # move to score screen

def score_view():
    st.success(f"Your score: {st.session_state.score} / 5")
    st.progress(st.session_state.score / 5.0)

    cert_bytes, cert_name = generate_certificate_bytes(st.session_state.name, st.session_state.score)
    st.download_button("Download your certificate (PNG)", data=cert_bytes, file_name=cert_name, type="primary")
    st.image(cert_bytes, caption="Shareable certificate")

    st.divider()
    st.subheader("Share your achievement")
    app_url = st.text_input("Public app URL (for the share preview):", value="https://your-streamlit-app-url/")
    share_text = ("I just completed the Neuro-diversity in Schools – Fundamentals lesson "
                  "and earned my certificate. #NeuroInclusive #UDL")
    st.code(share_text, language=None)
    li_url = "https://www.linkedin.com/sharing/share-offsite/?url=" + urllib.parse.quote(app_url, safe="")
    st.link_button("Share on LinkedIn", li_url)

    if st.button("Restart lesson"):
        for k in ["step", "started", "answers", "score", "finished"]:
            st.session_state.pop(k, None)
        st.rerun()

# ----------------------------
# Router
# ----------------------------
if not st.session_state.started and st.session_state.step == 0:
    slide_intro()
elif st.session_state.finished or st.session_state.step == 6:
    score_view()
else:
    {1: slide_1, 2: slide_2, 3: slide_3, 4: slide_4, 5: slide_5_quiz}.get(st.session_state.step, slide_intro)()

# ----------------------------
# Admin panel
# ----------------------------
with st.expander("Admin: view completions log"):
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        st.dataframe(df, use_container_width=True)
        st.download_button("Download CSV", data=df.to_csv(index=False), file_name="completions.csv", mime="text/csv")
    else:
        st.caption("No completions yet.")

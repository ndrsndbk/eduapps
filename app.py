import streamlit as st
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io, os, urllib.parse

# ----------------------
# Brand (inline CSS; no .streamlit needed)
# ----------------------
SAGE = "#DDE6D5"
TEAL = "#2E7D7C"
SAND = "#F3EEE6"
INK  = "#0F172A"

st.set_page_config(page_title="Neuro‑diversity in Schools – Fundamentals", page_icon="🧠", layout="centered")

CSS = """
<style>
:root { --sage:%s; --teal:%s; --sand:%s; --ink:%s; }
div.block-container { padding-top:1.2rem; padding-bottom:2rem; }
.stButton>button { height:3rem; border-radius:0.75rem; }
</style>
""" % (SAGE, TEAL, SAND, INK)
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------
# Paths (create on the fly; works with only app.py present)
# ----------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
CERT_DIR = os.path.join(DATA_DIR, "certificates")
LOG_PATH = os.path.join(DATA_DIR, "completions.csv")
os.makedirs(CERT_DIR, exist_ok=True)

# ----------------------
# State
# ----------------------
def init_state():
    st.session_state.setdefault("step", 0)
    st.session_state.setdefault("answers", {})
    st.session_state.setdefault("name", "")
    st.session_state.setdefault("email", "")
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("finished", False)

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step = max(0, st.session_state.step - 1)

# ----------------------
# Persistence
# ----------------------
def save_completion(name, email, score):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = {"timestamp_utc": ts, "name": name, "email": email, "score": score}
    if os.path.exists(LOG_PATH):
        try:
            df = pd.read_csv(LOG_PATH)
        except Exception:
            df = pd.DataFrame(columns=["timestamp_utc","name","email","score"])
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(LOG_PATH, index=False)

# ----------------------
# Certificate (drawn via Pillow; no external assets)
# ----------------------
def _hex_to_rgb(hx): hx = hx.lstrip("#"); return tuple(int(hx[i:i+2],16) for i in (0,2,4))

def generate_certificate_bytes(name, score):
    """Return PNG bytes AND also save a copy under data/certificates/."""
    W, H = (1654, 2339)  # A4 ~150dpi
    bg = Image.new("RGB", (W, H), _hex_to_rgb(SAND))
    draw = ImageDraw.Draw(bg)

    # Header ribbon
    header_h = int(H * 0.16)
    draw.rectangle([0, 0, W, header_h], fill=_hex_to_rgb(TEAL))

    # Footer line
    draw.line([(int(W*0.1), int(H*0.86)), (int(W*0.9), int(H*0.86))], fill=_hex_to_rgb(TEAL), width=3)

    # Fonts
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=int(W*0.06))
        name_font  = ImageFont.truetype("DejaVuSans-Bold.ttf", size=int(W*0.08))
        label_font = ImageFont.truetype("DejaVuSans.ttf",      size=int(W*0.028))
        body_font  = ImageFont.truetype("DejaVuSans.ttf",      size=int(W*0.035))
    except:
        title_font = name_font = label_font = body_font = ImageFont.load_default()

    def center_text(y, text, font, fill):
        bbox = draw.textbbox((0,0), text, font=font)
        w = bbox[2]-bbox[0]
        x = (W - w)//2
        draw.text((x,y), text, font=font, fill=fill)

    # Logo glyph (placeholder): sage circle + brain emoji
    circle_r = int(header_h*0.28)
    cx0 = int(W*0.1); cy0 = int(header_h/2 - circle_r)
    draw.ellipse((cx0, cy0, cx0+circle_r*2, cy0+circle_r*2), fill=_hex_to_rgb(SAGE))
    try:
        emoji_font = ImageFont.truetype("DejaVuSans.ttf", size=int(circle_r*1.2))
    except:
        emoji_font = ImageFont.load_default()
    eb = draw.textbbox((0,0), "🧠", font=emoji_font)
    draw.text((cx0+circle_r-(eb[2]-eb[0])//2, cy0+circle_r-(eb[3]-eb[1])//2), "🧠", font=emoji_font, fill=(0,0,0))

    # Brand text
    draw.text((cx0 + circle_r*2 + 24, int(header_h*0.30)), "Neuro Niche", font=title_font, fill=(255,255,255))
    draw.text((cx0 + circle_r*2 + 24, int(header_h*0.62)), "Certificate of Completion", font=body_font, fill=(255,255,255))

    # Body
    y = int(header_h + H*0.08)
    center_text(y, "Congratulations", title_font, _hex_to_rgb(INK)); y += int(H*0.06)
    learner = (name or "Learner").strip()
    center_text(y, learner, name_font, _hex_to_rgb(INK)); y += int(H*0.07)
    center_text(y, "has successfully completed", body_font, _hex_to_rgb(INK)); y += int(H*0.05)
    center_text(y, "Neuro‑diversity in Schools — Fundamentals", body_font, _hex_to_rgb(INK)); y += int(H*0.05)
    center_text(y, f"Score: {score}/5", body_font, _hex_to_rgb(INK)); y += int(H*0.07)

    date_str = datetime.utcnow().strftime("%b %d, %Y (UTC)")
    draw.text((int(W*0.15), int(H*0.82)), f"Date: {date_str}", font=label_font, fill=_hex_to_rgb(INK))
    draw.text((int(W*0.60), int(H*0.82)), "Authorized by: Neuro Niche", font=label_font, fill=_hex_to_rgb(INK))

    # Save to memory
    buf = io.BytesIO()
    bg.save(buf, format="PNG")
    buf.seek(0)

    # Also persist to data/certificates
    fname = f"neuro_niche_certificate_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
    with open(os.path.join(CERT_DIR, fname), "wb") as f:
        f.write(buf.getbuffer())

    buf.seek(0)
    return buf, fname

# ----------------------
# Slides
# ----------------------
def intro_slide():
    st.markdown("### Neuro‑diversity in Schools — Fundamentals")
    st.write("A short, interactive lesson for educators. ~5 minutes.")
    st.markdown("**Enter your details to begin:**")

    st.session_state.name = st.text_input("Your name", value=st.session_state.name, placeholder="e.g., Sam Teacher")
    st.session_state.email = st.text_input("Email (for your certificate & log)", value=st.session_state.email, placeholder="you@school.org")

    col1, col2 = st.columns(2)
    with col1:
        st.button("Start", on_click=next_step, disabled=not (st.session_state.name and st.session_state.email))
    with col2:
        st.caption("We’ll log completion time and score for your school records.")

def slide_1():
    st.markdown("#### 1) What does **neurodiversity** mean?")
    st.write("Select the best definition.")
    default_idx = 1 if st.session_state.answers.get('s1') == "The natural variation in human brains and minds across the population." else 0
    choice = st.radio(
        "Neurodiversity refers to…",
        [
            "A medical disorder affecting a small number of people.",
            "The natural variation in human brains and minds across the population.",
            "A trend on social media about productivity hacks."
        ], index=default_idx
    )
    st.session_state.answers['s1'] = choice
    nav()

def slide_2():
    st.markdown("#### 2) What **neurodiversity is not** (stigma & stereotypes)")
    st.write("Pick the statements that are **incorrect** and based on stereotypes.")
    opts = [
        "All neurodivergent students have the same needs.",
        "With the right supports and environment, many students can thrive.",
        "Neurodiversity is caused by bad parenting.",
        "You can 'see' neurodiversity just by looking at someone."
    ]
    selected = st.multiselect("Incorrect statements:", opts, default=st.session_state.answers.get('s2', []))
    st.session_state.answers['s2'] = selected
    nav()

def slide_3():
    st.markdown("#### 3) What does **neuro‑inclusive** mean?")
    st.write("Choose the best description.")
    default_idx = 1 if st.session_state.answers.get('s3') == "Design environments, teaching, and supports so different learners can succeed." else 0
    choice = st.selectbox(
        "Neuro‑inclusive schools…",
        [
            "Expect conformity to one 'normal' way of thinking and behaving.",
            "Design environments, teaching, and supports so different learners can succeed.",
            "Exclude students unless they have a formal diagnosis."
        ],
        index=default_idx
    )
    st.session_state.answers['s3'] = choice
    nav()

def slide_4():
    st.markdown("#### 4) How can schools be **more inclusive**?")
    st.write("Pick up to three actions you could take this term.")
    actions = [
        "Adopt Universal Design for Learning (multiple ways to engage/express).",
        "Improve sensory supports (quiet spaces, lighting, movement breaks).",
        "Use strengths‑based IEP goals and flexible assessment options.",
        "Apply zero‑tolerance discipline for all regulation difficulties."
    ]
    selected = st.multiselect("Select actions:", actions, default=st.session_state.answers.get('s4', []), max_selections=3)
    st.session_state.answers['s4'] = selected
    nav()

def slide_5_quiz():
    st.markdown("#### 5) Quick Check — 3 questions")
    idx1 = 1 if st.session_state.answers.get('q1') == "Human brain/mind diversity" else 0
    q1 = st.radio("Q1: Which is closest to the definition of neurodiversity?",
                  ["A disorder category", "Human brain/mind diversity", "A new curriculum"], index=idx1)
    st.session_state.answers['q1'] = q1

    idx2 = 0 if st.session_state.answers.get('q2') == "All neurodivergent students are the same" else 0
    q2 = st.radio("Q2: Which statement is a **stereotype**?",
                  ["All neurodivergent students are the same",
                   "Environments influence participation",
                   "Strengths‑based approaches help"], index=idx2)
    st.session_state.answers['q2'] = q2

    idx3 = 1 if st.session_state.answers.get('q3') == "Designs for variability and offers choices" else 0
    q3 = st.radio("Q3: A **neuro‑inclusive** classroom does what?",
                  ["Forces one standard of 'normal'",
                   "Designs for variability and offers choices",
                   "Excludes until diagnosis is provided"], index=idx3)
    st.session_state.answers['q3'] = q3

    st.button("Finish & See Score", on_click=finish, use_container_width=True)

# ----------------------
# Finish / Share
# ----------------------
def finish():
    score = 0
    if st.session_state.answers.get('s1') == "The natural variation in human brains and minds across the population.":
        score += 1

    wrong_stereos = {
        "All neurodivergent students have the same needs.",
        "Neurodiversity is caused by bad parenting.",
        "You can 'see' neurodiversity just by looking at someone."
    }
    s2 = set(st.session_state.answers.get('s2', []))
    if wrong_stereos.issubset(s2) and len(s2) == len(wrong_stereos):
        score += 1

    if st.session_state.answers.get('s3') == "Design environments, teaching, and supports so different learners can succeed.":
        score += 1

    if st.session_state.answers.get('q1') == "Human brain/mind diversity":
        score += 1
    if st.session_state.answers.get('q3') == "Designs for variability and offers choices":
        score += 1

    st.session_state.score = score
    st.session_state.finished = True
    save_completion(st.session_state.name, st.session_state.email, score)

def score_view():
    st.success(f"Your score: {st.session_state.score} / 5")
    st.progress(st.session_state.score/5.0)

    # Certificate (in-memory download + saved copy)
    cert_bytes, cert_name = generate_certificate_bytes(st.session_state.name, st.session_state.score)
    st.download_button("Download your certificate (PNG)", data=cert_bytes, file_name=cert_name, type="primary")
    st.image(cert_bytes, caption="Shareable certificate")

    # Share
    st.divider()
    st.markdown("##### Share your achievement")
    app_url = st.text_input("Public app URL (for sharing preview):", value="https://your-streamlit-app-url/")
    share_text = "I just completed the Neuro‑diversity in Schools – Fundamentals lesson and earned my certificate. #NeuroInclusive #UDL"
    st.write("Post text (copy/paste into LinkedIn):")
    st.code(share_text, language=None)
    li_url = "https://www.linkedin.com/sharing/share-offsite/?url=" + urllib.parse.quote(app_url, safe="")
    st.link_button("Share on LinkedIn", li_url)

    st.button("Restart", on_click=restart)

def restart():
    for k in ["step","answers","score","finished"]:
        st.session_state.pop(k, None)
    init_state()

def nav():
    col1, col2 = st.columns(2)
    with col1:
        st.button("Back", on_click=prev_step, use_container_width=True)
    with col2:
        st.button("Next", on_click=next_step, use_container_width=True)

# ----------------------
# Run
# ----------------------
init_state()
steps = [intro_slide, slide_1, slide_2, slide_3, slide_4, slide_5_quiz]
if not st.session_state.finished:
    steps[min(st.session_state.step, len(steps)-1)]()
else:
    score_view()

with st.expander("Admin: view completions log"):
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        st.dataframe(df, use_container_width=True)
    else:
        st.caption("No completions yet.")

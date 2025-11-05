import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Neuro Niche – Fundamentals Lesson", page_icon="🧠")

# --- Simple, brand-friendly styling ---
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #F3EEE6 !important;
}
.stButton > button {
    border-radius: 0.75rem !important;
    height: 2.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- Helper: Certificate generator ---
def generate_certificate(name, score):
    img = Image.new("RGB", (900, 600), color=(243, 238, 230))
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.load_default()
    heading = "Neuro Niche"
    draw.text((350, 80), heading, fill=(46, 125, 124), font=title_font)
    draw.text((230, 200), f"Congratulations, {name}!", fill=(15, 23, 42), font=title_font)
    draw.text((180, 250), f"You have completed the Neurodiversity in Schools Fundamentals Lesson.", fill=(15, 23, 42), font=title_font)
    draw.text((180, 300), f"Your score: {score}/5", fill=(15, 23, 42), font=title_font)
    draw.text((320, 480), f"© {datetime.now().year} Neuro Niche", fill=(100, 100, 100), font=title_font)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --- UI ---
st.title("🧠 Neurodiversity in Schools – Fundamentals")
st.write("An interactive mini-lesson introducing neurodiversity, inclusion, and affirming education.")

name = st.text_input("Your full name")
email = st.text_input("Your email address")

if name and email:
    st.success("Welcome! Click below to begin your lesson.")
else:
    st.warning("Please enter your name and email before starting.")

if "step" not in st.session_state:
    st.session_state.step = 0

if name and email:
    if st.button("Start Lesson") or st.session_state.step > 0:
        st.session_state.step += 1

# --- Lesson slides ---
def slide_1():
    st.header("1) What does neurodiversity mean?")
    st.write("Select the best definition.")
    return st.radio(
        "Neurodiversity refers to…",
        ["A medical disorder affecting a small number of people.",
         "The natural variation in human brains and minds across the population.",
         "A trend on social media about productivity hacks."]
    )

def slide_2():
    st.header("2) What neurodiversity does *not* mean")
    st.write("Neurodiversity is not synonymous with disorder or deficit—it includes the full spectrum of human thinking styles.")
    st.write("Common misconceptions include:")
    st.markdown("- Only autistic people are neurodivergent  \n- Neurodiversity means the same as disability  \n- Neurodiversity is a recent social trend")

def slide_3():
    st.header("3) What does neuro-inclusive mean?")
    st.write("A neuro-inclusive school recognizes and values different thinking and learning styles. It provides flexibility, predictability, and genuine belonging for all learners.")

def slide_4():
    st.header("4) How can schools be more inclusive?")
    st.markdown("""
    **Examples include:**
    - Flexible seating and sensory-safe spaces  
    - Clear visual schedules and expectations  
    - Collaborative goal-setting with students  
    - Supporting autonomy and communication differences
    """)

def slide_5_quiz():
    st.header("5) Quick Check")
    st.write("Choose the correct answers:")
    q1 = st.radio("Neurodiversity recognizes…", ["Deficits in the brain.", "Natural variation in minds.", "A medical diagnosis."])
    q2 = st.radio("Being neuro-inclusive means…", ["Ignoring differences.", "Valuing diverse ways of thinking.", "Using one-size-fits-all strategies."])
    return [q1, q2]

# --- Navigation ---
if st.session_state.step == 1:
    ans = slide_1()
    st.session_state.ans1 = ans
    st.button("Next", on_click=lambda: setattr(st.session_state, "step", 2))

elif st.session_state.step == 2:
    slide_2()
    st.button("Next", on_click=lambda: setattr(st.session_state, "step", 3))

elif st.session_state.step == 3:
    slide_3()
    st.button("Next", on_click=lambda: setattr(st.session_state, "step", 4))

elif st.session_state.step == 4:
    slide_4()
    st.button("Take Quiz", on_click=lambda: setattr(st.session_state, "step", 5))

elif st.session_state.step == 5:
    quiz = slide_5_quiz()
    if st.button("Submit Quiz"):
        score = 0
        if st.session_state.get("ans1") == "The natural variation in human brains and minds across the population.": score += 1
        if quiz[0] == "Natural variation in minds.": score += 1
        if quiz[1] == "Valuing diverse ways of thinking.": score += 1

        cert = generate_certificate(name, score)
        st.success(f"You scored {score}/5! 🎉")
        st.download_button("Download your certificate", data=cert, file_name=f"{name}_certificate.png", mime="image/png")

        linkedin_text = f"I just completed the Neurodiversity in Schools Fundamentals Lesson with Neuro Niche! #Neurodiversity #InclusiveEducation"
        share_url = f"https://www.linkedin.com/sharing/share-offsite/?url=https://neuronicheapps-edu.streamlit.app/&summary={linkedin_text}"
        st.markdown(f"[Share on LinkedIn]({share_url})")

# --- Admin log view ---
with st.expander("Admin: view completions log"):
    st.write("Log entries will appear here once integrated with backend or CSV logging.")

import os
import time
import streamlit as st
from groq import Groq

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Email Generator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# API KEY HANDLING (never hard-coded, never shown in UI)
# Priority: Streamlit secrets (used on Streamlit Cloud) -> environment variable
# (used in Colab / local, set via os.environ, e.g. from a Colab "Secrets" tab)
# ----------------------------------------------------------------------------
def get_api_key() -> str:
    key = ""
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""
    if not key:
        key = os.environ.get("GROQ_API_KEY", "")
    return key


GROQ_API_KEY = get_api_key()

# ----------------------------------------------------------------------------
# STYLING
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .stApp {
            background: radial-gradient(circle at top left, #1f1147 0%, #0d0821 45%, #05030f 100%);
            color: #f2f0fa;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #150a33 0%, #0b0620 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        .hero {
            text-align: center;
            padding: 1.4rem 1rem 1.8rem 1rem;
        }
        .hero h1 {
            font-size: 2.6rem;
            font-weight: 800;
            background: linear-gradient(90deg, #a78bfa, #f472b6, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        .hero p {
            color: #b6b0d4;
            font-size: 1.05rem;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 18px;
            padding: 1.6rem 1.6rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        }

        .email-output {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(167, 139, 250, 0.4);
            border-radius: 16px;
            padding: 1.8rem;
            white-space: pre-wrap;
            font-family: 'Georgia', serif;
            font-size: 1.02rem;
            line-height: 1.65;
            color: #f5f3ff;
            animation: fadeIn 0.6s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        div.stButton > button {
            background: linear-gradient(90deg, #7c3aed, #db2777);
            color: white;
            font-weight: 700;
            border: none;
            border-radius: 12px;
            padding: 0.7rem 1.4rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            width: 100%;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(124, 58, 237, 0.45);
        }

        .badge {
            display: inline-block;
            background: rgba(124, 58, 237, 0.18);
            border: 1px solid rgba(124, 58, 237, 0.5);
            color: #c4b5fd;
            padding: 0.15rem 0.7rem;
            border-radius: 999px;
            font-size: 0.78rem;
            margin-right: 0.4rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>AI Email Generator</h1>
        <p>Turn a topic and a few bullet points into a polished, ready-to-send email — powered by Groq.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not GROQ_API_KEY:
    st.error(
        "No Groq API key found. Add `GROQ_API_KEY` to your Streamlit secrets "
        "(Settings → Secrets on Streamlit Cloud) or set it as an environment "
        "variable before running. The key is never read from or shown in the UI."
    )

# ----------------------------------------------------------------------------
# SIDEBAR — SETTINGS
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Email Settings")

    tone = st.selectbox(
        "Tone",
        [
            "Professional", "Friendly", "Persuasive", "Formal",
            "Casual", "Apologetic", "Enthusiastic", "Urgent",
            "Empathetic", "Confident",
        ],
        index=0,
    )

    email_type = st.selectbox(
        "Email type",
        [
            "General", "Sales/Outreach", "Follow-up", "Apology",
            "Thank you", "Meeting request", "Announcement",
            "Complaint / Escalation", "Job application / Cover letter",
            "Networking",
        ],
        index=0,
    )

    length = st.select_slider(
        "Length", options=["Short", "Medium", "Long"], value="Medium"
    )

    st.markdown("---")
    st.markdown("### Optional details")
    sender_name = st.text_input("Your name (signature)", "")
    recipient_name = st.text_input("Recipient's name", "")
    subject_hint = st.text_input("Preferred subject line (optional)", "")

    st.markdown("---")
    model = st.selectbox(
        "Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-120b"],
        index=0,
        help="Larger models generally write higher-quality, more nuanced emails.",
    )
    temperature = st.slider("Creativity", 0.0, 1.2, 0.7, 0.1)

# ----------------------------------------------------------------------------
# MAIN INPUT AREA
# ----------------------------------------------------------------------------
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### What is this email about?")
    topic = st.text_input(
        "Topic",
        placeholder="e.g. Requesting a deadline extension for the Q3 report",
    )

    st.markdown("#### Key points to include")
    points = st.text_area(
        "Our points (one per line)",
        placeholder=(
            "e.g.\n"
            "- The client data arrived 3 days later than planned\n"
            "- We need 5 extra business days\n"
            "- Quality will not be affected"
        ),
        height=180,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    generate = st.button("Generate Email", use_container_width=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### Generated Email")
    output_placeholder = st.empty()
    output_placeholder.markdown(
        "<div class='email-output' style='opacity:0.5;'>"
        "Your generated email will appear here...</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# PROMPT ENGINEERING — for high quality output
# ----------------------------------------------------------------------------
def build_prompt():
    bullet_points = "\n".join(
        f"- {line.strip()}" for line in points.splitlines() if line.strip()
    )
    length_guide = {
        "Short": "under 100 words, 2-3 short paragraphs max",
        "Medium": "roughly 120-200 words, well-structured",
        "Long": "roughly 220-320 words, thorough but not padded",
    }[length]

    signature = sender_name.strip() if sender_name.strip() else "[Your Name]"
    greeting_name = recipient_name.strip() if recipient_name.strip() else "there"

    subject_instruction = (
        f'Use this exact subject line: "{subject_hint.strip()}"'
        if subject_hint.strip()
        else "Write a compelling, specific subject line (not generic)."
    )

    return f"""You are an elite professional email copywriter. Write a high-quality,
human-sounding email based on the details below. The email must read as if a
thoughtful, articulate person wrote it — never generic, robotic, or filled with
clichés like "I hope this email finds you well" or "In today's fast-paced world".

EMAIL TYPE: {email_type}
TONE: {tone}
TARGET LENGTH: {length_guide}
RECIPIENT NAME: {greeting_name}
SENDER SIGNATURE NAME: {signature}

TOPIC:
{topic.strip()}

KEY POINTS TO NATURALLY WEAVE IN (do not just list them, integrate them fluidly):
{bullet_points if bullet_points else "(none provided — infer sensible content from the topic)"}

REQUIREMENTS:
1. {subject_instruction}
2. Open with a natural, non-cliché greeting appropriate to the tone.
3. The body must have a clear purpose, logical flow, and a strong opening line
   that immediately signals why the reader should care.
4. Every key point above must be reflected in the email, in your own words,
   integrated smoothly — not copy-pasted verbatim.
5. Match the requested tone precisely and consistently throughout.
6. End with a clear, specific call to action or next step (when relevant to
   the email type), followed by an appropriate sign-off and the sender name.
7. Use proper email formatting with short paragraphs and good whitespace —
   no walls of text.
8. Do not use placeholder brackets except for the sender/recipient names
   already given. Do not add meta-commentary, notes, or explanations.
9. Output ONLY the email itself, starting with "Subject: ..." on the first
   line, followed by a blank line, then the email body. Nothing else.
"""


# ----------------------------------------------------------------------------
# GENERATION
# ----------------------------------------------------------------------------
if generate:
    if not GROQ_API_KEY:
        st.error("Cannot generate, no Groq API key configured.")
    elif not topic.strip():
        st.warning("Please enter a topic for the email.")
    else:
        with st.spinner("Crafting your email..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                prompt = build_prompt()

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a world-class professional email writer "
                                "known for clear, persuasive, and natural-sounding "
                                "emails. You never sound like a generic AI."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=900,
                )

                email_text = response.choices[0].message.content.strip()

                output_placeholder.markdown(
                    f"<div class='email-output'>{email_text}</div>",
                    unsafe_allow_html=True,
                )

                st.session_state["last_email"] = email_text
                st.success("Email generated!")

            except Exception as e:
                st.error(f"Something went wrong while generating the email: {e}")

# ----------------------------------------------------------------------------
# DOWNLOAD / COPY
# ----------------------------------------------------------------------------
if "last_email" in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    dcol1, dcol2, dcol3 = st.columns([1, 1, 2])
    with dcol1:
        st.download_button(
            "Download as .txt",
            data=st.session_state["last_email"],
            file_name=f"email_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dcol2:
        st.code(st.session_state["last_email"], language=None)
st.markdown(
    """
    
    """,
    unsafe_allow_html=True,
)


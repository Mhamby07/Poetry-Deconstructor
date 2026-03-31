import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="AP Lit Poetry Workshop", page_icon="🏛️", layout="wide")
genai.configure(api_key=st.secrets["API_KEY"])

# --- 2. SIDEBAR: AP EXAM FOCUS & LITERARY DEVICES ---
with st.sidebar:
    st.title("🏛️ AP FRQ 1: Poetry")
    
    st.subheader("1. Select Workshop Mode")
    ap_mode = st.selectbox(
        "Workshop Mode:",
        [
            "Line-by-Line Explication",
            "Row A: Thesis Workshop",
            "Row B: Evidence & Commentary",
            "Row C: Complexity & Shifts"
        ]
    )
    
    st.markdown("---")
    st.subheader("2. Literary Device Focus")
    st.write("Target a specific element to see how it builds meaning.")
    device_focus = st.selectbox(
        "Select a Device:",
        [
            "Open Analysis (All Devices)",
            "Imagery & Sensory Details",
            "Metaphor, Simile & Conceit",
            "Enjambment & Syntax",
            "Tone & Diction",
            "Structure & Form (Volta, Meter)",
            "Metonymy & Synecdoche"
        ]
    )
    
    st.markdown("---")
    with st.expander("📝 AP Rubric Reminders"):
        st.write("**Row A (1 pt):** Must establish a defensible thesis analyzing how the poet uses literary elements to convey meaning.")
        st.write("**Row B (4 pts):** Must provide specific evidence and explain *how* that evidence conveys the meaning.")
        st.write("**Row C (1 pt):** Must demonstrate a complex understanding (e.g., exploring tensions, shifts, or broader contexts).")
        
    st.markdown("---")
    if st.button("Start Over / New Poem"):
        st.session_state.clear()
        st.rerun()

# --- 3. THE "PROFESSOR" SYSTEM PROMPT ---
ap_professor_prompt = f"""
You are a distinguished, veteran AP English Literature Exam Reader and a passionate literature professor. 
The student has selected the workshop mode: '{ap_mode}' and is focusing on the literary device: '{device_focus}'.

CRITICAL RULES:
1. NEVER do the work for the student. Do not write the thesis or give away the theme.
2. Focus heavily on '{device_focus}'. If they selected a specific device, guide them to locate an example of it in the poem.
3. THE GOLDEN RULE: Do not let the student just identify the device. You must aggressively push them to explain HOW the '{device_focus}' functions to create the Meaning of the Work as a Whole (MOWAW). 
4. Keep your responses concise (1-2 short paragraphs max) ending with a highly targeted analytical question.
"""

generation_config = genai.types.GenerationConfig(temperature=0.3)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=ap_professor_prompt,
    generation_config=generation_config
)

# --- 4. SESSION MANAGEMENT ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "poem_text" not in st.session_state:
    st.session_state.poem_text = ""
if "workshop_active" not in st.session_state:
    st.session_state.workshop_active = False

# Ensure chat session matches the selected mode AND device
if "current_mode" not in st.session_state or st.session_state.current_mode != ap_mode or "current_device" not in st.session_state or st.session_state.current_device != device_focus:
    st.session_state.current_mode = ap_mode
    st.session_state.current_device = device_focus
    if st.session_state.workshop_active:
        st.session_state.chat_session = model.start_chat(history=[])
        try:
            prompt = f"We are now shifting our focus to {ap_mode} with a specific lens on {device_focus}. Give me a brief welcoming thought about why analyzing {device_focus} is crucial for understanding this poem's deeper meaning, and ask your first specific question."
            response = st.session_state.chat_session.send_message(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception:
            pass

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- 5. UI: POEM INPUT SCREEN ---
if not st.session_state.workshop_active:
    st.title("🏛️ The AP Literature Poetry Workshop")
    st.write("Welcome, scholar. Paste your text below to begin our explication.")
    
    raw_poem = st.text_area("Paste the poem here:", height=300)
    
    if st.button("Begin Analysis"):
        if raw_poem.strip():
            st.session_state.poem_text = raw_poem
            st.session_state.workshop_active = True
            
            try:
                initial_prompt = f"Here is the poem we are analyzing:\n\n{raw_poem}\n\nPlease welcome the student. Focus on {device_focus} in the context of {ap_mode}. Ask a high-level AP question to begin."
                response = st.session_state.chat_session.send_message(initial_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.rerun() 
            except Exception:
                st.error("Error loading poem. Please try again.")
        else:
            st.warning("Please paste a poem first!")

# --- 6. UI: SPLIT-SCREEN WORKSHOP ---
if st.session_state.workshop_active:
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.subheader("📜 The Text")
        st.info(st.session_state.poem_text)
        
    with col2:
        st.subheader(f"🗣️ Discussion: {device_focus}")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_input = st.chat_input("Enter your analysis...")
        
        if user_input:
            st.chat_message("user").markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            try:
                response = st.session_state.chat_session.send_message(user_input)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                
            except ResourceExhausted:
                st.error("🚨 **Network Overload.** The College Board servers are busy. Please wait 60 seconds and try again.")
                if st.session_state.chat_history:
                    st.session_state.chat_history.pop()
                    
            except ValueError:
                st.error("🚨 **Content Filtered.** The AI's safety filters blocked this response. Try rephrasing your analysis.")
                if st.session_state.chat_history:
                    st.session_state.chat_history.pop()
                    
            except Exception as e:
                st.error("An unexpected error occurred. Please refresh the page and try again.")
                if st.session_state.chat_history:
                    st.session_state.chat_history.pop()

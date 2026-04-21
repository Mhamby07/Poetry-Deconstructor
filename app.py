import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import time
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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
            "Chunk Analysis (2-3 Lines)",
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

# --- 3. HELPER FUNCTIONS ---
def generate_ap_poetry_prompt(poem_title: str, poem_author: str, poem_text: str) -> str:
    """Generates an AP Literature Style Question 1 essay prompt based on a poem."""
    
    # Turn off safety filters so classic poems (death, war, etc.) don't get blocked
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    prompt_model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        generation_config=genai.types.GenerationConfig(temperature=0.4),
        safety_settings=safety_settings
    )
    
    ai_prompt = f"""
    You are an expert AP English Literature and Composition exam writer. 
    Read the following poem:
    
    Title: {poem_title}
    Author: {poem_author}
    Text: 
    {poem_text}
    
    Write a Question 1 (Poetry Analysis) Free Response Question essay prompt for this poem. 
    
    RULES:
    1. It must follow the strict formatting and rigor of official AP exams. 
    2. Use the standard formula: "Read the following poem carefully. Then, in a well-written essay, analyze how the poet uses literary elements and techniques to convey [insert the specific complex theme, relationship, or attitude found in the poem]."
    3. Do not provide any commentary, outlines, or answers. 
    4. Provide ONLY the text of the prompt itself.
    """
    
    try:
        response = prompt_model.generate_content(ai_prompt)
        return response.text
    except Exception as e:
        # Now we will actually see what the Google API is complaining about!
        return f"⚠️ API Error Details: {str(e)}"


# --- 4. THE "PROFESSOR" SYSTEM PROMPT ---
ap_professor_prompt = f"""
You are a distinguished, veteran AP English Literature Exam Reader and a passionate literature professor. 
The student has selected the workshop mode: '{ap_mode}' and is focusing on the literary device: '{device_focus}'.

CRITICAL RULES:
1. NEVER do the work for the student initially. Do not write the thesis or give away the theme right away.
2. Focus heavily on '{device_focus}'. If they selected a specific device, guide them to locate an example of it in the poem.
3. THE GOLDEN RULE: Do not let the student just identify the device. You must aggressively push them to explain HOW the '{device_focus}' functions to create the Meaning of the Work as a Whole (MOWAW). 
4. Keep your responses concise (1-2 short paragraphs max) ending with a highly targeted analytical question.
5. THE 4-ATTEMPT RULE: You must monitor the student's progress. If the student makes 4 unsuccessful, incorrect, or highly confused attempts to answer the SAME question or analyze the same section, you MUST stop questioning them. You will then provide the correct analysis/answer yourself, explain clearly how you arrived at that conclusion using the text, and then seamlessly ask a new question to move the workshop forward so they do not remain stuck.
"""

# Apply the same safety settings to the main chat model just in case!
chat_safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = genai.types.GenerationConfig(temperature=0.3)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=ap_professor_prompt,
    generation_config=generation_config,
    safety_settings=chat_safety_settings
)

# --- 5. SESSION MANAGEMENT ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "poem_text" not in st.session_state:
    st.session_state.poem_text = ""
if "poem_title" not in st.session_state:
    st.session_state.poem_title = ""
if "poem_author" not in st.session_state:
    st.session_state.poem_author = ""
if "generated_ap_prompt" not in st.session_state:
    st.session_state.generated_ap_prompt = ""
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

# --- 6. UI: POEM INPUT SCREEN ---
if not st.session_state.workshop_active:
    st.title("🏛️ The AP Literature Poetry Workshop")
    st.write("Welcome, scholar. Paste your text below to begin our explication.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        poem_title = st.text_input("Poem Title (Optional):")
    with col_b:
        poem_author = st.text_input("Poet (Optional):")
        
    raw_poem = st.text_area("Paste the poem here:", height=300)
    
    if st.button("Begin Analysis"):
        if raw_poem.strip():
            st.session_state.poem_title = poem_title.strip() if poem_title else "Untitled"
            st.session_state.poem_author = poem_author.strip() if poem_author else "Unknown"
            st.session_state.poem_text = raw_poem
            
            # GENERATE THE AP PROMPT AUTOMATICALLY BEFORE WORKSHOP STARTS
            with st.spinner("Analyzing poem themes and generating official AP FRQ prompt..."):
                generated_prompt = generate_ap_poetry_prompt(
                    poem_title=st.session_state.poem_title, 
                    poem_author=st.session_state.poem_author, 
                    poem_text=st.session_state.poem_text
                )
                st.session_state.generated_ap_prompt = generated_prompt
            
            st.session_state.workshop_active = True
            
            # ADD A SPEED BUMP HERE to prevent API traffic jams
            time.sleep(2)
            
            try:
                initial_prompt = f"Here is the poem we are analyzing:\n\n{raw_poem}\n\nPlease welcome the student. Focus on {device_focus} in the context of {ap_mode}. Ask a high-level AP question to begin."
                response = st.session_state.chat_session.send_message(initial_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.rerun() 
            except Exception:
                st.error("Error loading poem. Please try again.")
        else:
            st.warning("Please paste a poem first!")

# --- 7. UI: SPLIT-SCREEN WORKSHOP ---
if st.session_state.workshop_active:
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    # LEFT COLUMN: THE POEM & AP PROMPT
    with col1:
        # Display the auto-generated AP Prompt at the very top as the target goal
        st.subheader("🎯 Your Essay Prompt Goal")
        st.success(f"**Free Response Question 1: Poetry Analysis**\n\n{st.session_state.generated_ap_prompt}")
        st.markdown("---")
        
        st.subheader("📜 The Text")
        if st.session_state.poem_title != "Untitled" or st.session_state.poem_author != "Unknown":
            st.markdown(f"**{st.session_state.poem_title}** by {st.session_state.poem_author}")
            
        st.info(st.session_state.poem_text)
        
    # RIGHT COLUMN: THE CHAT
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

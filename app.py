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
            "Chunk Analysis (2-4 Lines)",
            "Logical Chunking (Stanzas/Thematic Units)",
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
    
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    prompt_model = genai.GenerativeModel(
        model_name='gemini-2.5-flash-lite', 
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
        return f"⚠️ API Error Details: {str(e)}"


# --- 4. THE "PROFESSOR" SYSTEM PROMPT ---
ap_professor_prompt = f
"""
You are a distinguished, veteran AP English Literature Exam Reader and a passionate literature professor. 
The student has selected the workshop mode: '{ap_mode}' and is focusing on the literary device: '{device_focus}'.

CRITICAL RULES:
1. NEVER do the work for the student initially. Do not write the thesis or give away the theme right away.
2. PACING & CHUNKING: Strictly adhere to the chosen '{ap_mode}'. 
   - If the mode is "Line-by-Line Explication", analyze exactly one line at a time.
   - If the mode is "Chunk Analysis (2-4 Lines)", group the text and analyze exactly 2 to 4 lines at a time.
   - If the mode is "Logical Chunking (Stanzas/Thematic Units)", group the text by complete stanzas, full syntactic sentences, or clear thematic shifts (usually 4 to 10 lines at a time).
3. Focus heavily on '{device_focus}'. If they selected a specific device, guide them to locate an example of it within the current section you are discussing.
4. THE GOLDEN RULE: Do not let the student just identify the device. You must aggressively push them to explain HOW the '{device_focus}' functions to create the Meaning of the Work as a Whole (MOWAW). 
5. Keep your responses concise (1-2 short paragraphs max) ending with a highly targeted analytical question about the specific chunk you are currently on.
6. THE 4-ATTEMPT RULE: You must monitor the student's progress. If the student makes 4 unsuccessful, incorrect, or highly confused attempts to answer the SAME question or analyze the same chunk, you MUST stop questioning them. You will then provide the correct analysis/answer yourself, explain clearly how you arrived at that conclusion using the text, and then seamlessly ask a new question about the NEXT logical section in the poem so they do not remain stuck.
"""

chat_safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="AP Lit Poetry Deconstructor", page_icon="✒️", layout="wide")
genai.configure(api_key=st.secrets["API_KEY"])

# --- 2. SIDEBAR UI (AP Focus Areas) ---
with st.sidebar:
    st.title("✒️ AP Analysis Panel")
    st.write("Select a specific AP Literature skill to focus on during your deconstruction.")
    
    focus_area = st.selectbox(
        "Analytical Focus:",
        [
            "General AP Analysis (All Elements)",
            "Structure, Form & Syntax (Volta, Enjambment, Meter)",
            "Figurative Language (Conceit, Metonymy, Synecdoche)",
            "Tone, Mood & Shifts",
            "Diction & Imagery"
        ]
    )
    
    st.markdown("---")
    st.subheader("AP Lit Golden Rule:")
    st.write("*Always connect the literary device to the meaning of the work as a whole.*")
    
    st.markdown("---")
    if st.button("Start Over / New Poem"):
        st.session_state.chat_history = []
        st.session_state.chat_session = None
        st.session_state.poem_loaded = False
        st.rerun()

# --- 3. MAIN LAYOUT & AI INITIALIZATION ---
st.title("✒️ The AP Lit Poetry Deconstructor")

# The rigorous AP Literature System Prompt
ap_system_prompt = f"""
You are an expert, rigorous AP English Literature teacher guiding a student through a poem.
The student has selected the following focus area: {focus_area}.

CRITICAL RULES:
1. Do NOT write the analysis for them. Do not give away the theme or write an essay.
2. Focus strictly on AP-level analysis. Use elevated terminology (e.g., volta, conceit, enjambment, metonymy, juxtaposition, syntax).
3. Quote ONE specific line or stanza, identify a device or structural element relevant to the {focus_area}, and ask a probing, Socratic question about its function and effect.
4. Push the student to connect the specific authorial choice to the "meaning of the work as a whole."
5. Validate their responses, gently correct superficial readings or misinterpretations, and push them deeper. Keep the tone academic, encouraging, and rigorous.
"""

generation_config = genai.types.GenerationConfig(
    temperature=0.3, # Slightly higher than 1984 to allow for poetic interpretation, but low enough to stay focused.
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=ap_system_prompt,
    generation_config=generation_config
)

# --- 4. SESSION MANAGEMENT ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "poem_loaded" not in st.session_state:
    st.session_state.poem_loaded = False
if "current_focus" not in st.session_state or st.session_state.current_focus != focus_area:
    # If they change the focus area, we need to restart the chat session to apply the new prompt
    st.session_state.current_focus = focus_area
    if st.session_state.poem_loaded:
        st.session_state.chat_session = model.start_chat(history=[])

if "chat_session" not in st.session_state or st.session_state.chat_session is None:
    st.session_state.chat_session = model.start_chat(history=[])

# --- 5. STEP ONE: POEM INPUT ---
if not st.session_state.poem_loaded:
    st.write("Paste a poem below. I will help you analyze its complex elements and prepare for the AP Exam.")
    poem_text = st.text_area("Poem Text:", height=300)
    
    if st.button("Begin AP Deconstruction"):
        if poem_text.strip():
            st.session_state.poem_loaded = True
            
            # Lock in the poem and send the initial hidden prompt to the AI
            try:
                initial_prompt = f"Here is the poem we are analyzing:\n\n{poem_text}\n\nPlease start the analysis by pointing out one specific element related to our focus ({focus_area}) and asking a high-level AP question about its effect."
                response = st.session_state.chat_session.send_message(initial_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.rerun() 
            except Exception as e:
                st.error("Error loading poem. Please try again.")
        else:
            st.warning("Please paste a poem first!")

# --- 6. STEP TWO: CHAT INTERFACE ---
if st.session_state.poem_loaded:
    st.markdown("---")
    
    # Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    user_input = st.chat_input("Type your AP-level analysis here...")
    
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        try:
            response = st.session_state.chat_session.send_message(user_input)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            
        except ResourceExhausted:
            st.error("🚨 **Traffic Jam.** \n\nThe API is currently overloaded. Please wait 60 seconds and try again.")
            if st.session_state.chat_history:
                st.session_state.chat_history.pop()
                
        except ValueError:
            st.error("🚨 **Content Filtered.** \n\nThe AI's safety filters blocked this response. Try rephrasing your analysis.")
            if st.session_state.chat_history:
                st.session_state.chat_history.pop()
                
        except Exception as e:
            st.error("An unexpected error occurred. Please refresh the page and try again.")
            if st.session_state.chat_history:
                st.session_state.chat_history.pop()

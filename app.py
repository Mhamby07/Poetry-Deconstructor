import streamlit as st
import google.generativeai as genai

# 1. Setup and Configuration
st.set_page_config(page_title="Poetry Deconstructor", page_icon="✒️")

# Securely load the API key from Streamlit secrets
genai.configure(api_key=st.secrets["API_KEY"])

st.title("✒️ The Poetry Deconstructor")
st.write("Paste a poem below. I won't give you the answers, but I will help you find the literary devices and figure out what they mean!")

# 2. System Prompt: The AI's Secret Instructions
system_prompt = """
You are an expert, encouraging high school English teacher guiding a student through a poem.
The student will provide a poem. Your job is to help them deconstruct it line by line.
CRITICAL RULE: Do NOT write an analysis or explain the theme for them. 
Instead, pick ONE specific line or stanza, identify a literary device used (e.g., metaphor, imagery, enjambment, alliteration, meter), quote the line, and ask the student a probing question about WHY the poet might have used that device and what effect it creates.
Wait for the student's response. Validate their thinking, gently correct misconceptions, and either push deeper on that same line or move to a new literary device. Keep the tone conversational, academic, and highly encouraging.
"""

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_prompt
)

# 3. Manage Session State (Memory)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "poem_loaded" not in st.session_state:
    st.session_state.poem_loaded = False

# 4. Step One: Poem Input
if not st.session_state.poem_loaded:
    poem_text = st.text_area("Paste the text of the poem here:", height=250)
    
    if st.button("Start Deconstructing"):
        if poem_text.strip():
            # Lock in the poem and send the initial hidden prompt to the AI
            st.session_state.poem_loaded = True
            initial_prompt = f"Here is the poem we are analyzing:\n\n{poem_text}\n\nPlease start the analysis by pointing out one literary device and asking a question about its effect."
            
            # Get the AI's first question
            response = st.session_state.chat_session.send_message(initial_prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            
            # Refresh the app to hide the text box and show the chat
            st.rerun() 
        else:
            st.warning("Please paste a poem first!")

# 5. Step Two: The Socratic Chat Interface
if st.session_state.poem_loaded:
    # Give students a way to reset the app for a new poem
    if st.button("Start Over with a New Poem"):
        st.session_state.chat_history = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.poem_loaded = False
        st.rerun()

    st.markdown("---")

    # Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input for the Student
    user_input = st.chat_input("Type your analysis here...")
    
    if user_input:
        # Show the user's message on screen
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Send message to Gemini and get response
        response = st.session_state.chat_session.send_message(user_input)
        
        # Show the AI's response on screen
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.chat_history.append({"role": "assistant", "content": response.text})

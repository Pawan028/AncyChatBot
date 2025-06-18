
"""
Ancy Travel Guide - Streamlit Web Application
A poetic AI travel companion powered by Groq's fast inference API
"""

import streamlit as st
import requests
import json
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

 
load_dotenv()

 
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-8b-8192"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

 
SYSTEM_PROMPT = """
You are Ancy, a warm and inspiring AI travel guide with a poetic soul and adventurous spirit.

Your characteristics:
- Speak with beautiful, flowing language and travel metaphors
- Always remain enthusiastic, encouraging, and wise
- Offer detailed advice about destinations, travel tips, cultural insights, and emotional support
- Use vivid imagery of places, journeys, and discoveries in your responses
- Be inspiring and uplifting while providing practical, actionable travel wisdom
- Share stories and insights that make travelers feel excited about their journeys
- Keep responses engaging but focused (3-6 sentences typically)

Remember: You are a companion for wanderers, dreamers, and adventurers on their life journeys.
"""

class AncyTravelGuide:
    """Ancy Travel Guide chatbot class"""
    
    def __init__(self, api_key: str):
        """Initialize Ancy with API credentials"""
        self.api_key = api_key
        
    def _make_api_request(self, user_message: str, conversation_history: List[Dict]) -> Optional[str]:
        """Make API request to Groq and return response"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Build conversation with system prompt and history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (last 10 messages to keep context manageable)
        messages.extend(conversation_history[-10:])
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.8,
            "stream": False
        }
        
        try:
            response = requests.post(
                GROQ_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                return "🔑 Authentication failed. Please check your Groq API key in .env file."
            elif response.status_code == 429:
                return "⏳ Rate limit reached. Please wait a moment before trying again."
            else:
                return f"🚫 API error ({response.status_code}): {str(e)}"
                
        except requests.exceptions.ConnectionError:
            return "🌐 Connection error. Please check your internet connection."
            
        except requests.exceptions.Timeout:
            return "⏰ Request timed out. The API might be busy, please try again."
            
        except json.JSONDecodeError:
            return "📄 Invalid response format from API."
            
        except KeyError as e:
            return f"🔍 Unexpected response structure: missing {str(e)}"
            
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def chat(self, user_input: str, conversation_history: List[Dict]) -> str:
        """Main chat method"""
        if not user_input.strip():
            return "🤔 I sense the quiet before an adventure... What's stirring in your traveler's heart?"
        
        return self._make_api_request(user_input, conversation_history)

def validate_api_key(api_key: str) -> bool:
    """Validate if API key is properly set"""
    return api_key and api_key != "YOUR_GROQ_API_KEY_HERE" and len(api_key) > 10

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ancy_initialized" not in st.session_state:
        st.session_state.ancy_initialized = False

def display_welcome_message():
    """Display Ancy's welcome message"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center; 
                margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; font-size: 2.5rem;">🌍 Ancy Travel Guide</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
            Your Poetic AI Companion for Life's Beautiful Journeys
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; 
                border-left: 5px solid #667eea; margin-bottom: 2rem;">
        <div style="color: #333;">
            <p style="margin: 0 0 1rem 0; font-size: 1.1rem;">
                🌟 <strong>Welcome, fellow wanderer!</strong> I'm Ancy, your poetic travel companion 
                ready to guide you through the endless tapestries of our beautiful world.
            </p>
            <p style="margin: 0 0 1rem 0;">
                ✈️ Whether you're dreaming of distant shores, planning your next adventure, or seeking 
                wisdom for life's journey, I'm here to inspire and assist you.
            </p>
            <p style="margin: 0; font-style: italic; color: #666;">
                What adventure shall we explore together today?
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Ancy Travel Guide",
        page_icon="🌍",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Hide Streamlit default elements
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stDeployButton {display: none;}
    
    /* Chat styling */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: fadeIn 0.5s ease-in;
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        margin-left: 2rem;
    }
    
    .ancy-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 4px solid #9c27b0;
        margin-right: 2rem;
    }
    
    .message-avatar {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .message-content {
        line-height: 1.6;
        color: #333;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Clear button styling */
    .clear-btn {
        background: #ff6b6b;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        cursor: pointer;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .clear-btn:hover {
        background: #ff5252;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Check API key
    if not GROQ_API_KEY or not validate_api_key(GROQ_API_KEY):
        st.error("❌ Groq API key not found or invalid!")
        st.info("""
        **To set up your API key:**
        1. Create a `.env` file in your project directory
        2. Add your Groq API key: `GROQ_API_KEY=your_api_key_here`
        3. Get your free API key at [console.groq.com](https://console.groq.com/)
        """)
        st.stop()
    
    # Initialize Ancy
    ancy = AncyTravelGuide(GROQ_API_KEY)
    
    # Display welcome message if this is the first time
    if not st.session_state.ancy_initialized:
        display_welcome_message()
        st.session_state.ancy_initialized = True
    
    # Clear conversation button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🗑️ Clear Conversation", key="clear_btn"):
            st.session_state.messages = []
            st.rerun()
    
    # Chat messages container
    chat_container = st.container()
    
    # Display conversation history
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-avatar">🧳 You</div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ancy-message">
                    <div class="message-avatar">🌺 Ancy</div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input section at the bottom
    st.markdown("---")
    
    # Create input form
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "",
                placeholder="Ask me about travel destinations, tips, or life's adventures...",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("Send ✈️")
    
    # Handle user input
    if submit_button and user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show typing indicator
        with st.spinner("🌸 Ancy is crafting her response..."):
            # Get Ancy's response
            response = ancy.chat(user_input, st.session_state.messages)
            
            # Add Ancy's response to history
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to show new messages
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
        🌟 Made by Pawan Kumar Yadav for dreamers everywhere | Powered by Groq AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
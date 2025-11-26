# -*- coding: utf-8 -*-
import sys
import google.generativeai as genai
from gtts import gTTS
import os
import time
import tempfile # For creating reliable temporary files

# ==========================================
# ⚠️ UNICODE FIX FOR WINDOWS CONSOLES
# ==========================================
try:
    # Force the console output to use UTF-8 to display emojis correctly
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# ==========================================
# CONFIGURATION
# ==========================================
# 🔑 PASTE YOUR GEMINI API KEY HERE!
API_KEY = "AIzaSyBf1OOrJXK86zsw0ZwhjvCW5zZlAsX5BP8" 

# Configure the AI Model
try:
    genai.configure(api_key=API_KEY)
    # FIX: Using the currently available model
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ERROR: You forgot to add your API Key in the script!")
    else:
        print(f"Error configuring API: {e}")
    exit()

# ==========================================
# CORE FUNCTIONS
# ==========================================

def speak(text):
    """
    Converts text to speech using gTTS (online) and plays it 
    using a temporary MP3 file and the operating system's player.
    """
    temp_filepath = None
    try:
        # Create a temporary file path guaranteed to exist for gTTS
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filepath = fp.name

        # 1. Generate audio and save it to the temporary file
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(temp_filepath)
        
        # 2. Play the audio file using the system's default media player
        if os.name == 'nt': # Windows (most reliable way to play audio)
            os.system(f'start {temp_filepath}')
        elif os.uname()[0] == 'Darwin': # macOS
            os.system(f'afplay {temp_filepath}')
        else: # Linux (requires mpg123, which may need manual install)
            os.system(f'mpg123 {temp_filepath}')
            
        # 3. Wait for the audio to finish playing (estimated time)
        # This is an estimate; adjust the factor (e.g., 25) for speech speed.
        time_to_wait = max(1, len(text) / 25) 
        time.sleep(time_to_wait)

    except Exception as e:
        print(f"\n❌ AUDIO ERROR: Could not generate or play audio. Check internet/gTTS/media player. ({e})")
        
    finally:
        # 4. Clean up the temporary file
        if temp_filepath and os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                # If deletion fails (e.g., file still locked), print a warning
                pass

def get_ai_correction(user_text, level):
    """
    Sends the broken English to Gemini and asks for a specific level conversion.
    """
    
    prompt = f"""
    You are a helpful and encouraging English Tutor.
    
    Task:
    1. Analyze this input text: "{user_text}"
    2. If the text is completely unintelligible or not English, explain clearly and politely why you cannot understand it.
    3. If the text is understandable (even if broken), rewrite it into **{level}** English.
    
    Guidelines for Levels:
    - "Easy": Use very simple vocabulary (top 500 words), short sentences (5-7 words max), and active voice. Like talking to a 6-year-old.
    - "Medium": Use standard professional English. Clear, polite, and grammatically perfect. Suitable for emails or work.
    - "Difficult": Use advanced vocabulary, complex sentence structures, idioms, and an academic or literary tone.
    
    Output Format:
    Only provide the rewritten text OR the explanation. Do not add introductory text like "Here is the correction".
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"I am sorry, I had trouble connecting to the brain. Error: {e}"

# ==========================================
# MAIN APP LOOP
# ==========================================

def main():
    os.system('cls' if os.name == 'nt' else 'clear') 
    print("="*50)
    print("🤖 AI ENGLISH LEVEL CONVERTER (Voice Enabled - gTTS)")
    print("="*50)
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ERROR: You forgot to add your API Key in the code!")
        return

    # Speak the initial greeting (no prefix, as requested)
    speak("Hello! I am ready to help. Please type your sentence.")

    while True:
        print("\n" + "-"*30)
        user_text = input("✍️ Enter your broken English (or 'q' to quit): ").strip()
        
        if user_text.lower() in ['q', 'quit', 'exit']:
            speak("Goodbye! Keep practicing.")
            break
            
        if not user_text:
            continue

        print("\nChoose difficulty level:")
        print("1. Easy (Simple words)")
        print("2. Medium (Professional)")
        print("3. Difficult (Advanced/Poetic)")
        
        level_choice = input("Select 1, 2, or 3: ").strip()
        
        if level_choice == '1':
            target_level = "Easy"
        elif level_choice == '2':
            target_level = "Medium"
        elif level_choice == '3':
            target_level = "Difficult"
        else:
            target_level = "Medium" 
            print("Defaulting to Medium level...")

        print(f"\nThinking... ({target_level} Mode)")
        
        result = get_ai_correction(user_text, target_level)
        
        # The result is printed, then spoken.
        print(f"\n✨ Correction: {result}")
        speak(result)

if __name__ == "__main__":
    main()
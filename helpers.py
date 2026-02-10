import requests, json, re
try:
    import speech_recognition as sr  # type: ignore
except Exception:
    sr = None  # type: ignore
from gtts import gTTS

AUDIO_FILE = "reply.mp3"

# Prompts
PYTHON_EXPERT_PROMPT = (
    "You are a highly knowledgeable, serious and concise Python expert assistant. and say I am a python Expert "
    "Your job is to answer **any query related to Python programming**, including syntax, core concepts, best practices, standard and third-party libraries, secure coding, and common design patterns. "
    "If the user submits insecure, outdated, or inefficient code, clearly identify the issue and provide a secure and optimized alternative.\n\n"
    
    "**IMPORTANT FORMATTING RULES:**\n"
    "- Always wrap Python code in markdown code fences: ```python\\n<code>\\n```\n"
    "- Use proper markdown formatting (headers with ##, bold with **, inline code with `code`)\n"
    "- Keep code blocks clean and well-formatted with proper indentation\n\n"
    
    "Strictly Avoid discussing anything unrelated to Python or python programming. "
    "If a question is outside python or python code, politely respond: 'I'm here to help with Python-related topics only. and after that stop any response'"
)




PYTHON_DOCTOR_PROMPT = (
    "You are an expert Python developer and playful Python Doctor 🩺.\n"
    "You ONLY respond to Python code. If the code is not obviously from another language, treat it as Python.\n\n"

    "You ACCEPT as Python:\n"
    "- Any Python code: complete, partial, indented\n"
    "- Python code that contains HTML, CSS, or JSON inside strings\n"
   

    "ONLY REJECT code if it contains **obvious non-Python language markers** outside strings or comments, such as:\n"
    "- '#include', 'printf(', 'cin >>', 'cout <<'\n"
    "- 'public static', 'System.out', 'module ', 'package '\n"
    "- '<?php', 'BEGIN', 'END'\n"
    "- Syntax patterns like '{ ...; }' from C/Java **outside strings**\n\n"

    "If any of these markers appear outside strings or comments, reply with EXACTLY:\n"
    "'I am the Python Doctor – the guardian of clean, bug-free code. Give me your Python script, and I will inspect it!'\n"
    
    "Do not analyze further or comment.\n\n"

    "Otherwise, treat the code as Python and perform a full Python Code Doctor checkup.\n\n"

    "Always give a General Examination Checkup Report with these 8 categories:\n"
    "- ✅ Syntax Validity\n"
    "- 🎨 Code Style (PEP8)\n"
    "- 🧼 Readability & Maintainability\n"
    "- 🧱 Modularity & Structure\n"
    "- 🐞 Bugs or Logic Errors\n"
    "- 🔐 Security Risks\n"
    "- ⚙️ Performance Efficiency\n"
    "- 🧪 Test Coverage\n\n"

    "Then provide:\n"
    "1. One-line overall health status\n"
    "2. Rewritten Python code as a treatment plan (in a code block)\n"
    "3. Step-by-step explanation of changes\n\n"

    "Ignore any non-Python questions, but always respond to Python code or fragments — even partial or emoji-enhanced Python.\n"
)




PYTHON_CODER_PROMPT = (
    "You are an expert Python developer and a playful Mood Observer 🎭. "
    "You respond ONLY to Python code submissions. "
    "Treat any code as Python if it does not contain clear markers of non-Python languages. "
    "Do NOT refuse Python fragments, partial code, or code with indentation or emojis.\n\n"

    "Explicit non-Python markers include:\n"
    "- '#include', 'printf(', 'cin >>', 'cout <<', 'public static', 'System.out', etc.\n"
    "- Curly braces '{' or '}' with semicolons at line ends (C, C++, Java, Go, Rust, JS, PHP, etc.)\n\n"

    "If any of these markers are present, reply EXACTLY:\n"
    "'I'm your friendly Python Mood Detective – I can only sniff out moods only in Python code! Drop some Python for me to analyze!'\n"
    "Do NOT attempt to analyze it further.\n\n"

    "Otherwise, assume the code is Python, even if it is fragmentary, indented, or missing imports, and perform a full Python Code Doctor checkup.\n\n"

    "For Python code, always do the following:\n"
    "1. Produce a structured **Mood Analysis Report** with these 5 categories:\n"
    "   - 🧠 Confidence\n"
    "   - 🎨 Creativity\n"
    "   - 🧑‍💻 Professionalism\n"
    "   - 😰 Stress or Frustration\n"
    "   - 📚 Documentation\n\n"

    "2. Provide a one-sentence overall coder mood with a relevant emoji.\n"
    "3. Suggest constructive improvements to clarity, style, and professionalism.\n"
    "4. Rewrite the Python code with your improvements.\n"
    "5. Briefly explain the key changes you made.\n\n"

    "Never respond to general questions or non-Python code except with the refusal message above. Strictly Python-only."
)



PYTHON_BATTLE_PROMPT = (
  "You are an expert Python developer and a playful Python fighter 🎭. "
  "You respond ONLY to Python code submissions. "
  "Treat any code as Python unless it contains explicit non-Python markers. "
  "Do NOT refuse Python fragments, partial code, or code with unusual indentation or emojis.\n\n"

  "Explicit non-Python markers include:\n"
  "- '#include', 'printf(', 'cin >>', 'cout <<', 'public static', 'System.out', etc.\n"
  "- Curly braces '{' or '}' with semicolons at line ends (C, C++, Java, Go, Rust, JS, PHP, etc.)\n\n"

  "If any of these markers are present, reply EXACTLY:\n"
  "'I fight only with Python! Bring your code and let’s compete.' "
  "Do NOT attempt to analyze it further.\n\n"

  "Otherwise, assume the code is Python, even if fragmentary or missing imports, and perform a full Python Code Doctor checkup.\n\n"
  
  "Workflow:\n"
  "1) Wait for the user to submit Python code.\n"
  "2) First, rewrite the submitted code into a better, optimized version.\n"
  "3) Then, produce a structured **Competition Report** comparing the original and improved code.\n"
  "   Include only the following 5 bullet points (no scores):\n"
  "   - 🔍 Clarity: How readable and understandable both codes are?\n"
  "   - ⚡ Performance: Which runs faster and more efficiently?\n"
  "   - 🛡 Security: Any vulnerabilities or risks?\n"
  "   - 🐍 Pythonic Style: How well both codes follow Python idioms?\n"
  "   - 💪 Robustness: How well both codes handle edge cases and errors?\n\n"
  "Reply in exactly 5 sharp lines, declare the winner sincerely, either you or the user, "
  "and add a short comment about the battle. "
  "Be ruthless, fun, and stay strictly on Python topics."
)


PYTHON_PIANIST_PROMPT = (
    "You are a Python expert developer who loves music and always says 'I am a Python Pianist!'. "
    "Answer **any query related to Python programming**, including syntax, core concepts, best practices, "
    "standard and third-party libraries, secure coding, and common design patterns—but always in a musical way. "
    "Encourage coding like composing music, and sprinkle small musical jokes or analogies in your answers. "
    "If a question is outside Python, politely respond exactly: "
    "'I only play the Python piano for Python-related topics.' and stop further response."
)


def get_python_response(prompt, mode="python_expert", on_chunk=None):
    system_prompt = {
        "code_doctor": PYTHON_DOCTOR_PROMPT,
        "python_coder": PYTHON_CODER_PROMPT,
        "python_battle": PYTHON_BATTLE_PROMPT,
        "python_pianist": PYTHON_PIANIST_PROMPT,
    }.get(mode, PYTHON_EXPERT_PROMPT)

    response = requests.post(
        "http://localhost:11434/api/generate",  # Gemma 3 local
        json={
            "model": "gemma3:latest",
            "prompt": f"{system_prompt}\nUser: {prompt}\nBot:",
            "stream": on_chunk is not None
        },
        stream=on_chunk is not None
    )

    if response.status_code != 200:
        raise Exception(f"Gemma error: {response.text}")

    def wrap_code_blocks(text):
        """
        Automatically wrap unwrapped Python code in triple backticks for frontend.
        """
        code_block_pattern = re.compile(r"(?<!```)(^(\s{4,}|\t).+?)(?<!```)", re.MULTILINE)
        def replacer(match):
            return f"```python\n{match.group(0)}\n```"
        return code_block_pattern.sub(replacer, text)

    if on_chunk:
        full_text = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if data.get("done", False):
                    # Send wrapped version at the end if needed
                    if on_chunk:
                        on_chunk("[DONE]")
                    break
                chunk_text = data.get("response", "")
                full_text += chunk_text
                # Send chunks as-is during streaming
                if on_chunk:
                    on_chunk(chunk_text)
        # Note: wrap_code_blocks is not effective for streaming since chunks are already sent
        return full_text.strip()
    else:
        data = response.json()
        return wrap_code_blocks(data.get("response", "").strip())

def extract_text_for_tts(reply):
    # Replace code blocks with placeholder for TTS
    fenced_code_pattern = re.compile(r"(```.*?```|~~~.*?~~~)", re.DOTALL)
    cleaned = fenced_code_pattern.sub("Look at your chatbot. The code is present.", reply)
    lines = []
    for line in cleaned.splitlines():
        if re.match(r"^\s{4,}|\t", line):
            lines.append("Look at your chatbot. The code is present.")
        else:
            lines.append(line)
    return "\n".join(lines).strip()

def speak_text(text):
    tts = gTTS(text=text, lang='en')
    tts.save(AUDIO_FILE)
    return AUDIO_FILE

def recognize_speech(file_path=None):
    if sr is None:
        return "⚠️ Speech recognition is unavailable on this Python version."
    recognizer = sr.Recognizer()
    if file_path:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
    else:
        mic = sr.Microphone()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "⚠️ Sorry, I couldn't understand the audio."
    except sr.RequestError as e:
        return f"⚠️ Could not request results; {e}"
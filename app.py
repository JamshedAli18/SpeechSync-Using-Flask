from flask import Flask, render_template_string, request, url_for
import pyttsx3
import os

app = Flask(__name__)

# Folder to store generated audio files
AUDIO_FOLDER = "static/audio"
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

def text_to_speech_pyttsx3(text, voice_gender='male'):
    """
    Convert input text to speech using pyttsx3 and save it as an MP3 file.
    
    Args:
        text (str): The text to convert to speech.
        voice_gender (str): Desired voice gender ('male' or 'female').
    
    Returns:
        str: Path to the saved audio file.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()

    # Get available voices
    voices = engine.getProperty('voices')

    # Select a voice based on the desired gender
    selected_voice = None
    for voice in voices:
        voice_name = voice.name.lower()
        if voice_gender.lower() == 'male' and ('david' in voice_name or 'male' in voice_name):
            selected_voice = voice
            break
        elif voice_gender.lower() == 'female' and ('zira' in voice_name or 'female' in voice_name):
            selected_voice = voice
            break

    if selected_voice:
        engine.setProperty('voice', selected_voice.id)
    else:
        print(f"No {voice_gender} voice found. Using default voice.")

    # Set other properties
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

    # Save the audio to a file
    audio_file = os.path.join(AUDIO_FOLDER, "output.mp3")
    engine.save_to_file(text, audio_file)
    engine.runAndWait()

    return audio_file

@app.route('/', methods=['GET', 'POST'])
def index():
    audio_url = None
    error = None

    if request.method == 'POST':
        text = request.form.get('text')
        voice_gender = request.form.get('voice_gender')

        if not text or text.strip() == "":
            error = "Please enter some text to convert to speech."
        else:
            try:
                audio_file = text_to_speech_pyttsx3(text, voice_gender)
                audio_url = url_for('static', filename='audio/output.mp3')
            except Exception as e:
                error = f"Error generating audio: {str(e)}"

    # HTML template with embedded CSS
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Text-to-Speech Converter</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-height: 100vh;
                background: linear-gradient(135deg, #6e8efb, #a777e3);
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                padding: 30px;
                width: 100%;
                max-width: 500px;
                text-align: center;
                backdrop-filter: blur(10px);
                transition: transform 0.3s ease;
            }
            .container:hover {
                transform: scale(1.02);
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
                font-size: 2rem;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            label {
                display: block;
                color: #555;
                font-weight: 500;
                margin-bottom: 8px;
            }
            textarea {
                width: 100%;
                height: 120px;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 1rem;
                resize: vertical;
                transition: border-color 0.3s ease;
            }
            textarea:focus {
                border-color: #6e8efb;
                outline: none;
                box-shadow: 0 0 5px rgba(110, 142, 251, 0.5);
            }
            select {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 1rem;
                background: #fff;
                cursor: pointer;
                transition: border-color 0.3s ease;
            }
            select:focus {
                border-color: #6e8efb;
                outline: none;
                box-shadow: 0 0 5px rgba(110, 142, 251, 0.5);
            }
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(45deg, #6e8efb, #a777e3);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.3s ease, background 0.3s ease;
            }
            button:hover {
                transform: translateY(-2px);
                background: linear-gradient(45deg, #5d7de6, #915fc7);
            }
            .error {
                color: #e74c3c;
                margin-top: 10px;
                font-size: 0.9rem;
                text-align: center;
            }
            .audio-player {
                margin-top: 20px;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            audio {
                width: 100%;
                outline: none;
            }
            @media (max-width: 600px) {
                .container {
                    padding: 20px;
                }
                h1 {
                    font-size: 1.5rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Text-to-Speech</h1>
            <form method="POST">
                <div class="form-group">
                    <label for="text">Enter Text:</label>
                    <textarea id="text" name="text" placeholder="Type your text here..." required></textarea>
                </div>
                <div class="form-group">
                    <label for="voice_gender">Select Voice:</label>
                    <select id="voice_gender" name="voice_gender">
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                    </select>
                </div>
                <button type="submit">Convert to Speech</button>
            </form>

            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}

            {% if audio_url %}
                <div class="audio-player">
                    <p>Listen to the audio:</p>
                    <audio controls autoplay>
                        <source src="{{ audio_url }}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """

    return render_template_string(html_content, audio_url=audio_url, error=error)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template_string, jsonify, request
import webbrowser
import subprocess
import platform
import datetime
import threading
import time
import random

# Try to import optional packages
try:
    import speech_recognition as sr
    import pyttsx3

    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("Warning: Speech recognition not available. Install speechrecognition and pyttsx3")

try:
    import wikipedia

    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False
    print("Warning: Wikipedia not available. Install wikipedia package")

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("Warning: Email functionality not available")

app = Flask(__name__)

# Global variables
last_response = {'status': 'no_response'}
is_processing = False

# Initialize speech components if available
if SPEECH_AVAILABLE:
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        tts_engine = pyttsx3.init()
    except Exception as e:
        print(f"Speech initialization error: {e}")
        SPEECH_AVAILABLE = False

# Email configuration - UPDATE THESE WITH YOUR CREDENTIALS
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'your_email@gmail.com'  # Replace with your email
EMAIL_PASS = 'your_app_password'  # Replace with your app password

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Voice Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #333;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 600px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .header {
            margin-bottom: 30px;
        }

        .title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 20px;
        }

        .status-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }

        .status {
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }

        .greeting {
            font-size: 1.2rem;
            color: #667eea;
            font-weight: 500;
            margin-bottom: 20px;
        }

        .controls {
            margin: 30px 0;
        }

        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1rem;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            font-weight: 600;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .btn-secondary {
            background: linear-gradient(135deg, #6c757d, #495057);
            box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
        }

        .btn-secondary:hover {
            box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
        }

        .response-area {
            margin-top: 30px;
        }

        .response-card {
            background: #fff;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            border-left: 4px solid #28a745;
            text-align: left;
        }

        .response-card.error {
            border-left-color: #dc3545;
            background: #fff5f5;
        }

        .response-card.warning {
            border-left-color: #ffc107;
            background: #fffbf0;
        }

        .response-card.email_waiting {
            border-left-color: #17a2b8;
            background: #f0f9ff;
        }

        .query {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }

        .response {
            color: #333;
            line-height: 1.6;
        }

        .listening-indicator {
            display: none;
            margin: 20px 0;
        }

        .listening-animation {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            margin: 0 auto 15px;
            position: relative;
            animation: pulse 2s infinite;
        }

        .listening-animation::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
        }

        .feature-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }

        .feature-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }

        .feature-desc {
            font-size: 0.9rem;
            color: #666;
        }

        .warning-banner {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🎤 AI Voice Assistant</h1>
            <p class="subtitle">Your intelligent voice-powered companion</p>
        </div>

        {% if not speech_available %}
        <div class="warning-banner">
            ⚠️ Speech recognition not available. Install required packages: pip install speechrecognition pyttsx3 pyaudio
        </div>
        {% endif %}

        <div class="status-card">
            <div class="status" id="status">Ready to help</div>
            <div class="greeting" id="greeting">Click "Get Greeting" to start!</div>
        </div>

        <div class="controls">
            <button class="btn" id="greetBtn" onclick="getGreeting()">👋 Get Greeting</button>
            {% if speech_available %}
            <button class="btn" id="listenBtn" onclick="startListening()">🎤 Start Listening</button>
            {% endif %}
            <button class="btn" onclick="testFeatures()">🧪 Test Features</button>
        </div>

        <div class="listening-indicator" id="listeningIndicator">
            <div class="listening-animation"></div>
            <div class="status">Listening for your command...</div>
        </div>

        <div class="feature-grid">
            <div class="feature-card" onclick="openWebsite('youtube')">
                <div class="feature-icon">🎥</div>
                <div class="feature-title">Open YouTube</div>
                <div class="feature-desc">Click to open YouTube</div>
            </div>
            <div class="feature-card" onclick="openWebsite('google')">
                <div class="feature-icon">🌐</div>
                <div class="feature-title">Open Google</div>
                <div class="feature-desc">Click to open Google</div>
            </div>
            <div class="feature-card" onclick="openApp('code')">
                <div class="feature-icon">💻</div>
                <div class="feature-title">Open VS Code</div>
                <div class="feature-desc">Click to launch VS Code</div>
            </div>
            <div class="feature-card" onclick="getTime()">
                <div class="feature-icon">⏰</div>
                <div class="feature-title">Get Time</div>
                <div class="feature-desc">Click to get current time</div>
            </div>
            <div class="feature-card" onclick="getDate()">
                <div class="feature-icon">📅</div>
                <div class="feature-title">Get Date</div>
                <div class="feature-desc">Click to get current date</div>
            </div>
        </div>

        <div class="response-area" id="responseArea"></div>
    </div>

    <script>
        let isListening = false;
        let responseCheckInterval;

        function getGreeting() {
            fetch('/api/greeting')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('greeting').innerHTML = `🎉 ${data.message}`;
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('greeting').innerHTML = '❌ Error getting greeting';
                });
        }

        function startListening() {
            if (isListening) return;

            isListening = true;
            const listenBtn = document.getElementById('listenBtn');
            if (listenBtn) {
                listenBtn.disabled = true;
                listenBtn.innerHTML = '⏳ Listening...';
            }
            document.getElementById('listeningIndicator').style.display = 'block';

            fetch('/api/listen', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showResponse({
                            type: 'error',
                            message: data.error,
                            query: '',
                            action: ''
                        });
                        resetListening();
                    } else {
                        checkForResponse();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    resetListening();
                    showResponse({
                        type: 'error',
                        message: 'Failed to start listening',
                        query: '',
                        action: ''
                    });
                });
        }

        function checkForResponse() {
            responseCheckInterval = setInterval(() => {
                fetch('/api/response')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status !== 'no_response') {
                            clearInterval(responseCheckInterval);
                            resetListening();
                            showResponse(data);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        clearInterval(responseCheckInterval);
                        resetListening();
                    });
            }, 500);
        }

        function resetListening() {
            isListening = false;
            const listenBtn = document.getElementById('listenBtn');
            if (listenBtn) {
                listenBtn.disabled = false;
                listenBtn.innerHTML = '🎤 Start Listening';
            }
            document.getElementById('listeningIndicator').style.display = 'none';
        }

        function showResponse(data) {
            const responseArea = document.getElementById('responseArea');
            const responseCard = document.createElement('div');
            responseCard.className = `response-card ${data.type}`;

            const timestamp = new Date().toLocaleTimeString();

            responseCard.innerHTML = `
                ${data.query ? `<div class="query">🗣️ You said: "${data.query}"</div>` : ''}
                <div class="response">${getResponseIcon(data.type)} ${data.message}</div>
                <div class="timestamp">⏰ ${timestamp}</div>
            `;

            responseArea.insertBefore(responseCard, responseArea.firstChild);

            while (responseArea.children.length > 10) {
                responseArea.removeChild(responseArea.lastChild);
            }
        }

        function getResponseIcon(type) {
            switch(type) {
                case 'success': return '✅';
                case 'error': return '❌';
                case 'warning': return '⚠️';
                default: return 'ℹ️';
            }
        }

        // Manual feature testing functions
        function openWebsite(site) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: `open ${site}`})
            })
            .then(response => response.json())
            .then(data => showResponse(data));
        }

        function openApp(app) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: `open ${app}`})
            })
            .then(response => response.json())
            .then(data => showResponse(data));
        }

        function getTime() {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: 'time'})
            })
            .then(response => response.json())
            .then(data => showResponse(data));
        }

        function getDate() {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: 'date'})
            })
            .then(response => response.json())
            .then(data => showResponse(data));
        }

        function testFeatures() {
            showResponse({
                type: 'success',
                message: 'All basic features are working! Click on the feature cards above to test individual functions.',
                query: 'Test',
                action: 'test'
            });
        }

        document.addEventListener('DOMContentLoaded', function() {
            getGreeting();
        });
    </script>
</body>
</html>
"""


def speak(text):
    """Convert text to speech"""
    if not SPEECH_AVAILABLE:
        print(f"TTS: {text}")
        return

    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")


def listen_for_audio():
    """Listen for audio input and process commands"""
    global last_response, is_processing

    if not SPEECH_AVAILABLE:
        last_response = {
            'type': 'error',
            'message': 'Speech recognition not available. Please install required packages.',
            'query': '',
            'action': 'no_speech'
        }
        return

    try:
        is_processing = True
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        # Recognize speech
        query = recognizer.recognize_google(audio).lower()
        print(f"Recognized: {query}")

        # Process the command
        response = process_command(query)
        response['query'] = query
        last_response = response

    except sr.WaitTimeoutError:
        last_response = {
            'type': 'warning',
            'message': 'No speech detected. Please try again.',
            'query': '',
            'action': 'timeout'
        }
    except sr.UnknownValueError:
        last_response = {
            'type': 'error',
            'message': 'Sorry, I could not understand your speech.',
            'query': '',
            'action': 'unknown'
        }
    except Exception as e:
        last_response = {
            'type': 'error',
            'message': f'Error: {str(e)}',
            'query': '',
            'action': 'error'
        }
    finally:
        is_processing = False


def process_command(query):
    """Process voice commands and return appropriate response"""

    # Wikipedia search
    if 'wikipedia' in query and WIKIPEDIA_AVAILABLE:
        try:
            topic = query.replace('wikipedia', '').strip()
            if topic:
                summary = wikipedia.summary(topic, sentences=2)
                speak(summary)
                return {
                    'type': 'success',
                    'message': f'Wikipedia result for "{topic}": {summary}',
                    'action': 'wikipedia'
                }
            else:
                return {
                    'type': 'warning',
                    'message': 'Please specify what you want to search on Wikipedia',
                    'action': 'wikipedia_prompt'
                }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Wikipedia search failed: {str(e)}',
                'action': 'wikipedia_error'
            }

    # Open websites
    elif 'open youtube' in query or query == 'youtube':
        webbrowser.open('https://www.youtube.com')
        speak("Opening YouTube")
        return {
            'type': 'success',
            'message': 'Opening YouTube in your browser',
            'action': 'open_website'
        }

    elif 'open google' in query or query == 'google':
        webbrowser.open('https://www.google.com')
        speak("Opening Google")
        return {
            'type': 'success',
            'message': 'Opening Google in your browser',
            'action': 'open_website'
        }

    # Open applications
    elif 'open code' in query or query == 'code':
        try:
            if platform.system() == 'Windows':
                subprocess.Popen(['code'])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['code'])
            else:  # Linux
                subprocess.Popen(['code'])
            speak("Opening Visual Studio Code")
            return {
                'type': 'success',
                'message': 'Opening Visual Studio Code',
                'action': 'open_app'
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Could not open VS Code: {str(e)}',
                'action': 'app_error'
            }

    # Time and date
    elif 'time' in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        return {
            'type': 'success',
            'message': f'Current time: {current_time}',
            'action': 'time'
        }

    elif 'date' in query:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
        return {
            'type': 'success',
            'message': f'Today\'s date: {current_date}',
            'action': 'date'
        }

    # Default response
    else:
        return {
            'type': 'warning',
            'message': 'Sorry, I didn\'t understand that command. Available commands: Open YouTube, Open Google, Open Code, Time, Date.',
            'action': 'unknown_command'
        }


# Flask routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, speech_available=SPEECH_AVAILABLE)


@app.route('/api/greeting')
def greeting():
    greetings = [
        "Hello! I'm your AI assistant. How can I help you today?",
        "Hi there! Ready to assist you!",
        "Welcome! I can help you open websites, get time/date, and more!",
        "Greetings! Your assistant is ready to serve!"
    ]
    message = random.choice(greetings)
    return jsonify({'message': message})


@app.route('/api/status')
def status():
    if is_processing:
        return jsonify({'status': 'Processing your request...'})
    else:
        return jsonify({'status': 'Ready to help'})


@app.route('/api/listen', methods=['POST'])
def listen():
    global last_response

    if not SPEECH_AVAILABLE:
        return jsonify({'error': 'Speech recognition not available'})

    last_response = {'status': 'no_response'}

    # Start listening in a separate thread
    thread = threading.Thread(target=listen_for_audio)
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'started_listening'})


@app.route('/api/response')
def get_response():
    return jsonify(last_response)


@app.route('/api/command', methods=['POST'])
def manual_command():
    """Handle manual commands from UI buttons"""
    data = request.json
    command = data.get('command', '').lower()

    response = process_command(command)
    response['query'] = f'Manual: {command}'

    return jsonify(response)


if __name__ == '__main__':
    print("Starting AI Assistant...")
    print("=" * 50)
    print("INSTALLATION STATUS:")
    print(f"✅ Flask: Available")
    print(
        f"{'✅' if SPEECH_AVAILABLE else '❌'} Speech Recognition: {'Available' if SPEECH_AVAILABLE else 'Not Available'}")
    print(f"{'✅' if WIKIPEDIA_AVAILABLE else '❌'} Wikipedia: {'Available' if WIKIPEDIA_AVAILABLE else 'Not Available'}")
    print(f"{'✅' if EMAIL_AVAILABLE else '❌'} Email: {'Available' if EMAIL_AVAILABLE else 'Not Available'}")
    print("=" * 50)

    if not SPEECH_AVAILABLE:
        print("To enable speech recognition, run:")
        print("pip install speechrecognition pyttsx3 pyaudio")
        print()

    print("🌐 Open http://localhost:5000 in your browser")
    print("📱 The app will work with basic features even without speech packages!")

    app.run(debug=True, host='0.0.0.0', port=5000)
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const micBtn = document.getElementById('micBtn');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const captionCard = document.getElementById('captionCard');
    const captionText = document.getElementById('captionText');
    const captionMode = document.getElementById('captionMode');
    const captionLabel = document.getElementById('captionLabel');
    const chatFeed = document.getElementById('chatFeed');
    const clearBtn = document.getElementById('clearBtn');
    const textForm = document.getElementById('textForm');
    const textInput = document.getElementById('textInput');
    const canvas = document.getElementById('visualizerCanvas');
    const canvasCtx = canvas.getContext('2d');

    // State Variables
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let audioContext = null;
    let analyser = null;
    let dataArray = null;
    let animationId = null;
    let speechRecognition = null;
    let currentAudio = null;

    // Canvas Sizing
    function resizeCanvas() {
        canvas.width = canvas.parentElement.clientWidth - 40;
        canvas.height = 110;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize Web Speech Recognition for Realtime Captions
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        speechRecognition = new SpeechRecognition();
        speechRecognition.continuous = true;
        speechRecognition.interimResults = true;
        speechRecognition.lang = 'en-US';

        speechRecognition.onresult = (event) => {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                interimTranscript += event.results[i][0].transcript;
            }
            if (isRecording && interimTranscript.trim()) {
                updateCaptions(interimTranscript, 'USER SPEAKING', 'User');
            }
        };

        speechRecognition.onerror = (event) => {
            console.warn('Speech recognition event:', event.error);
        };
    }

    // Toggle Microphone Recording
    micBtn.addEventListener('click', () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    // Spacebar Key Trigger
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && document.activeElement !== textInput) {
            e.preventDefault();
            if (isRecording) {
                stopRecording();
            } else {
                startRecording();
            }
        }
    });

    // Start Audio Capture
    async function startRecording() {
        if (isRecording) return;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                stream.getTracks().forEach(track => track.stop());
                await processAudioInput(audioBlob);
            };

            // Audio Visualizer Setup
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(stream);
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 64;
            source.connect(analyser);
            dataArray = new Uint8Array(analyser.frequencyBinCount);

            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add('recording');
            setStatus('listening', 'Listening...');
            updateCaptions('Listening to your voice...', 'RECORDING', 'User');

            if (speechRecognition) {
                try { speechRecognition.start(); } catch (err) {}
            }

            drawVisualizer();
        } catch (err) {
            console.error('Microphone access error:', err);
            updateCaptions('Microphone access error. Please allow mic permissions.', 'ERROR', 'System');
        }
    }

    // Stop Audio Capture
    function stopRecording() {
        if (!isRecording) return;
        isRecording = false;
        micBtn.classList.remove('recording');

        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        if (speechRecognition) {
            try { speechRecognition.stop(); } catch (err) {}
        }
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        drawIdleVisualizer();
        setStatus('processing', 'Transcribing...');
        updateCaptions('Processing voice audio with Groq Whisper...', 'TRANSCRIBING', 'Whisper AI');
    }

    // Process Recorded Audio File via Backend API
    async function processAudioInput(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.webm');

            // 1. Transcribe with Whisper
            const transcribeRes = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });

            if (!transcribeRes.ok) {
                const errData = await transcribeRes.json();
                throw new Error(errData.detail || 'Transcription failed');
            }

            const transcribeData = await transcribeRes.json();
            const userText = transcribeData.text.trim();

            if (!userText) {
                setStatus('ready', 'Ready');
                updateCaptions('No speech was detected. Please try again.', 'IDLE', 'System');
                return;
            }

            // Append user message to chat feed
            appendChatMessage('user', userText);
            updateCaptions(`"${userText}"`, 'USER PROMPT', 'User');

            // 2. Chat Completion with Groq Llama 3.3
            setStatus('processing', 'Thinking...');
            const chatRes = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userText })
            });

            if (!chatRes.ok) {
                const errData = await chatRes.json();
                throw new Error(errData.detail || 'Chat request failed');
            }

            const chatData = await chatRes.json();
            const aiReply = chatData.response;

            // Append assistant reply to chat feed
            appendChatMessage('assistant', aiReply);

            // 3. Text to Speech Response
            setStatus('speaking', 'Speaking...');
            await playTTSResponse(aiReply);

        } catch (err) {
            console.error('Processing error:', err);
            setStatus('ready', 'Error');
            updateCaptions(`Error: ${err.message}`, 'ERROR', 'System');
        }
    }

    // Play Voice Response and Stream Typewriter Captions
    async function playTTSResponse(text) {
        try {
            const ttsRes = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });

            if (!ttsRes.ok) throw new Error('TTS failed');

            const blob = await ttsRes.blob();
            const audioUrl = URL.createObjectURL(blob);

            if (currentAudio) {
                currentAudio.pause();
            }

            currentAudio = new Audio(audioUrl);

            // Typewriter Captions effect synchronised with voice
            typewriterCaption(text);

            currentAudio.onended = () => {
                setStatus('ready', 'Ready');
                captionMode.textContent = 'Idle';
                drawIdleVisualizer();
            };

            await currentAudio.play();
            drawPlaybackVisualizer();

        } catch (err) {
            console.error('TTS playback error:', err);
            setStatus('ready', 'Ready');
            updateCaptions(text, 'AI RESPONSE', 'VoiceSphere');
        }
    }

    // Typewriter Subtitle Animation
    function typewriterCaption(fullText) {
        captionLabel.textContent = 'AI RESPONSE';
        captionMode.textContent = 'Speaking';
        captionCard.classList.add('active');
        captionText.textContent = '';

        let index = 0;
        const speed = Math.max(15, Math.floor(12000 / fullText.length)); // Adapt speed to length

        const interval = setInterval(() => {
            captionText.textContent = fullText.slice(0, index);
            index++;
            if (index > fullText.length) {
                clearInterval(interval);
            }
        }, speed);
    }

    // Text Form Submission (Alternative to Voice)
    textForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = textInput.value.trim();
        if (!text) return;

        textInput.value = '';
        appendChatMessage('user', text);
        updateCaptions(`"${text}"`, 'USER PROMPT', 'User');

        setStatus('processing', 'Thinking...');
        try {
            const chatRes = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const chatData = await chatRes.json();
            appendChatMessage('assistant', chatData.response);
            setStatus('speaking', 'Speaking...');
            await playTTSResponse(chatData.response);
        } catch (err) {
            updateCaptions(`Error: ${err.message}`, 'ERROR', 'System');
            setStatus('ready', 'Ready');
        }
    });

    // Helper: Update UI Captions
    function updateCaptions(text, mode, label) {
        captionText.textContent = text;
        captionMode.textContent = mode;
        captionLabel.textContent = label || 'LIVE CAPTIONS';
        captionCard.classList.add('active');
    }

    // Helper: Set System Status Indicator
    function setStatus(stateClass, label) {
        statusIndicator.className = `status-indicator ${stateClass}`;
        statusText.textContent = label;
    }

    // Helper: Append Message to Feed
    function appendChatMessage(role, text) {
        const welcome = chatFeed.querySelector('.welcome-message');
        if (welcome) welcome.remove();

        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${role}`;
        
        const roleSpan = document.createElement('div');
        roleSpan.className = 'bubble-role';
        roleSpan.textContent = role === 'user' ? 'You' : 'VoiceSphere AI';

        const textDiv = document.createElement('div');
        textDiv.className = 'bubble-text';
        textDiv.textContent = text;

        bubble.appendChild(roleSpan);
        bubble.appendChild(textDiv);
        chatFeed.appendChild(bubble);

        chatFeed.scrollTop = chatFeed.scrollHeight;
    }

    // Clear History Button
    clearBtn.addEventListener('click', () => {
        chatFeed.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">✨</div>
                <h3>Realtime AI Speech Assistant</h3>
                <p>History cleared. Click the microphone or press Spacebar to start a new conversation!</p>
            </div>
        `;
        updateCaptions('Press the microphone button below or hit Spacebar to start speaking...', 'Idle', 'LIVE CAPTIONS');
        captionCard.classList.remove('active');
    });

    // Audio Visualizer - Microphone Wave Animation
    function drawVisualizer() {
        if (!isRecording) return;
        animationId = requestAnimationFrame(drawVisualizer);

        analyser.getByteFrequencyData(dataArray);
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

        const barWidth = (canvas.width / dataArray.length) * 2;
        let x = 0;

        for (let i = 0; i < dataArray.length; i++) {
            const barHeight = (dataArray[i] / 255) * canvas.height * 0.85;
            
            const gradient = canvasCtx.createLinearGradient(0, canvas.height, 0, 0);
            gradient.addColorStop(0, '#00f2fe');
            gradient.addColorStop(1, '#ff0844');

            canvasCtx.fillStyle = gradient;
            canvasCtx.fillRect(x, canvas.height - barHeight, barWidth - 3, barHeight);
            x += barWidth;
        }
    }

    // Audio Visualizer - Playback Pulse Animation
    function drawPlaybackVisualizer() {
        if (!currentAudio || currentAudio.paused) return;
        requestAnimationFrame(drawPlaybackVisualizer);

        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        const time = Date.now() * 0.003;
        canvasCtx.beginPath();
        canvasCtx.lineWidth = 3;
        canvasCtx.strokeStyle = '#4facfe';

        for (let x = 0; x < canvas.width; x += 5) {
            const y = canvas.height / 2 + Math.sin(x * 0.02 + time) * 25 * Math.cos(x * 0.005);
            if (x === 0) canvasCtx.moveTo(x, y);
            else canvasCtx.lineTo(x, y);
        }
        canvasCtx.stroke();
    }

    // Audio Visualizer - Idle State
    function drawIdleVisualizer() {
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        canvasCtx.beginPath();
        canvasCtx.lineWidth = 1.5;
        canvasCtx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        canvasCtx.moveTo(0, canvas.height / 2);
        canvasCtx.lineTo(canvas.width, canvas.height / 2);
        canvasCtx.stroke();
    }

    // Initial Idle Visualizer Draw
    drawIdleVisualizer();
});

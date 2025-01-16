interface WhisperOptions {
    minVolume?: number;        // Minimum volume threshold (0-1)
    silenceLength?: number;    // Minimum silence duration in seconds
    language?: string;         // Language code for transcription
    translate?: boolean;       // Whether to translate to English
    prompt?: string;          // Optional prompt for the API
}

interface WhisperResponse {
    text: string;
    language?: string;
    segments?: Array<{
        id: number;
        seek: number;
        start: number;
        end: number;
        text: string;
        tokens: number[];
        temperature: number;
        avg_logprob: number;
        compression_ratio: number;
        no_speech_prob: number;
    }>;
}

export class WhisperService {
    private mediaRecorder: MediaRecorder | null = null;
    private audioChunks: Blob[] = [];
    private isRecording = false;
    private options: WhisperOptions;
    private onTranscriptionCallback: ((text: string) => void) | null = null;
    private onErrorCallback: ((error: string) => void) | null = null;
    private analyser: AnalyserNode | null = null;
    private silenceStart: number | null = null;
    private stream: MediaStream | null = null;
    private audioContext: AudioContext | null = null;
    private isMonitoring = false;

    constructor(options: WhisperOptions = {}) {
        // console.log('WhisperService initialized with options:', options);
        this.options = {
            minVolume: options.minVolume ?? 0.01,
            silenceLength: options.silenceLength ?? 1.5,
            language: options.language,
            translate: options.translate ?? false,
            prompt: options.prompt
        };
    }

    public onTranscription(callback: (text: string) => void) {
        this.onTranscriptionCallback = callback;
    }

    public onError(callback: (error: string) => void) {
        this.onErrorCallback = callback;
    }

    private handleError(error: string) {
        // console.error('WhisperService error:', error);
        if (this.onErrorCallback) {
            this.onErrorCallback(error);
        }
    }

    public async startRecording() {
        if (this.isRecording) {
            // console.log('Already recording, ignoring start request');
            return;
        }

        try {
            // Initialize audio stream if not exists
            if (!this.stream) {
                // console.log('Requesting microphone access...');
                this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            }

            // Initialize audio context if not exists
            if (!this.audioContext) {
                this.audioContext = new AudioContext();
                const source = this.audioContext.createMediaStreamSource(this.stream);
                this.analyser = this.audioContext.createAnalyser();
                this.analyser.fftSize = 2048;
                source.connect(this.analyser);
            }

            // Start monitoring for sound
            if (!this.isMonitoring) {
                this.isMonitoring = true;
                this.monitorAudio();
            }

        } catch (err) {
            this.handleError(`Failed to initialize audio: ${err}`);
        }
    }

    private startRecordingSession() {
        // console.log('Starting recording session...');
        this.mediaRecorder = new MediaRecorder(this.stream!);
        this.audioChunks = [];
        this.isRecording = true;

        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                // console.log('Audio data available, size:', event.data.size);
                this.audioChunks.push(event.data);
            }
        };

        this.mediaRecorder.onstop = async () => {
            // console.log('MediaRecorder stopped, processing audio chunks...');
            if (this.audioChunks.length > 0) {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/mp3' });
                // console.log('Created audio blob, size:', audioBlob.size);
                await this.transcribeAudio(audioBlob);
                this.audioChunks = [];
            }
            this.isRecording = false;
        };

        this.mediaRecorder.start(1000); // Collect data every second
        // console.log('MediaRecorder started');
    }

    private monitorAudio() {
        if (!this.analyser || !this.isMonitoring) return;

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.analyser.getByteTimeDomainData(dataArray);

        const volume = dataArray.reduce((acc, val) => acc + Math.abs(val - 128), 0) / (bufferLength * 128);

        if (volume < this.options.minVolume!) {
            if (this.silenceStart === null && this.isRecording) {
                // console.log('Silence detected, starting silence timer');
                this.silenceStart = Date.now();
            } else if (this.silenceStart && this.isRecording && 
                      Date.now() - this.silenceStart > this.options.silenceLength! * 1000) {
                // console.log('Silence threshold reached, stopping recording');
                this.stopRecordingSession();
                this.silenceStart = null;
            }
        } else {
            // Sound detected
            if (!this.isRecording) {
                // console.log('Sound detected, starting new recording');
                this.startRecordingSession();
            }
            if (this.silenceStart !== null) {
                // console.log('Sound detected, resetting silence timer');
                this.silenceStart = null;
            }
        }

        requestAnimationFrame(() => this.monitorAudio());
    }

    private stopRecordingSession() {
        if (!this.isRecording) return;
        
        // console.log('Stopping recording session...');
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
    }

    public stopRecording() {
        // console.log('Stopping recording completely...');
        this.isMonitoring = false;
        this.isRecording = false;
        
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }

        this.silenceStart = null;
        this.analyser = null;
    }

    private async transcribeAudio(audioBlob: Blob): Promise<void> {
        if (audioBlob.size === 0) {
            // console.log('Empty audio blob, skipping transcription');
            return;
        }

        // console.log('Starting transcription of audio blob:', audioBlob.size, 'bytes');
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.mp3');
        formData.append('model', 'whisper-1');
        formData.append('response_format', 'verbose_json');

        if (this.options.language) {
            formData.append('language', this.options.language);
        }

        if (this.options.prompt) {
            formData.append('prompt', this.options.prompt);
        }

        if (this.options.translate) {
            formData.append('translate', 'true');
        }

        try {
            // console.log('Sending transcription request to server...');
            const response = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Transcription failed');
            }

            const result: WhisperResponse = await response.json();
            // console.log('Received transcription:', result.text);

            if (this.onTranscriptionCallback && result.text.trim()) {
                this.onTranscriptionCallback(result.text);
            }

        } catch (err) {
            this.handleError(`Transcription failed: ${err}`);
        }
    }
} 
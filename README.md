# Chattie - AI-Enhanced Team Communication Platform

## Overview
Chattie is a modern team communication platform built with SvelteKit, combining Slack-like features with advanced AI capabilities for enhanced collaboration.

## Features

### Core Communication
- 💬 Real-time messaging with WebSocket
- 📂 Channels and direct messages
- 🧵 Thread support
- 📎 File sharing and search
- 👋 User presence and status
- 😀 Emoji reactions

### AI Capabilities
- 🤖 Intelligent message summarization
- 🗣️ Speech synthesis and voice messages
- 👤 Facial animation for avatars
- 🎯 Context-aware responses
- 🔍 AI-powered search
- 💡 Smart suggestions

## Tech Stack

### Frontend
- SvelteKit
- TailwindCSS
- Socket.io-client
- MediaPipe (facial animation)

### Backend
- Node.js
- WebSocket
- PostgreSQL + Prisma
- Redis (caching)

### AI Infrastructure
- LangChain
- Pinecone (vector DB)
- OpenAI API
- ElevenLabs (voice synthesis)

## Project Structure
```
chattie/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── chat/          # Message components
│   │   │   ├── channels/      # Channel management
│   │   │   ├── ai/           # AI components
│   │   │   └── shared/       # Common UI elements
│   │   ├── stores/           # Svelte stores
│   │   ├── services/         # API and WebSocket
│   │   └── utils/           # Helper functions
│   ├── routes/
│   │   ├── api/             # API endpoints
│   │   ├── channels/        # Channel routes
│   │   └── dm/             # Direct message routes
│   └── app.html
├── static/                  # Static assets
├── tests/                  # Test suite
└── prisma/                # Database schema
```

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chattie.git
cd chattie
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Start development server:
```bash
npm run dev
```

## AI Integration Guide

### Model Setup
1. Configure API keys in `.env`:
```env
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
```

2. Initialize AI services:
```typescript
// src/lib/services/ai/setup.ts
import { initLangChain, initPinecone, initVoiceSynthesis } from './ai';

export async function setupAI() {
  await Promise.all([
    initLangChain(),
    initPinecone(),
    initVoiceSynthesis()
  ]);
}
```

### Key AI Features

#### Context-Aware Chat
- Message vectorization for semantic search
- Thread summarization
- Smart suggestions based on conversation context

#### Voice & Animation
- Real-time voice synthesis
- Facial animation for avatars
- Speech-to-text for voice messages

#### Search & Discovery
- AI-powered message search
- Channel recommendations
- Content categorization

## Development Workflow

1. Create feature branch:
```bash
git checkout -b feature/your-feature
```

2. Make changes and test:
```bash
npm run test
```

3. Submit PR for review

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

This updated README provides a clearer structure, better documentation of AI features, and a more practical getting started guide. It maintains focus on both the communication platform aspects and the AI integration while providing concrete implementation details.Â
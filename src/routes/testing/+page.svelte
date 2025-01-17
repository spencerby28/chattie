<script lang="ts">
    import type { PageData } from './$types';
    import { Speaker, Loader2 } from 'lucide-svelte';
    import { toast } from 'svelte-sonner';

    export let data: PageData;
    let loadingVoiceId: string | null = null;
    let playingAudio: { element: HTMLAudioElement; voiceId: string } | null = null;

    // Map AI personas by their ID for easy lookup
    const personasById = new Map(data.ai_personas.map(persona => [persona.sender_id, persona]));

    // Helper function to get persona info for a message
    function getPersonaInfo(userId: string) {
        const persona = personasById.get(userId);
        return {
            name: persona?.name || userId,
            voiceId: persona?.voice_id || null
        };
    }

    async function playTextToSpeech(voiceId: string, text: string) {
        // If already playing this audio, stop it
        if (playingAudio?.voiceId === voiceId) {
            playingAudio.element.pause();
            playingAudio.element.currentTime = 0;
            playingAudio = null;
            return;
        }

        // Stop any other playing audio
        if (playingAudio) {
            playingAudio.element.pause();
            playingAudio.element.currentTime = 0;
            playingAudio = null;
        }

        if (loadingVoiceId) return;
        loadingVoiceId = voiceId;
        
        try {
            const response = await fetch('/api/speech', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ voiceId, text })
            });

            if (!response.ok) throw new Error('Failed to convert text to speech');

            const { audio } = await response.json();
            const audioElement = new Audio(`data:audio/mp3;base64,${audio}`);
            
            audioElement.addEventListener('ended', () => {
                playingAudio = null;
            });

            await audioElement.play();
            playingAudio = { element: audioElement, voiceId };
        } catch (error) {
            console.error('Text-to-speech error:', error);
            toast.error('Failed to play audio');
        } finally {
            loadingVoiceId = null;
        }
    }
</script>

<div class="container mx-auto p-4 space-y-6">
    <!-- Display AI Personas -->
    <div class="border rounded-lg p-4 bg-muted">
        <h2 class="text-lg font-semibold mb-2">AI Personas</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each data.ai_personas as persona}
                <div class="p-4 rounded-lg bg-card">
                    <div class="font-medium">{persona.name}</div>
                    <div class="text-sm text-muted-foreground">ID: {persona.sender_id}</div>
                    {#if persona.voice_id}
                        <div class="text-sm text-muted-foreground">Voice ID: {persona.voice_id}</div>
                        <button
                            class="mt-2 text-sm px-2 py-1 rounded bg-primary text-primary-foreground hover:opacity-90 inline-flex items-center gap-1"
                            on:click={() => playTextToSpeech(persona.voice_id, `Hello, I am ${persona.name}. This is a test of my voice.`)}
                            disabled={loadingVoiceId !== null && loadingVoiceId !== persona.voice_id}
                        >
                            {#if loadingVoiceId === persona.voice_id}
                                <Loader2 class="w-3 h-3 animate-spin" />
                            {:else if playingAudio?.voiceId === persona.voice_id}
                                <Speaker class="w-3 h-3 animate-pulse" />
                            {:else}
                                <Speaker class="w-3 h-3" />
                            {/if}
                            Test Voice
                        </button>
                    {/if}
                </div>
            {/each}
        </div>
    </div>

    <!-- Display Messages -->
    <div class="border rounded-lg p-4 bg-muted">
        <h2 class="text-lg font-semibold mb-2">Messages</h2>
        <div class="space-y-4">
            {#each data.messages as message}
                {@const personaInfo = getPersonaInfo(message.user_id)}
                <div class="p-4 rounded-lg bg-card">
                    <div class="flex justify-between items-start">
                        <div class="font-medium">
                            {personaInfo.name}
                            {#if personaInfo.voiceId}
                                <span class="text-xs text-muted-foreground ml-2">Voice: {personaInfo.voiceId}</span>
                            {/if}
                        </div>
                        <div class="flex items-center gap-2">
                            {#if personaInfo.voiceId}
                                <button
                                    class="p-1 hover:bg-muted rounded-full transition-colors disabled:opacity-50"
                                    on:click={() => playTextToSpeech(personaInfo.voiceId, message.content)}
                                    disabled={loadingVoiceId !== null && loadingVoiceId !== personaInfo.voiceId}
                                    title={playingAudio?.voiceId === personaInfo.voiceId ? "Stop audio" : "Play text-to-speech"}
                                >
                                    {#if loadingVoiceId === personaInfo.voiceId}
                                        <Loader2 class="w-4 h-4 animate-spin" />
                                    {:else if playingAudio?.voiceId === personaInfo.voiceId}
                                        <Speaker class="w-4 h-4 animate-pulse" />
                                    {:else}
                                        <Speaker class="w-4 h-4" />
                                    {/if}
                                </button>
                            {/if}
                            <div class="text-sm text-muted-foreground">
                                {new Date(message.$createdAt).toLocaleString()}
                            </div>
                        </div>
                    </div>
                    <p class="mt-2">{message.content}</p>
                </div>
            {/each}
        </div>
    </div>
</div>
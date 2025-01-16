<script lang="ts">
    import { onMount } from 'svelte';
    import { Button } from "$lib/components/ui/button";
    import { Card } from "$lib/components/ui/card";
    import { Alert, AlertDescription } from "$lib/components/ui/alert";
    import { WhisperService } from '$lib/services/whisper';

    let transcription = '';
    let isRecording = false;
    let error = '';
    let whisperService: WhisperService;

    export let data: PageData;

    onMount(() => {
        whisperService = new WhisperService({
            minVolume: 0.04,        // 1% minimum volume
            silenceLength: 1.5,     // 1.5s silence
            translate: false        // Don't translate to English
        });

        whisperService.onTranscription((text) => {
            transcription += text + " "
        });

        whisperService.onError((err) => {
            error = err;
            isRecording = false;
        });

        return () => {
            if (isRecording) {
                whisperService.stopRecording();
            }
        };
    });

    function startRecording() {
        if (isRecording) return;
        error = '';
        transcription = '';
        isRecording = true;
        whisperService.startRecording();
    }

    function stopRecording() {
        if (!isRecording) return;
        isRecording = false;
        whisperService.stopRecording();
    }
</script>

<div class="container mx-auto p-4 space-y-6">
    <Card class="p-6">
        <div class="space-y-4">
            <div class="flex gap-4">
                <Button 
                    variant={isRecording ? "destructive" : "default"}
                    on:click={isRecording ? stopRecording : startRecording}
                >
                    {isRecording ? 'Stop Recording' : 'Start Recording'}
                </Button>
            </div>

            {#if error}
                <Alert variant="destructive">
                    <AlertDescription>
                        {error}
                    </AlertDescription>
                </Alert>
            {/if}

            <div class="border rounded-lg p-4 min-h-[200px] bg-muted">
                <h2 class="text-lg font-semibold mb-2">Live Transcription</h2>
                <p class="whitespace-pre-wrap">{transcription || 'No transcription yet. Click "Start Recording" to begin.'}</p>
            </div>

            <div class="border rounded-lg p-4 bg-muted">
                <h2 class="text-lg font-semibold mb-2">Page Data</h2>
                <pre class="whitespace-pre-wrap overflow-auto">{JSON.stringify(data.persona, null, 2)}</pre>
            </div>
        </div>
    </Card>
</div>

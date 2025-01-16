```markdown
Below is an example of how you might approach integrating the @whisper-stream Bash script into a SvelteKit application for live audio transcription. The key idea is to spawn the script on the server side (using a SvelteKit endpoint) and stream its output over Server-Sent Events (SSE) to the client. On the client side, you can display the incoming transcription in real time until the user stops recording.

---

## 1. Create a Server Endpoint for Streaming

In this example, we create a new route at src/routes/testing/stream/+server.ts that:

• Spawns the @whisper-stream script.  
• Pipes its stdout to an SSE stream.  
• Closes the stream upon script termination or if the user stops the process.

```typescript:src/routes/testing/stream/+server.ts
import type { RequestHandler } from './$types';
import { spawn } from 'child_process';

export const GET: RequestHandler = async () => {
    // Create a new readable stream for SSE
    const stream = new ReadableStream({
        start(controller) {
            // Spawn the @whisper-stream Bash script for continuous transcription
            // You may pass additional arguments, e.g. '--volume', '--translate', etc.
            const whisper = spawn('./whisper-stream', []);

            // Listen for stdout data and send SSE events
            whisper.stdout.on('data', (data) => {
                // Convert the chunk to UTF-8 text
                const text = data.toString('utf-8');

                // Each SSE message must be formatted with "data: ...\n\n"
                controller.enqueue(
                    new TextEncoder().encode(`data: ${text}\n\n`)
                );
            });

            // On error, close out the readable stream
            whisper.stderr.on('data', (err) => {
                console.error('whisper-stream error:', err.toString());
            });

            // End the stream when script finishes or is killed
            whisper.on('close', () => {
                controller.close();
            });
        }
    });

    return new Response(stream, {
        headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            Connection: 'keep-alive'
        }
    });
};
```

Notes:
1. Make sure whisper-stream is executable and in a path accessible by the server process.  
2. Adjust arguments (e.g., --oneshot, --file) to match your needs.  
3. This returns a streaming response so the client can see each new line as it arrives.

---

## 2. Frontend Integration

Below is an example Svelte page (src/routes/testing/stream/+page.svelte) that uses SvelteKit’s SSR by default but opens an EventSource on mount. It continuously receives transcription output in real time and displays it.

```svelte:src/routes/testing/stream/+page.svelte
<script lang="ts">
    import { onMount } from 'svelte';

    let transcription = '';
    let eventSource: EventSource | null = null;

    function startTranscription() {
        // Open a connection to our SSE endpoint
        eventSource = new EventSource('/testing/stream');
        eventSource.onmessage = (event) => {
            // Accumulate the incoming text
            transcription += event.data;
        };
        eventSource.onerror = (err) => {
            console.error('SSE error:', err);
        };
    }

    function stopTranscription() {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
    }

    onMount(() => {
        // Cleanup if the component is destroyed
        return () => {
            stopTranscription();
        };
    });
</script>

<div class="space-y-4 p-4">
    <button
        class="px-4 py-2 bg-primary text-primary-foreground rounded"
        on:click={startTranscription}
    >
        Start
    </button>
    <button
        class="px-4 py-2 bg-destructive text-destructive-foreground rounded"
        on:click={stopTranscription}
    >
        Stop
    </button>

    <div class="border rounded p-4 mt-4">
        <h2 class="text-lg font-bold mb-2">Live Transcription</h2>
        <p class="whitespace-pre-wrap">{transcription}</p>
    </div>
</div>
```

When the user clicks “Start,” the page creates a new EventSource connection to /testing/stream, spawns the whisper-stream process on the server (per the +server.ts file), and receives SSE data. Stop closes the connection and ends streaming.

---

## 3. Usage Notes & Next Steps

1. For local development, ensure that your server has permission to execute the whisper-stream script.  
2. If you need advanced control (e.g., sending arguments like --duration, --volume, or piping data from the browser’s microphone), you may adapt the child_process spawn arguments accordingly.  
3. You can further refine the SSE messages to handle JSON or parse specific segments if you want more structured data.  
4. For production, consider security implications (e.g., restricting script usage, validating user permissions).  

With this scaffolding in place, you can test continuously recorded audio from the server side, capture transcriptions in real time, and display them to the user until a button triggers the stop logic.

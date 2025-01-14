export async function sendMessage(
  message: string,
  workspaceId: string,
  channelId: string,
  isThread?: boolean
) {
  if (!message.trim()) return;
  
  const startTime = performance.now();
  console.log('[sendMessage] Starting message send');
  
  try {
    const fetchStartTime = performance.now();
    const response = await fetch('/api/message/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: message.trim(),
        workspaceId,
        channelId,
        isThread
      })
    });
    const fetchEndTime = performance.now();
    console.log(`[sendMessage] Network request took: ${fetchEndTime - fetchStartTime}ms`);

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const totalTime = performance.now() - startTime;
    console.log(`[sendMessage] Total client time: ${totalTime}ms`);
    return response;

  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}


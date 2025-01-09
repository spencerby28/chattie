export async function sendMessage(
  message: string,
  workspaceId: string,
  channelId: string
) {
  if (!message.trim()) return;
  
  try {
    const response = await fetch('/api/message/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: message.trim(),
        workspaceId,
        channelId
      })
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response;

  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}


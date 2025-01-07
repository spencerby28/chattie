<script lang="ts">
    import * as Drawer from "$lib/components/ui/drawer";
    import { Button } from "$lib/components/ui/button";
    import type { Message } from "$lib/types";
    import { createEventDispatcher } from "svelte";
    import { replyBoxStore } from "$lib/stores/threads";
    import { messageStore } from "$lib/stores/messages";

    const dispatch = createEventDispatcher();
    let replyContent = "";

    $: replyToMessage = $replyBoxStore.messageId ? 
        $messageStore.find(m => m.$id === $replyBoxStore.messageId) : null;

    function handleSubmit() {
        if (!replyContent.trim()) return;
        
        dispatch("reply", {
            content: replyContent,
            replyToMessageId: $replyBoxStore.messageId,
            channelId: $replyBoxStore.channelId
        });
        
        replyContent = "";
        replyBoxStore.set({
            open: false,
            messageId: '',
            channelId: ''
        });
    }

    function handleClose() {
        replyContent = "";
        replyBoxStore.set({
            open: false,
            messageId: '',
            channelId: ''
        });
    }

    // Reset content when drawer closes without submit
    function handleOpenChange(open: boolean) {
        if (!open) {
            handleClose();
        }
    }
</script>

<Drawer.Root 
    open={$replyBoxStore.open} 
    onOpenChange={handleOpenChange}
    shouldScaleBackground={true}
>
    <Drawer.Content>
        <Drawer.Header>
            <Drawer.Title>Reply to Message</Drawer.Title>
            {#if replyToMessage}
                <Drawer.Description>
                    <div class="flex gap-3 p-2 bg-gray-50 rounded-lg">
                        <img
                            src={replyToMessage.user?.avatar || '/images/avatar.png'}
                            alt=""
                            class="w-8 h-8 rounded-lg object-cover"
                        />
                        <div>
                            <div class="font-semibold text-sm">{replyToMessage.sender_name}</div>
                            <p class="text-sm text-gray-600">{replyToMessage.content}</p>
                        </div>
                    </div>
                </Drawer.Description>
            {/if}
        </Drawer.Header>

        <div class="p-4">
            <textarea
                bind:value={replyContent}
                placeholder="Type your reply..."
                class="w-full h-32 p-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
        </div>

        <Drawer.Footer class="flex justify-end gap-2">
            <Button variant="outline" on:click={handleClose}>
                Cancel
            </Button>
            <Button on:click={handleSubmit} disabled={!replyContent.trim()}>
                Reply
            </Button>
        </Drawer.Footer>
    </Drawer.Content>
</Drawer.Root>
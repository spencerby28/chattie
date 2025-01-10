<script lang="ts">
  import { page } from '$app/stores';
  import * as Command from "$lib/components/ui/command";
  import * as Popover from "$lib/components/ui/popover";
  import { Button } from "$lib/components/ui/button";
  import { Textarea } from "$lib/components/ui/textarea";
  import { cn } from "$lib/utils";
  import { ArrowRight, ArrowUp } from 'lucide-svelte';

  let message = '';
  let sending = false;
  let showMemberSearch = false;
  let searchStartIndex = -1;
  let textareaEl: HTMLTextAreaElement;
  
  // Get workspace members from page data
  $: members = ($page.data.workspace?.memberData || []).map((member: any) => ({
    id: member.id,
    name: member.name
  }));

  async function handleSubmit() {
    if (!message.trim() || sending) return;
    
    const currentMessage = message.trim();
    message = ''; // Clear immediately for better UX
    
    try {
      sending = true;
      const response = await fetch('/api/message/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: currentMessage,
          workspaceId: $page.params.workspaceId,
          channelId: $page.params.channelId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
        message = currentMessage; // Restore message if failed
      }
    } catch (error) {
      console.error('Error sending message:', error);
      message = currentMessage; // Restore message if failed
    } finally {
      sending = false;
    }
  }
  
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === '@') {
      searchStartIndex = message.length;
      showMemberSearch = true;
    } else if (event.key === 'Enter') {
      if (searchStartIndex >= 0 && !event.shiftKey) {
        event.preventDefault();
        const searchStr = message.slice(searchStartIndex + 1);
        const match = members.find(m => 
          m.name.toLowerCase().startsWith(searchStr.toLowerCase())
        );
        if (match) {
          message = message.slice(0, searchStartIndex) + `@${match.name} `;
        }
        searchStartIndex = -1;
        showMemberSearch = false;
      } else if (!event.shiftKey) {
        event.preventDefault();
        handleSubmit();
      }
    } else if (event.key === 'Escape') {
      searchStartIndex = -1;
      showMemberSearch = false;
    } else if (event.key === 'Backspace' && searchStartIndex >= 0) {
      // If we backspace past the @ symbol, close the search
      if (message.length <= searchStartIndex) {
        searchStartIndex = -1;
        showMemberSearch = false;
      }
    }
  }

  $: if (searchStartIndex >= 0) {
    const searchStr = message.slice(searchStartIndex + 1).toLowerCase();
    const filteredMembers = members.filter(m => 
      m.name.toLowerCase().includes(searchStr)
    );
    if (filteredMembers.length === 0) {
      showMemberSearch = false;
    } else {
      showMemberSearch = true; // Re-show if results exist after backspace
    }
  }
</script>

<form 
  class="relative flex items-center " 
  on:submit|preventDefault={handleSubmit}
>

  {#if showMemberSearch}
    <div class="absolute bottom-full left-0 w-full mb-2">
      <Command.Root class="w-full">
        <Command.List class="w-full">
          <Command.Empty>No members found</Command.Empty>
          {#each members.filter(m => 
            m.name.toLowerCase().includes(message.slice(searchStartIndex + 1).toLowerCase())
          ) as member}
            <Command.Item 
              value={member.name}
              onSelect={() => {
                message = message.slice(0, searchStartIndex) + `@${member.name} `;
                showMemberSearch = false;
                searchStartIndex = -1;
              }}
            >
              {member.name}
            </Command.Item>
          {/each}
        </Command.List>
      </Command.Root>
    </div>
  {/if}
  
  <Textarea
    bind:this={textareaEl}
    bind:value={message}
    on:keydown={handleKeydown}
    placeholder="Type a message... (Use @ to mention)"
    class={cn(
      "flex-1 min-h-[75px] resize-none border-2 border-gray-300",
      "focus-visible:ring-1 focus-visible:ring-offset--1"
    )}
  />
  <Button
    type="submit" 
    variant="ghost"
    disabled={!message.trim() || sending}
    class="ml-2 rounded-full bg-gray-300 hover:bg-gray-200"
  >
    <ArrowUp class="w-7 h-7" />
  </Button>
</form>
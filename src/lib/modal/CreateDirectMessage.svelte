<script lang="ts">
    import * as AlertDialog from "$lib/components/ui/alert-dialog";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import { Button } from "$lib/components/ui/button";
    import { goto } from '$app/navigation';
    import { dev } from '$app/environment';
    import { RealtimeService } from '$lib/services/realtime';
    import type { SimpleMember } from '$lib/types';

    export let open = false;
    export let selectedUserId: string | null = null;
    export let onOpenChange: (open: boolean) => void;
    export let members: SimpleMember[] = [];
    export let workspaceId: string;

    let loading = false;
    let selectedMemberIds: string[] = [];
    let showAdditionalMembers = false;

    // Get realtime service instance
    const realtime = RealtimeService.getInstance();

    $: selectedMember = members.find(m => m.id === selectedUserId);

    async function handleCreateDirectMessage(event: SubmitEvent) {
        event.preventDefault();
        loading = true;

        const formData = new FormData(event.target as HTMLFormElement);
        const additionalMemberIds = formData.getAll('selected_members') as string[];
        const message = formData.get('initial_message') as string;
        const customGroupName = formData.get('group_name') as string;

        // Include selectedUserId in memberIds if it exists
        const memberIds = selectedUserId ? [selectedUserId, ...additionalMemberIds] : additionalMemberIds;
        const memberNames = memberIds.map(id => members.find(m => m.id === id)?.name).filter(Boolean);
        const defaultGroupName = memberNames.join(' & ');

        try {
            const response = await fetch('/api/dm/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    memberNames,
                    memberIds,
                    message,
                    workspaceId,
                    groupName: memberIds.length > 1 ? (customGroupName || defaultGroupName) : defaultGroupName
                })
            });

            if (!response.ok) {
                throw new Error('Failed to create direct message');
            }

            const { channelId } = await response.json();
            
            // Close modal first
            onOpenChange(false);

            // Navigate to the new DM channel with reinitialize flag
            await goto(`/workspaces/${workspaceId}/channels/${channelId}?reinitialize=true`);
        } catch (error) {
            console.error('Error creating direct message:', error);
        } finally {
            loading = false;
        }
    }

    function handleMemberSelection(event: Event) {
        const checkbox = event.target as HTMLInputElement;
        if (checkbox.checked) {
            selectedMemberIds = [...selectedMemberIds, checkbox.value];
        } else {
            selectedMemberIds = selectedMemberIds.filter(id => id !== checkbox.value);
        }
    }
</script>

<AlertDialog.Root {open} onOpenChange={onOpenChange}>
    <AlertDialog.Content>
        <AlertDialog.Header>
            <AlertDialog.Title>New Direct Message</AlertDialog.Title>
            <AlertDialog.Description>
                Start a conversation with {selectedMember?.name}.
            </AlertDialog.Description>
        </AlertDialog.Header>

        {#if selectedMember}
            <div class="flex flex-col items-center gap-4 mb-6">
                <img
                    src={selectedMember.avatarUrl || '/images/avatar.png'}
                    alt=""
                    class="w-20 h-20 rounded-full"
                />
                <span class="text-xl font-semibold">{selectedMember.name}</span>
            </div>
        {/if}

        <form on:submit={handleCreateDirectMessage} class="space-y-6">
            <Button 
                type="button" 
                variant="outline" 
                class="w-full"
                on:click={() => showAdditionalMembers = !showAdditionalMembers}
            >
                {showAdditionalMembers ? 'Hide Additional Members' : 'Add More Members'}
            </Button>

            {#if showAdditionalMembers}
                <div class="space-y-2">
                    <Label>Select Additional Members</Label>
                    <div class="max-h-48 overflow-y-auto space-y-2 border rounded-lg p-2">
                        {#each members.filter(m => m.id !== selectedUserId) as member}
                            <label class="flex items-center text-foreground p-2 hover:bg-accent/50 rounded-lg">
                                <input
                                    type="checkbox"
                                    name="selected_members"
                                    value={member.id}
                                    class="mr-2 accent-foreground"
                                    on:change={handleMemberSelection}
                                />
                                <span class="flex items-center gap-2">
                                    <img
                                        src={member.avatarUrl || '/images/avatar.png'}
                                        alt=""
                                        class="w-6 h-6 rounded-full"
                                    />
                                    {member.name}
                                </span>
                            </label>
                        {/each}
                    </div>
                </div>
            {/if}

            {#if selectedMemberIds.length > 0}
                <div class="space-y-2">
                    <Label for="group_name">Group Name</Label>
                    <Input
                        id="group_name"
                        name="group_name"
                        placeholder="Enter group name..."
                    />
                </div>
            {/if}

            <div class="space-y-2">
                <Label for="message">Initial Message</Label>
                <textarea
                    id="initial_message"
                    name="initial_message"
                    rows="3"
                    class="w-full px-3 py-2 border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-blue-500 dark:border-gray-700"
                    placeholder="Write your first message..."
                ></textarea>
            </div>

            <AlertDialog.Footer>
                <AlertDialog.Cancel asChild>
                    <Button type="button" variant="outline" on:click={() => onOpenChange(false)}>Cancel</Button>
                </AlertDialog.Cancel>
                <Button type="submit" disabled={loading}>
                    {loading ? 'Creating...' : 'Start Conversation'}
                </Button>
            </AlertDialog.Footer>
        </form>
    </AlertDialog.Content>
</AlertDialog.Root>

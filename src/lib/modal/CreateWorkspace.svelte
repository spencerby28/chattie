<script lang="ts">
    import * as AlertDialog from "$lib/components/ui/alert-dialog";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import { Button } from "$lib/components/ui/button";
    import { goto } from '$app/navigation';
    import { dev } from '$app/environment';
    import { aiInitStore } from '$lib/stores/ai-initialization';
    import { toast } from "svelte-sonner";

    export let open = false;
    export let onOpenChange: (open: boolean) => void;

    let loading = false;
    let useAI = false;

    async function handleCreateWorkspace(event: SubmitEvent) {
        event.preventDefault();
        loading = true;

        const formData = new FormData(event.target as HTMLFormElement);
        const name = formData.get('workspace_name') as string;
        const description = formData.get('workspace_description') as string;
        const visibility = formData.get('visibility') as string;

        try {
            if (useAI) {
                aiInitStore.startInitialization();
            }

            const response = await fetch('/api/workspaces/create' + (useAI ? '?ai=true' : ''), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    description,
                    visibility
                })
            });

            if (!response.ok) {
                throw new Error('Failed to create workspace');
            }

            const { workspaceId } = await response.json();
            
            if (useAI) {
                aiInitStore.complete();
                toast.success("AI Workspace Created", {
                    description: "Your AI-powered workspace is ready!"
                });
            }

            // Close modal and navigate
            onOpenChange(false);
            await goto(`/workspaces/${workspaceId}?reinitialize=true`);
        } catch (error) {
            console.error('Error creating workspace:', error);
            if (useAI) {
                aiInitStore.reset();
            }
            toast.error("Failed to create workspace", {
                description: error instanceof Error ? error.message : "An unexpected error occurred"
            });
        } finally {
            loading = false;
        }
    }
</script>

<AlertDialog.Root {open} onOpenChange={onOpenChange}>
    <AlertDialog.Content>
        <AlertDialog.Header>
            <AlertDialog.Title>Create New Workspace</AlertDialog.Title>
            <AlertDialog.Description>
                Fill in the details below to create a new workspace.
                {#if useAI}
                <div class="mt-2 text-sm text-muted-foreground">
                    Note: AI workspace creation may take up to a minute to complete.
                </div>
                {/if}
            </AlertDialog.Description>
        </AlertDialog.Header>

        <form on:submit={handleCreateWorkspace} class="space-y-6">
            <div class="space-y-2">
                <Label for="name">Workspace Name</Label>
                <Input
                    type="text"
                    id="workspace_name"
                    name="workspace_name"
                    required
                    placeholder="Enter workspace name"
                />
            </div>

            <div class="space-y-2">
                <Label for="description">Description</Label>
                <textarea
                    id="workspace_description"
                    name="workspace_description"
                    rows="3"
                    class="w-full px-3 py-2 border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-blue-500 dark:border-gray-700"
                    placeholder="Enter workspace description"
                ></textarea>
            </div>

            <div class="space-y-2">
                <Label>Visibility</Label>
                <div class="flex gap-4">
                    <label class="flex items-center text-foreground">
                        <input
                            type="radio"
                            name="visibility"
                            value="public"
                            class="mr-2 accent-foreground"
                            checked
                        />
                        Public
                    </label>
                    <label class="flex items-center text-foreground">
                        <input
                            type="radio"
                            name="visibility"
                            value="private"
                            class="mr-2 accent-foreground"
                        />
                        Private
                    </label>
                </div>
            </div>

            <AlertDialog.Footer>
                <AlertDialog.Cancel asChild>
                    <Button type="button" variant="outline" on:click={() => onOpenChange(false)}>Cancel</Button>
                </AlertDialog.Cancel>
                {#if dev}
                    <Button type="button" variant="outline" on:click={() => useAI = !useAI} class={useAI ? "bg-primary text-primary-foreground" : ""}>
                        {useAI ? "AI Enabled" : "Try AI Feature"}
                    </Button>
                {/if}
                <Button type="submit" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Workspace'}
                </Button>
            </AlertDialog.Footer>
        </form>
    </AlertDialog.Content>
</AlertDialog.Root>

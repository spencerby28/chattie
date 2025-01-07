<script lang="ts">
	import { page } from '$app/stores';
	import * as Dialog from "$lib/components/ui/dialog";
	import { Button } from "$lib/components/ui/button";
	import { Input } from "$lib/components/ui/input";
	import { Label } from "$lib/components/ui/label";
	import { Copy, Check } from 'lucide-svelte';
	import { onMount } from 'svelte';

	export let open = false;
	export let onOpenChange: (open: boolean) => void;

	let inviteLink = '';
	let copied = false;
	let workspace = $page.data.workspace;

	onMount(async () => {
		// Generate invite link based on workspace ID
		inviteLink = `${window.location.origin}/invite/${workspace.$id}`;
	});

	async function copyInviteLink() {
		await navigator.clipboard.writeText(inviteLink);
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 2000);
	}

	async function updateWorkspaceName(event: Event) {
		const input = event.target as HTMLInputElement;
		const newName = input.value;

		try {
			const response = await fetch(`/api/workspaces/${workspace.$id}`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ name: newName }),
			});

			if (!response.ok) {
				throw new Error('Failed to update workspace name');
			}

			// Update local workspace data
			workspace = { ...workspace, name: newName };
		} catch (error) {
			console.error('Error updating workspace name:', error);
		}
	}
</script>

<Dialog.Root {open} onOpenChange={onOpenChange}>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>Workspace Settings</Dialog.Title>
			<Dialog.Description>
				Manage your workspace settings and invite members.
			</Dialog.Description>
		</Dialog.Header>

		<div class="grid gap-4 py-4">
			<div class="grid gap-2">
				<Label for="name">Workspace Name</Label>
				<Input
					id="name"
					value={workspace?.name || ''}
					on:change={updateWorkspaceName}
				/>
			</div>

			<div class="grid gap-2">
				<Label>Invite Link</Label>
				<div class="flex gap-2">
					<Input
						value={inviteLink}
						readonly
					/>
					<Button
						variant="outline"
						size="icon"
						on:click={copyInviteLink}
					>
						{#if copied}
							<Check class="h-4 w-4" />
						{:else}
							<Copy class="h-4 w-4" />
						{/if}
					</Button>
				</div>
				<p class="text-sm text-muted-foreground">
					Share this link with others to invite them to your workspace
				</p>
			</div>

			<div class="grid gap-2">
				<Label>Members ({workspace?.members?.length || 0})</Label>
				<div class="max-h-32 overflow-y-auto">
					{#each $page.data.workspace?.memberData || [] as member}
						<div class="flex items-center justify-between py-2">
							<span>{member.name}</span>
							{#if member.id === workspace?.owner}
								<span class="text-sm text-muted-foreground">Owner</span>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		</div>

		<Dialog.Footer>
			<Button variant="outline" on:click={() => onOpenChange(false)}>
				Close
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

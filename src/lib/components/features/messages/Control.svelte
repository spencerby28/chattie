<script lang="ts">
	import type { TipexEditor } from '@friendofsvelte/tipex';
	import { Loader2, Heading1, Heading2, Type, Bold, Italic, Code, AtSign } from 'lucide-svelte';
	import { cn } from '$lib/utils';
    import Button from '$lib/components/ui/button/button.svelte';
	import { buttonVariants } from '../../ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import type { SimpleMember } from '$lib/types';

	let { tipex, members = [], dropdownOpen } = $props<{
		tipex: TipexEditor;
		members: SimpleMember[];
		dropdownOpen: boolean;
	}>();

	const buttons = [
		/*
		{
			icon: Heading1,
			label: 'H1',
			isActive: () => tipex?.isActive('heading', { level: 1 }),
            // @ts-ignore
			action: () => tipex?.chain().focus().toggleHeading({ level: 1 }).run()
		},
		
		{
			icon: Heading2, 
			label: 'H2',
			isActive: () => tipex?.isActive('heading', { level: 2 }),
            // @ts-ignore
			action: () => tipex?.chain().focus().toggleHeading({ level: 2 }).run()
		},
		
		{
			icon: Type,
			label: 'P',
			isActive: () => tipex?.isActive('paragraph'),
            // @ts-ignore
			action: () => tipex?.chain().focus().setParagraph().run()
		},
		*/
		{
			icon: Bold,
			label: 'Bold',
			isActive: () => tipex?.isActive('bold'),
            // @ts-ignore
			action: () => tipex?.chain().focus().toggleBold().run()
		},
		{
			icon: Italic,
			label: 'Italic', 
			isActive: () => tipex?.isActive('italic'),
            // @ts-ignore
			action: () => tipex?.chain().focus().toggleItalic().run()
		},
		/*
		{
			icon: Code,
			label: 'Code',
			isActive: () => tipex?.isActive('code'),
            // @ts-ignore
			action: () => tipex?.chain().focus().toggleCode().run()
		}
			*/
	];

	function insertMention(member: SimpleMember) {
		tipex?.chain()
			.focus()
			.insertContent({
				type: 'mention',
				attrs: {
					id: member.id,
					name: member.name
				}
			})
			.run();
	}
</script>

<div class="flex gap-4">
	{#each buttons as button}
		<Button
			on:click={button.action}
			class={cn(
				buttonVariants({ 
					variant: button.isActive() ? "default" : "outline",
					size: "sm"
				}),
				"hover:bg-gradient-to-r hover:from-blue-400/60 hover:to-purple-600/60"
			)}
			title={button.label}
			type="button"
		>
			<svelte:component 
				this={button.icon} 
				class={cn(
					"h-4 w-4",
					button.isActive() ? "" : "invert"
				)}
			/>
		</Button>
	{/each}
<!--
	<DropdownMenu.Root bind:onOpenChange={dropdownOpen}>
		<DropdownMenu.Trigger>
			<Button
				class={cn(
					buttonVariants({ 
						variant: "outline",
						size: "sm"
					}),
					"hover:bg-gradient-to-r hover:from-blue-400/60 hover:to-purple-600/60"
				)}
				title="Mention"
				type="button"
			>
				<AtSign class="h-4 w-4 invert" />
			</Button>
		</DropdownMenu.Trigger>
		<DropdownMenu.Content>
			{#each members as member}
				<DropdownMenu.Item on:click={() => insertMention(member)}>
					{member.name}
				</DropdownMenu.Item>
			{/each}
		</DropdownMenu.Content>
	</DropdownMenu.Root>
	-->
</div>

<style>
	:global(.ProseMirror .mention) {
		color: rgb(59 130 246);
		cursor: pointer;
		display: inline-block;
		background: rgba(59, 130, 246, 0.1);
		border-radius: 4px;
		padding: 0 4px;
	}
</style>
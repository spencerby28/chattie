<script lang="ts">
	import type { TipexEditor } from '@friendofsvelte/tipex';
	import { Loader2, Heading1, Heading2, Type, Bold, Italic, Code, AtSign, Paperclip, Mic, MicOff } from 'lucide-svelte';
	import { cn } from '$lib/utils';
    import Button from '$lib/components/ui/button/button.svelte';
	import { buttonVariants } from '../../ui/button';
	import type { SimpleMember } from '$lib/types';

	let { tipex, members = [], dropdownOpen, onFileUpload, isRecording = false, onRecordingToggle } = $props<{
		tipex: TipexEditor;
		members: SimpleMember[];
		dropdownOpen: boolean;
		onFileUpload: () => void;
		isRecording?: boolean;
		onRecordingToggle?: () => void;
	}>();

	$effect(() => {
		console.log('Dropdown open state changed:', dropdownOpen);
	});

	const buttons = [
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
		}
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

	function triggerMention() {
		console.log('Triggering mention with editor:', tipex);
		tipex?.chain()
			.focus()
			.insertContent('@')
			.run();
		tipex?.commands.insertContent(' ');
		tipex?.commands.moveLeft(1);
		console.log('Mention triggered, editor state:', tipex?.getJSON());
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

	<Button
		on:click={onFileUpload}
		class={cn(
			buttonVariants({ 
				variant: "outline",
				size: "sm"
			}),
			"hover:bg-gradient-to-r hover:from-blue-400/60 hover:to-purple-600/60"
		)}
		title="Upload File"
		type="button"
	>
		<Paperclip class="h-4 w-4 invert" />
	</Button>

	<Button
		on:click={onRecordingToggle}
		class={cn(
			buttonVariants({ 
				variant: "outline",
				size: "sm"
			}),
			"hover:bg-gradient-to-r hover:from-blue-400/60 hover:to-purple-600/60",
			isRecording && "relative ring-2 ring-white after:absolute after:inset-[-2px] after:animate-pulse after:ring-2 after:ring-white after:rounded-md"
		)}
		title={isRecording ? "Stop Recording" : "Start Recording"}
		type="button"
	>
		<svelte:component this={isRecording ? Mic : MicOff} class="h-4 w-4 invert relative z-10" />
	</Button>

	<Button
		on:click={triggerMention}
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
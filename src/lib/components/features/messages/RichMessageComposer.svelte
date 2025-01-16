<script lang="ts">
	import { Tipex, defaultExtensions } from '@friendofsvelte/tipex';
	import type { Editor } from '@tiptap/core';
	import { cn } from '$lib/utils';
	import { Extension } from '@tiptap/core';
	import { Button } from "$lib/components/ui/button";
	import Control from '$lib/components/features/messages/Control.svelte';
	import { Node } from '@tiptap/core';
	import * as HoverCard from '$lib/components/ui/hover-card';
	import type { EditorView } from '@tiptap/pm/view';
	import { Plugin } from '@tiptap/pm/state';
	import { sendMessage } from './sendMessage';
	import { page } from '$app/stores';
	import type { SimpleMember } from '$lib/types';
	import UploadFile from '$lib/modal/UploadFile.svelte';
	import { Extension as TiptapExtension } from '@tiptap/core';
	import type { SuggestionOptions } from '@tiptap/suggestion';
	import suggestion from '@tiptap/suggestion';
	import { memberStore } from '$lib/stores/members';
	import * as Command from "$lib/components/ui/command";
	import * as Popover from "$lib/components/ui/popover";
	import { WhisperService } from '$lib/services/whisper';
	import { Loader2 } from 'lucide-svelte';
	import { onMount } from 'svelte';

	//import '@friendofsvelte/tipex/styles/Tipex.css';
	//import '@friendofsvelte/tipex/styles/ProseMirror.css';
	import '@friendofsvelte/tipex/styles/CodeBlock.css';
	import '$lib/components/features/messages/RenderStyles.css';

	let dropdownOpen = $state(false);
	let fileUploadOpen = $state(false);
	let members = $derived($memberStore); 
	let workspaceId = $derived($page.params.workspaceId);
	let channelId = $derived($page.params.channelId);
	let suggestionPopoverOpen = $state(false);
	let slashCommandPopoverOpen = $state(false);
	let isRecording = $state(false);
	let isProcessing = $state(false);
	let whisperService: WhisperService;
	let error = $state('');

	// Check if we're in a thread from URL params
	let isThread = $derived(new URLSearchParams($page.url.search).get('thread') === 'true');
	
	let body = ''
	let editor: Editor | undefined = $state();
	let currentRange: any = null;

	const htmlContent = $derived(editor?.getHTML());

	$effect(() => {
		console.log('Members updated:', members);
	});

	// Create suggestion plugin
	const suggestionConfig: Partial<SuggestionOptions> = {
		char: '@',
		command: ({ editor, range, props }) => {
			console.log('Mention command called with props:', props);
			editor
				.chain()
				.focus()
				.insertContentAt(range, [
					{
						type: 'mention',
						attrs: props
					}
				])
				.run();
			suggestionPopoverOpen = false;
		},
		allow: ({ editor, range }) => {
			console.log('Checking if mention is allowed at range:', range);
			return true;
		},
		items: ({ query }: { query: string }) => {
			console.log('Filtering members with query:', query);
			console.log('Available members:', members);
			return members.filter(member => 
				member.name.toLowerCase().includes(query.toLowerCase())
			);
		},
		render: () => {
			return {
				onStart: (props: any) => {
					console.log('Suggestion started with props:', props);
					suggestionPopoverOpen = true;
					currentRange = props.range;
					currentQuery = props.query || '';
					
					return () => {
						suggestionPopoverOpen = false;
						currentQuery = '';
					};
				},
				onUpdate: (props: any) => {
					currentRange = props.range;
					currentQuery = props.query || '';
				},
				onKeyDown: (props: any) => {
					if (props.event.key === 'Enter' && filteredMembers.length > 0) {
						handleMemberSelect(filteredMembers[0]);
						return true;
					}
					return false;
				},
				onExit: () => {
					suggestionPopoverOpen = false;
					currentQuery = '';
				},
			};
		},
	};

	const slashCommandConfig: Partial<SuggestionOptions> = {
		char: '/',
		command: ({ editor, range, props }) => {
			console.log('Slash command called with props:', props);
			// Handle slash command execution
			slashCommandPopoverOpen = false;
		},
		allow: ({ editor, range }) => {
			console.log('Checking if slash command is allowed at range:', range);
			return true;
		},
		items: ({ query }: { query: string }) => {
			const commands = [
				{ name: 'summarize', description: 'Summarize the conversation history' },
				{ name: 'analyze', description: 'Analyze the sentiment and key topics' },
				{ name: 'chat', description: 'Start a conversation with the AI assistant' }
			];
			return commands.filter(cmd => 
				cmd.name.toLowerCase().includes(query.toLowerCase())
			);
		},
		render: () => {
			return {
				onStart: (props: any) => {
					console.log('Slash command started with props:', props);
					slashCommandPopoverOpen = true;
					currentRange = props.range;
					currentQuery = props.query || '';
					
					return () => {
						slashCommandPopoverOpen = false;
						currentQuery = '';
					};
				},
				onUpdate: (props: any) => {
					currentRange = props.range;
					currentQuery = props.query || '';
				},
				onKeyDown: (props: any) => {
					if (props.event.key === 'Enter') {
						// Handle command selection
						return true;
					}
					return false;
				},
				onExit: () => {
					slashCommandPopoverOpen = false;
					currentQuery = '';
				},
			};
		},
	};

	// Add currentQuery state
	let currentQuery = $state('');
	let filteredMembers = $derived(
		members
			.filter(member => {
				// Filter out current user
				if (member.id === $page.data.user?.$id) return false;
				
				// Check if name matches query
				if (!member.name.toLowerCase().includes(currentQuery.toLowerCase())) return false;
				
				// Check if member is already mentioned
				if (editor) {
					const content = editor.getJSON();
					const existingMentions = findMentionsInContent(content);
					if (existingMentions.includes(member.id)) return false;
				}
				
				return true;
			})
	);

	// Add helper function to find mentions in content
	function findMentionsInContent(content: any): string[] {
		const mentions: string[] = [];
		
		function traverse(node: any) {
			if (node.type === 'mention' && node.attrs?.id) {
				mentions.push(node.attrs.id);
			}
			if (node.content) {
				node.content.forEach(traverse);
			}
		}
		
		if (content.content) {
			content.content.forEach(traverse);
		}
		
		return mentions;
	}

	// Create mention suggestion extension
	const MentionSuggestion = TiptapExtension.create({
		name: 'mention-suggestion',
		addOptions() {
			return {
				suggestion: {
					...suggestionConfig,
					editor: null as any,
				},
			}
		},
		addProseMirrorPlugins() {
			return [
				suggestion({
					...this.options.suggestion,
					editor: this.editor,
				}),
			]
		},
	});

	// Create slash command suggestion extension
	const SlashCommandSuggestion = TiptapExtension.create({
		name: 'slash-command-suggestion',
		addOptions() {
			return {
				suggestion: {
					...slashCommandConfig,
					editor: null as any,
				},
			}
		},
		addProseMirrorPlugins() {
			return [
				suggestion({
					...this.options.suggestion,
					editor: this.editor,
				}),
			]
		},
	});

	function handleMemberSelect(member: SimpleMember) {
		if (!editor || !currentRange) return;
		
		editor
			.chain()
			.focus()
			.insertContentAt(currentRange, [
				{
					type: 'mention',
					attrs: {
						id: member.id,
						name: member.name
					}
				}
			])
			.run();
			
		suggestionPopoverOpen = false;
	}

	// Create custom extension to handle Enter key
	const CustomKeymap = Extension.create({
		name: 'customKeymap',

		addKeyboardShortcuts() {
			return {
				Enter: () => {
					if (!this.editor) return false;

					// Only handle Enter if Shift is not pressed
					if (this.editor.view.state.selection.$head.parentOffset === 0) {
						return false;
					}

					const content = this.editor.getHTML();
					handleSend(content);

					// Return true to prevent default Enter behavior
					return true;
				}
			};
		}
	});

	// Create mention node extension
	const MentionNode = Node.create({
		name: 'mention',
		group: 'inline',
		inline: true,
		selectable: false,
		atom: true,

		addAttributes() {
			return {
				id: {
					default: null
				},
				name: {
					default: null
				}
			}
		},

		parseHTML() {
			return [
				{
					tag: 'span[data-mention-id]',
					getAttrs: element => {
						if (typeof element === 'string') return false;
						if (!(element instanceof HTMLElement)) return false;
						return {
							id: element.getAttribute('data-mention-id'),
							name: element.getAttribute('data-mention-name')
						}
					}
				}
			]
		},

		renderHTML({ node }) {
			return [
				'span',
				{
					'data-mention-id': node.attrs.id,
					'data-mention-name': node.attrs.name,
					class: 'mention',
					'data-mention': 'true'
				},
				`@${node.attrs.name}`
			]
		}
	});


	// Add custom extensions to default extensions
	const extensions = [
		...defaultExtensions,
		CustomKeymap,
		MentionNode,
	//	SlashCommandSuggestion,
		MentionSuggestion,
	];

	function handleSend(content?: string) {
		console.log('handleSend called with content:', content);
		
		// If content is passed directly and it's a simple paragraph
		if (content && content.startsWith('<p>') && content.endsWith('</p>')) {
			const innerText = content.slice(3, -4);
			// Check if there are any HTML tags inside
			if (!/<[^>]*>/.test(innerText)) {
				content = innerText;
			}
		}
		// If no direct content, get from editor
		else if (!content && editor) {
			console.log('No content passed, getting from editor');
			const html = editor.getHTML();
			const text = editor.getText();
			
			if (html === `<p>${text}</p>`) {
				content = text;
			} else {
				content = html;
			}
		}

		if (content?.trim()) {
			// If we're in a thread, pass the threadId from URL params
			// The channelId is always the current channel, even for threads
			sendMessage(content, $page.params.workspaceId, $page.params.channelId, isThread);
			editor?.commands.clearContent();
		}
	}

	onMount(() => {
		whisperService = new WhisperService({
			minVolume: 0.04,        // 4% minimum volume
			silenceLength: 1.5,     // 1.5s silence
			translate: false        // Don't translate to English
		});

		whisperService.onTranscription((text) => {
			if (editor && text.trim()) {
				const currentContent = editor.getText();
				if (currentContent) {
					editor.commands.insertContent(' ' + text);
				} else {
					editor.commands.setContent(text);
				}
			}
			isProcessing = false;
		});

		whisperService.onError((err) => {
			error = err;
			isRecording = false;
			isProcessing = false;
		});

		return () => {
			if (isRecording) {
				whisperService.stopRecording();
				isProcessing = false;
			}
		};
	});

	function handleRecordingToggle() {
		if (isRecording) {
			whisperService.stopRecording();
			isRecording = false;
			// Don't set processing here - it will be set when the actual API request is made
		} else {
			error = '';
			isRecording = true;
			whisperService.startRecording();
		}
	}

</script>
<div class="w-full flex flex-col">
	<div class="relative w-full">
		<Tipex
			{body}
			{extensions}
			bind:tipex={editor}
			class={cn(
				// Base styles
				'min-h-[120x] resize-none bg-muted relative border-t-2 border-border transition-all duration-300 outline-none',
				// Override ALL focus and outline states
				'[&.focused.focal]:ring-0 [&.focused.focal]:ring-offset-0 [&.focused.focal]:border-transparent [&.focused.focal]:outline-none',
				'[&.focused]:transition-all [&.focused]:duration-300 [&.focused]:translate-y-[-2px] [&.focused]:shadow-lg [&]:outline-none',
				'[&_.ProseMirror]:outline-none [&_.ProseMirror]:focus:outline-none',
				'[&_.tipex-editor-section]:outline-none [&_.tipex-editor-section]:focus:outline-none',
				// Editor section styles
				'[&_.tipex-editor-section]:px-3 [&_.tipex-editor-section]:pt-4 [&_.tipex-editor-section]:bg-background [&_.tipex-editor-section]:h-[110px]',
				'[&_.ProseMirror]:text-foreground [&_.ProseMirror_p]:m-0 [&_.ProseMirror]:h-full',
				// Controls section
				'[&_.tipex-controls]:bg-gradient-to-r [&_.tipex-controls]:from-blue-400/60 [&_.tipex-controls]:to-purple-600/60 [&_.tipex-controls]:border-t [&_.tipex-controls]:border-border [&_.tipex-controls]:outline-none',
				// Utility button styles
				'[&_.tipex-edit-button]:bg-muted [&_.tipex-edit-button]:text-accent-foreground',
				'[&_.tipex-edit-button]:px-2 [&_.tipex-edit-button]:py-2 [&_.tipex-edit-button]:rounded-md',
				'[&_.tipex-edit-button]:disabled:opacity-50 [&_.tipex-edit-button]:outline-none',
				'[&_.tipex-button-extra]:ml-2',
				// Controller styles
				'[&_.tipex-controller]:bg-gradient-to-r [&_.tipex-controller]:from-blue-400/60 [&_.tipex-controller]:to-purple-600/60 [&_.tipex-controller]:border-t [&_.tipex-controller]:border-border [&_.tipex-controller]:outline-none',
				'[&_.tipex-controller]:p-2 [&_.tipex-controller]:flex [&_.tipex-controller]:items-center',
				'[&_.tipex-controller]:justify-between',
				'[&_.tipex-basic-controller-wrapper]:h-0 [&_.tipex-basic-controller-wrapper]:flex [&_.tipex-basic-controller-wrapper]:items-center [&_.tipex-basic-controller-wrapper]:justify-center'
			)}
		>
			{#snippet foot(tipex)}
				{#if tipex?.isFocused || dropdownOpen}
					<!--svelte-ignore a11y_no_static_element_interactions-->
					<div 
						class="flex items-center justify-between px-2 py-2 bg-gradient-to-r from-blue-400/60 to-purple-600/60"
						onmousedown={(e) => e.preventDefault()}
					>
						<div class="flex items-center gap-4">
							<Control 
								{tipex} 
								{members} 
								{dropdownOpen}
								{isRecording}
								onRecordingToggle={handleRecordingToggle}
								onFileUpload={() => fileUploadOpen = true}
							/>
							{#if isProcessing}
								<div class="flex items-center gap-2 text-sm text-muted-foreground">
									<Loader2 class="h-4 w-4 animate-spin" />
									Processing...
								</div>
							{/if}
							{#if error}
								<div class="text-sm text-destructive">
									{error}
								</div>
							{/if}
						</div>
						<Button
							on:click={() => handleSend()}
							class="bg-black text-white hover:bg-black/90 mr-4"
							disabled={!tipex?.getText()?.trim()}
						>
							Send Message
						</Button>
					</div>
				{/if}
			{/snippet}
		</Tipex>

		{#if suggestionPopoverOpen}
			<div 
				class="absolute left-0 bottom-full z-50 border border-border bg-background text-foreground shadow-md rounded-md mx-3 p-2 mb-1 min-w-[200px] w-fit"
			>
				<div class="text-xs font-semibold text-muted-foreground mb-2 px-2">MENTION:</div>
				{#if filteredMembers.length === 0}
					<div class="p-2 text-sm text-muted-foreground">
						No members found
					</div>
				{:else}
					<div class="max-h-[180px] overflow-y-auto">
						{#each filteredMembers as member}
							<button
								class="w-full text-left px-2 py-1.5 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground flex items-center gap-2 transition-colors whitespace-nowrap"
								onmousedown={(e) => {
									e.preventDefault(); // Prevent focus loss
									handleMemberSelect(member);
								}}
							>
								{#if member.bot}
									<div class="flex items-center bg-gradient-to-r from-blue-400/60 to-purple-600/60 text-white rounded px-2 py-0.5">
										<span class="text-[10px] font-medium mr-1.5 text-foreground">AI</span>
										<span class="text-sm">{member.name}</span>
									</div>
								{:else if member.id === 'bot'}
									<div class="flex items-center bg-chattie-bg text-foreground rounded px-2 py-0.5 ring-1 ring-border">
										<span class="text-[10px] font-medium mr-1.5 text-foreground">AI</span>
										<span class="text-sm text-foreground">{member.name}</span>
									</div>
								{:else}
									<span class="flex-1">{member.name}</span>
								{/if}
							</button>
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		{#if slashCommandPopoverOpen}
			<div 
				class="absolute left-0 bottom-full z-50 border border-border bg-background text-foreground shadow-md rounded-md mx-3 p-2 mb-1 min-w-[200px] w-fit"
			>
				<div class="text-xs font-semibold text-muted-foreground mb-2 px-2">COMMANDS:</div>
				<div class="max-h-[180px] overflow-y-auto">
					<button
						class="w-full text-left px-2 py-1.5 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground flex items-center gap-2 transition-colors whitespace-nowrap"
						onmousedown={(e) => {
							e.preventDefault();
							// Handle command select
						}}
					>
						<div class="flex flex-col">
							<span class="font-medium">/summarize</span>
							<span class="text-xs text-muted-foreground">Summarize the conversation history</span>
						</div>
					</button>
					<button
						class="w-full text-left px-2 py-1.5 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground flex items-center gap-2 transition-colors whitespace-nowrap"
						onmousedown={(e) => {
							e.preventDefault();
							// Handle command select
						}}
					>
						<div class="flex flex-col">
							<span class="font-medium">/analyze</span>
							<span class="text-xs text-muted-foreground">Analyze the sentiment and key topics</span>
						</div>
					</button>
					<button
						class="w-full text-left px-2 py-1.5 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground flex items-center gap-2 transition-colors whitespace-nowrap"
						onmousedown={(e) => {
							e.preventDefault();
							// Handle command select
						}}
					>
						<div class="flex flex-col">
							<span class="font-medium">/chat</span>
							<span class="text-xs text-muted-foreground">Start a conversation with the AI assistant</span>
						</div>
					</button>
				</div>
			</div>
		{/if}
	</div>
</div>

<UploadFile
	bind:open={fileUploadOpen}
	onOpenChange={(open) => fileUploadOpen = open}
	{channelId}
	{workspaceId}
/>



<style>
	:global(.ProseMirror .mention) {
		color: rgb(59 130 246);
		cursor: pointer;
		display: inline-block;
		background: rgba(59, 130, 246, 0.1);
		border-radius: 4px;
		padding: 0 4px;
	}

	:global(.hover-card) {
		z-index: 1000;
	}

	:global(.tipex-editor) {
		border-radius: 0 !important;
		transform: translateY(0);
		transition: all 0.3s ease;
	}

	:global(.tipex-editor.focused) {
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
		transform: translateY(-2px);
	}

	:global(.tipex-editor-section) {
		border-radius: 0 !important;
	}

	:global(.mention-suggestion-list) {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		z-index: 1000;
	}

	:global(.mention-suggestion-list button) {
		transition: all 0.2s ease;
	}

	:global(.mention-suggestion-list button:hover) {
		transform: translateX(2px);
	}
</style>

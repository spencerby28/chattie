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
	
	//import '@friendofsvelte/tipex/styles/Tipex.css';
	//import '@friendofsvelte/tipex/styles/ProseMirror.css';
	import '@friendofsvelte/tipex/styles/CodeBlock.css';
	import '$lib/components/features/messages/RenderStyles.css';

	let dropdownOpen = $state(false);
	let members = $derived(($page.data.workspace?.memberData || []) as SimpleMember[]); 
	
	let body = '';
	let editor: Editor | undefined = $state();
	let activeHoverMember: { id: string; name: string } | null = $state(null);
	let hoverCardAnchor: HTMLElement | null = $state(null);

	const htmlContent = $derived(editor?.getHTML());

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

	// Create extension to handle mention hover events
	const MentionHoverExtension = Extension.create({
		name: 'mentionHover',

		addProseMirrorPlugins() {
			return [
				new Plugin({
					props: {
						handleDOMEvents: {
							mouseover(view: EditorView, event: MouseEvent) {
								const target = event.target as HTMLElement;
								if (target.hasAttribute('data-mention')) {
									const id = target.getAttribute('data-mention-id');
									const name = target.getAttribute('data-mention-name');
									if (id && name) {
										activeHoverMember = { id, name };
										hoverCardAnchor = target;
									}
								}
								return false;
							},
							mouseout(view: EditorView, event: MouseEvent) {
								const target = event.target as HTMLElement;
								if (target.hasAttribute('data-mention')) {
									setTimeout(() => {
										if (!document.querySelector('.hover-card:hover')) {
											activeHoverMember = null;
											hoverCardAnchor = null;
										}
									}, 100);
								}
								return false;
							}
						}
					}
				})
			];
		}
	});

	// Add custom extensions to default extensions
	const extensions = [
		...defaultExtensions,
		CustomKeymap,
		MentionNode,
		MentionHoverExtension
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
			console.log('Editor HTML:', html);
			console.log('Editor Text:', text);
			
			if (html === `<p>${text}</p>`) {
				content = text;
				console.log('Using plain text:', content);
			} else {
				content = html;
				console.log('Using HTML:', content);
			}
		}

		if (content?.trim()) {
			console.log('Final message to send:', content);
			sendMessage(content, $page.params.workspaceId, $page.params.channelId);
			editor?.commands.clearContent();
		}
	}

	function handleMentionClick(id: string | undefined) {
		if (!id) return;
		console.log('Opening DM with user:', id);
		activeHoverMember = null;
		hoverCardAnchor = null;
	}
</script>

<div class="w-full flex flex-col">
	<Tipex
		{body}
		{extensions}
		bind:tipex={editor}
		class={cn(
			// Base styles
			'min-h-[120x] resize-none bg-muted relative border-t-2 border-border transition-none outline-none',
			// Override ALL focus and outline states
			'[&.focused.focal]:ring-0 [&.focused.focal]:ring-offset-0 [&.focused.focal]:border-transparent [&.focused.focal]:outline-none',
			'[&.focused]:transition-none [&]:transition-none [&]:outline-none',
			'[&_.ProseMirror]:outline-none [&_.ProseMirror]:focus:outline-none',
			'[&_.tipex-editor-section]:outline-none [&_.tipex-editor-section]:focus:outline-none',
			// Editor section styles
			'[&_.tipex-editor-section]:px-3 [&_.tipex-editor-section]:pt-4 [&_.tipex-editor-section]:bg-background [&_.tipex-editor-section]:h-[110px]',
			'[&_.ProseMirror]:text-foreground [&_.ProseMirror_p]:m-0 [&_.ProseMirror]:h-full',
			// Controls section
			'[&_.tipex-controls]:bg-muted [&_.tipex-controls]:border-t [&_.tipex-controls]:border-border [&_.tipex-controls]:outline-none',
			// Utility button styles
			'[&_.tipex-edit-button]:bg-muted [&_.tipex-edit-button]:text-accent-foreground',
			'[&_.tipex-edit-button]:px-2 [&_.tipex-edit-button]:py-2 [&_.tipex-edit-button]:rounded-md',
			'[&_.tipex-edit-button]:disabled:opacity-50 [&_.tipex-edit-button]:outline-none',
			'[&_.tipex-button-extra]:ml-2',
			// Controller styles
			'[&_.tipex-controller]:bg-inherit [&_.tipex-controller]:border-t [&_.tipex-controller]:border-border [&_.tipex-controller]:outline-none',
			'[&_.tipex-controller]:p-2 [&_.tipex-controller]:flex [&_.tipex-controller]:items-center',
			'[&_.tipex-controller]:justify-between',
			'[&_.tipex-basic-controller-wrapper]:h-0 [&_.tipex-basic-controller-wrapper]:flex [&_.tipex-basic-controller-wrapper]:items-center [&_.tipex-basic-controller-wrapper]:justify-center'
		)}
	>
		{#snippet head(tipex)}
			{#if tipex?.isFocused|| dropdownOpen}
				<!--svelte-ignore a11y_no_static_element_interactions-->
				<div 
					class="flex items-center justify-between px-2 py-2"
					onmousedown={(e) => e.preventDefault()}
				>
					<Control {tipex} {members} {dropdownOpen} />
					<Button
						on:click={() => handleSend()}
						class="hover:bg-gradient-to-r hover:from-blue-400/60 hover:to-purple-600/60 mr-4"
						disabled={!tipex?.getText()?.trim()}
					>
						Send Message
					</Button>
				</div>
			{/if}
		{/snippet}
	</Tipex>
</div>

{#if activeHoverMember && hoverCardAnchor}
	<HoverCard.Root open={true}>
		<HoverCard.Trigger asChild>
			<div class="fixed opacity-0" style="pointer-events: none;">
				{@html hoverCardAnchor.outerHTML}
			</div>
		</HoverCard.Trigger>
		<HoverCard.Content
			class="w-80 hover-card"
			style="position: fixed; top: {hoverCardAnchor.getBoundingClientRect().bottom + 5}px; left: {hoverCardAnchor.getBoundingClientRect().left}px;"
		>
			<div class="flex justify-between space-x-4">
				<div class="space-y-1">
					<h4 class="text-sm font-semibold">{activeHoverMember.name}</h4>
					<div class="flex items-center pt-2">
						<button
							class="text-xs text-blue-500 hover:text-blue-600"
							onclick={() => handleMentionClick(activeHoverMember?.id)}
						>
							Send direct message
						</button>
					</div>
				</div>
			</div>
		</HoverCard.Content>
	</HoverCard.Root>
{/if}

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
	}

	:global(.tipex-editor-section) {
		border-radius: 0 !important;
	}

	:global(.tipex-editor::before) {
		content: '';
		position: absolute;
		left: 0;
		right: 0;
		top: 0;
		height: 3px;
		z-index: 100;
		opacity: 0;
		background: linear-gradient(
			90deg,
			rgb(96 165 250) 0%,
			rgb(129 140 248) 20%,
			rgb(147 51 234) 50%,
			rgb(129 140 248) 80%,
			rgb(96 165 250) 100%
		);
		background-size: 300% 100%;
		animation: gradient 3s ease infinite;
	}

	:global(.tipex-editor.focused::before) {
		opacity: 1;
	}

	@keyframes gradient {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}
</style>

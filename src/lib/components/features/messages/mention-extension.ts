import { Extension } from '@tiptap/core';
import type { SimpleMember } from '$lib/types';
import MentionHoverCard from './MentionHoverCard.svelte';

export const MentionExtension = Extension.create({
  name: 'mention',

  addProseMirrorPlugins() {
    return [
      {
        props: {
          handleDOMEvents: {
            mouseover(view, event) {
              const target = event.target as HTMLElement;
              if (target.classList.contains('mention')) {
                const member: SimpleMember = {
                  id: target.dataset.mentionId || '',
                  name: target.dataset.mentionName || ''
                };

                // Create hover card component
                const hoverCard = new MentionHoverCard({
                  target: document.createElement('div'),
                  props: { member }
                });

                // Position and show hover card
                const rect = target.getBoundingClientRect();
                const hoverCardEl = hoverCard.$$.root as HTMLElement;
                hoverCardEl.style.position = 'fixed';
                hoverCardEl.style.top = `${rect.bottom + 5}px`;
                hoverCardEl.style.left = `${rect.left}px`;
                document.body.appendChild(hoverCardEl);

                // Remove hover card when mouse leaves
                const removeHoverCard = () => {
                  hoverCard.$destroy();
                  target.removeEventListener('mouseleave', removeHoverCard);
                };
                target.addEventListener('mouseleave', removeHoverCard);
              }
              return false;
            }
          }
        }
      }
    ];
  }
}); 
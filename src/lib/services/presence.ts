import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
import { presenceStore } from '$lib/stores/presence';
import { page } from '$app/stores';
import { get } from 'svelte/store';

interface CustomStatus {
    emoji?: string;
    text?: string;
}

type BaseStatus = 'online' | 'offline' | 'away';

export class PresenceService {
    private static instance: PresenceService;
    private pulseInterval: NodeJS.Timeout | null = null;
    private userId: string | null = null;
    private currentCustomStatus: CustomStatus | null = null;
    private client: ReturnType<typeof createBrowserClient> | null = null;

    private constructor() {
        // console.log('[PresenceService] Creating new instance');
        this.client = createBrowserClient();
    }

    static getInstance() {
        if (!PresenceService.instance) {
            PresenceService.instance = new PresenceService();
        }
        return PresenceService.instance;
    }

    async initialize(userId: string) {
        // console.log('[PresenceService] Initializing for user:', userId);
        this.userId = userId;
        
        try {
            // console.log('[PresenceService] Creating initial presence document');
            const doc = await this.client?.databases.createDocument(
                'main',
                'presence',
                userId,
                {
                    userId,
                    baseStatus: 'online',
                    customStatus: null,
                    lastSeen: new Date().toISOString(),
                    workspaceId: get(page).params.workspaceId
                }
            );
            // console.log('[PresenceService] Created initial presence document:', doc);
        } catch (error: any) {
            // If document already exists, that's fine
            if (error.code !== 409) {
                // console.error('[PresenceService] Error creating presence document:', error);
            } else {
                // console.log('[PresenceService] Presence document already exists');
            }
        }

        // Start sending pulses
        // console.log('[PresenceService] Starting pulse check');
        this.startPulseCheck();

        // Set initial status
        // console.log('[PresenceService] Setting initial online status');
        await this.updateStatus('online');
    }

    private startPulseCheck() {
        // console.log('[PresenceService] Setting up pulse interval');
        if (this.pulseInterval) {
            // console.log('[PresenceService] Clearing existing pulse interval');
            clearInterval(this.pulseInterval);
        }

        this.pulseInterval = setInterval(async () => {
            if (!this.userId) {
                // console.warn('[PresenceService] No userId for pulse check');
                return;
            }
            
            try {
                // console.log('[PresenceService] Sending pulse');
                await this.sendPulse();
            } catch (error) {
                // console.error('[PresenceService] Failed to send pulse:', error);
            }
        }, 10000); // Every 10 seconds
    }

    private async sendPulse() {
        if (!this.userId || !this.client) {
            // console.warn('[PresenceService] Missing userId or client for pulse');
            return;
        }

        const data = {
            userId: this.userId,
            baseStatus: 'online',
            customStatus: this.currentCustomStatus,
            lastSeen: new Date().toISOString(),
            workspaceId: get(page).params.workspaceId
        };

        // console.log('[PresenceService] Sending pulse with data:', data);

        try {
            const response = await this.client.databases.updateDocument(
                'main',
                'presence',
                this.userId,
                data
            );
            // console.log('[PresenceService] Pulse sent successfully:', response);
        } catch (error: any) {
            // console.error('[PresenceService] Error sending pulse:', error);
            // If document doesn't exist, create it
            if (error.code === 404) {
                // console.log('[PresenceService] Document not found, creating new one');
                try {
                    const newDoc = await this.client.databases.createDocument(
                        'main',
                        'presence',
                        this.userId,
                        data
                    );
                    // console.log('[PresenceService] Created new presence document:', newDoc);
                } catch (createError) {
                    // console.error('[PresenceService] Error creating presence document:', createError);
                }
            }
        }
    }

    async updateStatus(baseStatus: BaseStatus, customStatus?: CustomStatus) {
        if (!this.userId || !this.client) {
            // console.warn('[PresenceService] Missing userId or client for status update');
            return;
        }

        // console.log('[PresenceService] Updating status:', { baseStatus, customStatus });
        this.currentCustomStatus = customStatus || null;

        const data = {
            userId: this.userId,
            baseStatus,
            customStatus: this.currentCustomStatus,
            lastSeen: new Date().toISOString(),
            workspaceId: get(page).params.workspaceId
        };

        try {
            const response = await this.client.databases.updateDocument(
                'main',
                'presence',
                this.userId,
                data
            );
            // console.log('[PresenceService] Status updated successfully:', response);

            // Update local store
            presenceStore.updateStatus(this.userId, baseStatus, customStatus);
        } catch (error: any) {
            // console.error('[PresenceService] Error updating status:', error);
            // If document doesn't exist, create it
            if (error.code === 404) {
                // console.log('[PresenceService] Document not found, creating new one');
                try {
                    const newDoc = await this.client.databases.createDocument(
                        'main',
                        'presence',
                        this.userId,
                        data
                    );
                    // console.log('[PresenceService] Created new presence document:', newDoc);
                } catch (createError) {
                    // console.error('[PresenceService] Error creating presence document:', createError);
                }
            }
        }
    }

    async cleanup() {
        // console.log('[PresenceService] Starting cleanup');
        if (this.pulseInterval) {
            // console.log('[PresenceService] Clearing pulse interval');
            clearInterval(this.pulseInterval);
            this.pulseInterval = null;
        }

        // Set status to offline when cleaning up
        if (this.userId && this.client) {
            // console.log('[PresenceService] Setting offline status');
            try {
                const response = await this.client.databases.updateDocument(
                    'main',
                    'presence',
                    this.userId,
                    {
                        userId: this.userId,
                        baseStatus: 'offline',
                        customStatus: null,
                        lastSeen: new Date().toISOString(),
                        workspaceId: get(page).params.workspaceId
                    }
                );
                // console.log('[PresenceService] Set offline status successfully:', response);
                presenceStore.updateStatus(this.userId, 'offline');
            } catch (error) {
                // console.error('[PresenceService] Error setting offline status:', error);
            }
        } else {
            // console.warn('[PresenceService] Missing userId or client for cleanup');
        }
    }
}

// Export singleton instance
export const presenceService = PresenceService.getInstance(); 
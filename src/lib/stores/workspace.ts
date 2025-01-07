import { writable } from 'svelte/store';
import { createSessionClient } from '$lib/appwrite/appwrite-client';
import type { Workspace, Channel } from '$lib/types';
import { ID, Query } from 'appwrite';

interface WorkspaceState {
    workspaces: Workspace[];
    currentWorkspace: Workspace | null;
    channels: Channel[];
    loading: boolean;
    error: string | null;
}

const createWorkspaceStore = () => {
    const { subscribe, set, update } = writable<WorkspaceState>({
        workspaces: [],
        currentWorkspace: null,
        channels: [],
        loading: false,
        error: null
    });

    return {
        subscribe,
        
        // Load user's workspaces
        loadWorkspaces: async (userId: string) => {
            try {
                update(state => ({ ...state, loading: true, error: null }));
                
                const client = createSessionClient(event);
                const response = await client.databases.listDocuments(
                    'chattie',
                    'workspaces',
                    [Query.search('members.userId', userId)]
                );
                
                update(state => ({
                    ...state,
                    workspaces: response.documents as Workspace[],
                    loading: false
                }));
            } catch (error) {
                update(state => ({
                    ...state,
                    error: 'Failed to load workspaces',
                    loading: false
                }));
            }
        },

        // Set current workspace and load its channels
        setCurrentWorkspace: async (workspaceId: string) => {
            try {
                update(state => ({ ...state, loading: true, error: null }));
                
                const client = createSessionClient(event);
                const [workspace, channelsResponse] = await Promise.all([
                    client.databases.getDocument('chattie', 'workspaces', workspaceId),
                    client.databases.listDocuments(
                        'chattie',
                        'channels',
                        [Query.equal('workspaceId', workspaceId)]
                    )
                ]);

                update(state => ({
                    ...state,
                    currentWorkspace: workspace as Workspace,
                    channels: channelsResponse.documents as Channel[],
                    loading: false
                }));
            } catch (error) {
                update(state => ({
                    ...state,
                    error: 'Failed to load workspace',
                    loading: false
                }));
            }
        },

        // Create a new workspace
        createWorkspace: async (name: string, userId: string) => {
            try {
                update(state => ({ ...state, loading: true, error: null }));
                
                const client = createSessionClient(event);
                const workspace = await client.databases.createDocument(
                    'chattie',
                    'workspaces',
                    ID.unique(),
                    {
                        name,
                        members: [{ userId, role: 'admin' }],
                        settings: {
                            allowInvites: true,
                            allowFileUploads: true,
                            maxFileSize: 10 * 1024 * 1024 // 10MB
                        }
                    }
                );

                // Create a default "general" channel
                await client.databases.createDocument(
                    'chattie',
                    'channels',
                    ID.unique(),
                    {
                        workspaceId: workspace.$id,
                        name: 'general',
                        type: 'public',
                        members: [userId]
                    }
                );

                update(state => ({
                    ...state,
                    workspaces: [...state.workspaces, workspace as Workspace],
                    loading: false
                }));

                return workspace.$id;
            } catch (error) {
                update(state => ({
                    ...state,
                    error: 'Failed to create workspace',
                    loading: false
                }));
                throw error;
            }
        }
    };
};

export const workspace = createWorkspaceStore();
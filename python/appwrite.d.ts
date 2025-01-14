import type { Models } from "appwrite";

export interface Workspaces extends Models.Document {
    name: string;
    owner_id: string;
    members: string[];
    ai_persona?: string;
    message_frequency?: number;
};

export interface Channels extends Models.Document {
    workspace_id: string;
    name: string;
    type: string;
    members: string[];
    last_message_at?: Date;
    description?: string;
    purpose?: string;
    topics?: string[];
    primary_personas?: string[];
};

export interface Messages extends Models.Document {
    channel_id: string;
    workspace_id: string;
    sender_type: string;
    sender_id: string;
    content: string;
    edited_at?: Date;
    mentions?: string[];
    ai_context?: string;
    ai_prompt?: string;
    sender_name?: string;
    thread_id?: string;
    thread_count?: number;
    attachments?: string[];
};

export interface AiPersonas extends Models.Document {
    workspace_id: string;
    name: string;
    personality: string;
    conversation_style: string;
    avatar_url?: string;
    knowledge_base?: string[];
    greeting?: string;
    role?: string;
    opinions?: string[];
    ai_user_id?: string;
};

export interface MessageThreads extends Models.Document {
    parent_message_id: string;
    channel_id: string;
    workspace_id: string;
    last_reply_at: Date;
    participant_ids: string[];
    ai_participants?: string[];
};

export interface Attachments extends Models.Document {
    type?: string;
    url?: string;
    name?: string;
    size?: number;
    message_id?: string;
};

export interface Reactions extends Models.Document {
    emoji?: string;
    message_id?: string;
    user_id?: string;
    user_name?: string;
    channel_id?: string;
};

export interface Presence extends Models.Document {
    userId: string;
    lastSeen?: Date;
    workspaceId?: string;
    baseStatus?: string;
    customStatus?: string;
};

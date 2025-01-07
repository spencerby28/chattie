import type { Models } from "appwrite";

export type User = Models.Document & {
  id: string;
  email: string;
  fullName: string;
  displayName: string;
  avatar: string;
  status: UserStatus;
  workspaceIds: string[];
}

export enum UserStatus {
  Online = 'online',
  Away = 'away',
  Offline = 'offline'
}

export type Workspace = Models.Document & {
  id: string;
  name: string;
  ownerId: string;
  channels: Channel[];
  members: WorkspaceMember[];
  settings: WorkspaceSettings;
}

export interface WorkspaceMember {
  userId: string;
  role: WorkspaceRole;
}

export enum WorkspaceRole {
  Admin = 'admin',
  Member = 'member'
}

export interface WorkspaceSettings {
  allowInvites: boolean;
  allowFileUploads: boolean;
  maxFileSize: number;
}

export type Channel = Models.Document & {
  id: string;
  workspaceId: string;
  name: string;
  type: ChannelType;
  members: string[];
}

export enum ChannelType {
  Public = 'public',
  Private = 'private'
}

export type Message = Models.Document & {
  channel_id: string;
  workspace_id: string;
  sender_type: 'person' | 'ai';
  sender_id: string;
  content: string;
  edited_at: string | null;
  mentions: string[];
  ai_context: string | null;
  ai_prompt: string | null;
  attachments: Attachment[];
  reactions: Reaction[];
  user?: User;
}

export type Attachment = Models.Document & {
  type: string;
  url: string;
  name: string;
  size: number;
}

export type Reaction = Models.Document & {
  message_id: string;
  emoji: string;
  userIds: string[];
}
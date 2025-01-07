
1. **Workspaces Collection**
```typescript:chattie/structure/db.md
{
  id: string // unique identifier
  name: string // workspace name
  created_at: datetime
  owner_id: string // user who created the workspace
  settings: {
    ai_persona: string // personality type for this workspace's AI
    message_frequency: number // how often AI should generate messages
  }
  members: string[] // array of user IDs
}
```

2. **Channels Collection**
```typescript
{
  id: string
  workspace_id: string // reference to workspace
  name: string
  type: 'public' | 'private'
  created_at: datetime
  members: string[] // array of user IDs with access
  last_message_at: datetime // for sorting/fetching
}
```

3. **Messages Collection**
```typescript
{
  id: string
  channel_id: string // reference to channel
  workspace_id: string // for faster querying
  sender_type: 'user' | 'ai' // to distinguish between human and AI messages
  sender_id: string // user ID or AI persona ID
  content: string
  created_at: datetime
  edited_at: datetime
  attachments: [{
    type: string
    url: string
    name: string
  }]
  reactions: [{
    emoji: string
    users: string[]
  }]
  mentions: string[] // array of mentioned user IDs
  metadata: {
    ai_context?: string // context used for AI generation
    ai_prompt?: string // prompt used if AI generated
  }
}
```

4. **AI Personas Collection**
```typescript
{
  id: string
  workspace_id: string
  name: string
  personality: string // description of AI personality
  avatar_url: string
  conversation_style: string // formal, casual, technical, etc.
  knowledge_base: string[] // topics/domains this AI specializes in
}
```

5. **Message Threads Collection** (for conversation continuity)
```typescript
{
  id: string
  parent_message_id: string
  channel_id: string
  workspace_id: string
  last_reply_at: datetime
  participant_ids: string[] // users involved in thread
  ai_participants: string[] // AI personas involved
}
```

Key Features of this Structure:

1. **Indexing**:
- Create indexes on `workspace_id` and `channel_id` in Messages collection
- Index `last_message_at` in Channels for efficient sorting
- Index `created_at` in Messages for pagination

2. **Relationships**:
- Workspaces → Channels (one-to-many)
- Channels → Messages (one-to-many)
- Messages → Threads (one-to-many)
- Workspaces → AI Personas (one-to-many)

3. **Query Patterns**:
- Fetch messages by channel with pagination
- Get all channels in a workspace
- Get AI personas for a workspace
- Get thread replies for a message

4. **Real-time Features**:
- Subscribe to message updates by channel
- Subscribe to thread updates
- Track AI message generation status

Would you like me to proceed with creating these collections in Appwrite, or would you like to discuss any specific aspect of this structure in more detail?

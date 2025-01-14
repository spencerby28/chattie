async def send_initial_messages(channel_id: str, workspace_id: str):
    try:
        # Get channel info
        channel = databases.get_document(
            database_id=DATABASE_ID,
            collection_id=CHANNELS_COLLECTION,
            document_id=channel_id
        )
        
        # Get AI personas for this channel
        ai_personas = []
        for persona_name in channel.get('primary_personas', []):
            # Query to find persona by name in workspace
            persona_docs = databases.list_documents(
                database_id=DATABASE_ID,
                collection_id=PERSONAS_COLLECTION,
                queries=[
                    Query.equal('workspace_id', workspace_id),
                    Query.equal('name', persona_name)
                ]
            )
            if persona_docs.documents:
                ai_personas.append(persona_docs.documents[0])

        # For each AI persona, generate and send an initial message
        for persona in ai_personas:
            # Create prompt for the persona's first message
            prompt = f"""
            You are {persona['name']}, with the following characteristics:
            Background: {persona['background']}
            Personality: {persona['personality']}
            Communication style: {persona['communication_style']}
            
            You are in a channel named '{channel['name']}' with the following:
            Description: {channel['description']}
            Purpose: {channel['purpose']}
            Topics: {', '.join(channel['topics'])}
            
            Write a brief initial message introducing yourself to the channel,
            keeping in mind your personality and the channel's purpose.
            The message should be natural and conversational.
            """
            
            # Generate message content using OpenAI
            message_content = await generate_with_openai(prompt, OPENAI_API_KEY)
            
            # Create message document
            message_data = {
                'channel_id': channel_id,
                'user_id': persona['user_id'],
                'content': message_content,
                'timestamp': datetime.now().isoformat(),
                'workspace_id': workspace_id,
                'type': 'text'
            }
            
            # Store message in database
            databases.create_document(
                database_id=DATABASE_ID,
                collection_id=MESSAGES_COLLECTION,
                document_id=ID.unique(),
                data=message_data,
                permissions=[
                    Permission.read(Role.users()),
                    Permission.write(Role.user(persona['user_id'])),
                    Permission.update(Role.user(workspace_id)),
                    Permission.delete(Role.user(workspace_id))
                ]
            )
            
            # Update channel's last_message_at
            databases.update_document(
                database_id=DATABASE_ID,
                collection_id=CHANNELS_COLLECTION,
                document_id=channel_id,
                data={
                    'last_message_at': message_data['timestamp']
                }
            )
            
    except Exception as e:
        logger.error(f"Error sending initial messages for channel {channel_id}: {str(e)}")
        logger.exception(e)
        raise e

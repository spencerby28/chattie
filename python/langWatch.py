import langwatch
import os
from openai import AsyncOpenAI
import asyncio

# Initialize LangWatch
langwatch.api_key = os.getenv("LANGWATCH_API_KEY")
langwatch.endpoint = "http://localhost:5560"

print(langwatch.endpoint)

@langwatch.trace()
async def trace_openai():
    try:
        # Create real OpenAI client
        openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Track the OpenAI calls
        langwatch.get_current_trace().autotrack_openai_calls(openai_client)
        
        # Make a real call to OpenAI
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Fixed model name
            messages=[{"role": "user", "content": "tell me a short story about a cat"}]
        )
        
        # Print the response content
        print(response.choices[0].message.content)
        return response
    except Exception as e:
        # LangWatch will automatically capture the error
        print(f"Error during OpenAI call: {str(e)}")
        raise

async def main():
    result = await trace_openai()
    return result

if __name__ == "__main__":
    asyncio.run(main())
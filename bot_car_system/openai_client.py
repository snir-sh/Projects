import os
from openai import OpenAI, AsyncOpenAI

# Get API key from environment variable
# To set it locally: export OPENAI_API_KEY="your-api-key-here"
# To create an OpenAI API key, visit: https://platform.openai.com/api-keys
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set. Create a key at https://platform.openai.com/api-keys")

client = OpenAI(api_key=api_key)

async_client = AsyncOpenAI(api_key=api_key)

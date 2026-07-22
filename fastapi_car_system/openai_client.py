from openai import OpenAI, AsyncOpenAI

api_key="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"

client = OpenAI(api_key=api_key)

async_client = AsyncOpenAI(api_key=api_key)

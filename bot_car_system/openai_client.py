from openai import OpenAI, AsyncOpenAI

api_key="sk-proj-KEY-HOLDER"

client = OpenAI(api_key=api_key)

async_client = AsyncOpenAI(api_key=api_key)

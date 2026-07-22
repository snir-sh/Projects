from openai_client import client, async_client
from gpt_query_data import CAR_KEYWORDS, GPT_INSTRUCTIONS, GPT_CONFIG


def is_car_related(message: str) -> bool:
    """Checks if the message is about cars."""
    text = message.lower()
    return any(word in text for word in CAR_KEYWORDS)


async def async_find_recommendation(message: str) -> str:
    """Query GPT for car recommendations."""
    response = await async_client.chat.completions.create(
        **GPT_CONFIG,
        messages=[
            {
                "role": "system",
                "content": GPT_INSTRUCTIONS
            },
            {
                "role": "user", 
                "content": message
                },
        ],

    )
    return response.choices[0].message.content.strip()


def find_recommendation(message: str) -> str:
    """Query GPT for car recommendations."""
    response = client.chat.completions.create(
        **GPT_CONFIG,
        messages=[
            {
                "role": "system",
                "content": GPT_INSTRUCTIONS
            },
            {
                "role": "user", 
                "content": message
                },
        ],

    )
    return response.choices[0].message.content.strip()

async def chat(message: str):
    if not is_car_related(message):
        return "not related"
    return await async_find_recommendation(message)
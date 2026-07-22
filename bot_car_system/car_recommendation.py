import Logger
from openai_client import client, async_client
from gpt_query_data import CAR_KEYWORDS, GPT_CONFIG, SYSTEM_MESSAGES 
from enums import Actions


def is_car_related(message: str) -> bool:
    """Checks if the message is about cars."""
    text = message.lower()
    return any(word in text for word in CAR_KEYWORDS)


async def recommendation_chat(history: list) -> str:
    """Query GPT for car recommendations."""
    response = await async_client.chat.completions.create(
        **GPT_CONFIG,
        messages=[SYSTEM_MESSAGES['recommendation']] + history
    )
    return response.choices[0].message.content.strip()


async def search_chat(history: list) -> str:
    """Query GPT for car recommendations."""
    response = client.chat.completions.create(
        **GPT_CONFIG,
        messages=[SYSTEM_MESSAGES['search']] + history
    )
    return response.choices[0].message.content.strip()

async def chat(history: list, chat_type: str):
    # if not is_car_related(message):
    #     return "not related"
    if chat_type == Actions.SEARCH.value:
        return await search_chat(history)
    elif chat_type == Actions.RECOMMENDATION.value:
        return await recommendation_chat(history)

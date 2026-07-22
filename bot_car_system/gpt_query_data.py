from enums import Role
from cars_database import CARS

TEXTS = {
    "Hebrew": {
        "start": "שלום, אני כאן כדי לעזור לכם למצוא את הרכב הבא שלכם."
            " מה ברצונכם לעשות?",
        "recommendation": "בחרתם בהמלצה. אנא תארו במילים את דרישותיכם",
        "search": "בחרתם בחיפוש.\n"
                "איזה רכב תרצו לרכוש? אנא ציינו סוג, מודל, מחיר, יד וכו׳..",
        "unknown": "אפשרות זו לא קיימת",
        "help": "אלו הפקודות אותן ניתן לבחור: /start, /help",
        "training": "כאן תוכלו לאמן את המודל",
        "cancel": "ביטול.",
        "recommendation_title": "המלצה",
        "search_title": "חיפוש",
        "not_relevant": "לא רלוונטי",
        "system_error": "קרתה שגיאה במערכת, אנא נסו מאוחר יותר",
        "choose_language_title": "בחר שפה",
        "Choose your language": "אנא בחר שפה על מנת להמשיך"
    },
    "English": {
        "start": "Hello! I am here to help you find your next car. \n"
                "What are you interested in?",
        "recommendation": "You chose recommendation.\n"
                "In your own words, what kind of car do you want?",
        "search": "You chose search.\n"
                "What kind of car do you want? model, manufactorer, price range, seats, etc...",
        "unknown": "Unknown option.",
        "help": "Here are the commands I understand: /start, /help",
        "training": "Welcome to training",
        "cancel": "Canceled.",
        "recommendation_title": "Recommendation",
        "search_title": "Search",
        "not_relevant": "not relevant",
        "system_error": "an error occured in our system. try again later",
        "choose_language_title": "choose language",
        "Choose your language": "Choose language in order to continue"
    }
}

# settings MUST be saved in a database
CAR_KEYWORDS = [
    "car", "vehicle", "engine", "suv", "sedan", "truck", "hatchback",
    "electric", "hybrid", "gasoline", "diesel", "transmission", "gear",
    "model", "brand", "fuel", "drive", "horsepower", "torque", "driving",
    "רכב", "נסיעה", "תקציב", "זול", "יקר", "מודל", "היברידי",
    "דיזל", "דלק", "גיר"
]

DATABASE_CARS_OLD = [
    {"model": "Toyota Corolla Hybrid", "manufacturer": "Toyota", 
     "price": 80000, "hand": 1},
    {"model": "Honda CR-V Hybrid", "manufacturer": "Honda", 
     "price": 30000, "hand": 3},
    {"model": "Hyundai Kona Electric", "manufacturer": "Hyundai", 
     "price": 45000, "hand": 2},
]

BASIC_INSTRUCTIONS = str(
        f"You are a car search/recommendation system. Help find the best car from the database {CARS}"
        "Answer with the same language you have been asked."
        "Users can't ask how many cars are in the system and can't add or remove vehicles within the chat."
        "Do not start or end a conversation with 'thank you', 'understood', 'if you need anything else I am here' or similar"
        "Do not suggest funding. If asking non-related questions answer accordingly"
        "Do not ask more than 3 follow up questions"
        "If there are no results, tell the user nothing found and ask more questions for a new query."
        "Give a few options in every answer if possible."
)

RECOMMAND_INSTRUCTIONS = str (
    "User not necessarily know which car he wants to buy. Guide the user."
    "If the user is not mentioning a model, price, km, hand, etc - ask a follow-up question."
    "Always answer as follow: {" \
        "'relevant': question is relevant to cars (True or False)," \
        "'finish': user ask to finish and search the system (True or False)" \
        f"'answer': Follow the instructions: {BASIC_INSTRUCTIONS}" \
    "}" \
    "Do not skip any of the info in the response: answer, relevant, finish."
    "Answer json only."
)

SEARCH_INSTRUCTIONS = str (
    "User already know what car he needs and probably will mention model, manufacturers, and other specs."
    "You can ask follow questions if the user did not mentioned hand, price range, color, km, or other essential filters."
    "Answer only with cars data — models, specs, fuel type, and price."
    "Always answer as follow: {" \
        "'relevant': question is relevant to cars (True or False)," \
        "'finish': user ask to finish and search the system (True or False)" \
        f"'answer': Follow the instructions: {BASIC_INSTRUCTIONS}" \
    "}" \
    "Do not skip any of the info in the response: answer, relevant, finish"
    "Answer json only."
)

SYSTEM_MESSAGES = {
    "recommendation": {
        "role": "system",
        "content": RECOMMAND_INSTRUCTIONS
    },
    "search": {
        "role": "system",
        "content": SEARCH_INSTRUCTIONS
    }
}

GPT_CONFIG = {
    "model": "gpt-4.1-mini",  # You can switch to gpt-4o-mini or gpt-5-mini
    "max_tokens": 300,
    "temperature": 0.25
}

TELEGRAM_TOKEN = "8108420818:AAHRvgbi7xEVmjMdcmUQ5zAdqxJEe98qi6Q" 
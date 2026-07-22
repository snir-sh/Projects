
# settings MUST be saved in a database
CAR_KEYWORDS = [
    "car", "vehicle", "engine", "suv", "sedan", "truck", "hatchback",
    "electric", "hybrid", "gasoline", "diesel", "transmission", "gear",
    "model", "brand", "fuel", "drive", "horsepower", "torque", "driving",
    "רכב"
]

DATABASE_CARS = [
    {"model": "Toyota Corolla Hybrid", "manufacturer": "Toyota"},
    {"model": "Honda CR-V Hybrid", "manufacturer": "Honda"},
    {"model": "Hyundai Kona Electric", "manufacturer": "Hyundai"},
]

GPT_INSTRUCTIONS =  (
                    "You are a car recommendation system based in Israel."
                    "Answer ONLY with cars data — models, specs, fuel type, and price range. "
                    "Do NOT include explanations, intros, or comments."
                    f"Give a few options in every answer but only things that are exist here: {DATABASE_CARS}."
                    "Cheap cars must be less than 100K. If nothing found you need to answer 'no results found'"
                    "If asking in Hebrew - answer in Hebrew, if asking in English - answer in English, etc.."
                    "If there any results, send me as array of jsons"
                )

GPT_CONFIG = {
    "model": "gpt-4.1-mini",  # You can switch to gpt-4o-mini or gpt-5-mini
    "max_tokens": 300,
    "temperature": 0.25,
}

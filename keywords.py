from datetime import datetime
# Keywords
keywords = [
    "news",
    "weather",
    "time",
    "date"
]

actions = [
    "Sorry, the news has been switched off for child safety.",
    "The current temperature in Almere, Flevoland, sits at a comfortable 22 degrees.",
    lambda: f"The time is {datetime.now().strftime('%I:%M %p')}",
    lambda: f"Today is {datetime.now().strftime('%B %d, %Y')}"
]

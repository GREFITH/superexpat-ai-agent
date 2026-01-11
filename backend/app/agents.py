EVENT_KEYWORDS = [
    "event", "events", "concert", "meetup",
    "festival", "conference", "show", "things to do"
]

JOB_KEYWORDS = [
    "job", "jobs", "hiring", "career", "vacancy"
]

KNOWN_CITIES = [
    "london", "berlin", "paris", "new york",
    "toronto", "jaipur", "delhi", "mumbai"
]


def detect_intent(query: str) -> str:
    q = query.lower()
    if any(k in q for k in EVENT_KEYWORDS):
        return "event"
    if any(k in q for k in JOB_KEYWORDS):
        return "job"
    return "general"


def extract_location(query: str) -> str:
    q = query.lower()
    for city in KNOWN_CITIES:
        if city in q:
            return city.title()
    return "Global"


def sanitize_query(query: str, location: str) -> str:
    return query.lower().replace(f"in {location.lower()}", "").strip()

# backend/app/rag.py
from app.agents import detect_intent, extract_location, sanitize_query
from app.tools import fetch_eventbrite_events, fetch_serpapi_results
from app.vector_store import vector_store
from app.config import settings
from datetime import datetime

# Initialize Gemini AI
try:
    import google.generativeai as genai
    
    if settings.gemini_api_key and "your_" not in settings.gemini_api_key.lower():
        genai.configure(api_key=settings.gemini_api_key)
        gemini_model = genai.GenerativeModel(settings.gemini_model)
        print(" Gemini AI initialized successfully")
    else:
        gemini_model = None
        print(" Gemini API key not configured - AI summaries disabled")
except Exception as e:
    gemini_model = None
    print(f" Gemini initialization failed: {e}")


def remove_duplicates(results):
    """Remove duplicate events based on title and date"""
    seen = set()
    unique_results = []
    
    for item in results:
        title = (item.get("title") or "").lower().strip()
        date = (item.get("start_date") or "").strip()
        
        if not title:
            continue
        
        key = f"{title}_{date}" if date else title
        
        if key not in seen:
            seen.add(key)
            unique_results.append(item)
    
    return unique_results


def filter_valid_events(results):
    """Filter out events that don't meet quality criteria"""
    valid_events = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for event in results:
        # Must have title
        if not event.get("title"):
            continue
        
        # Must have valid URL
        url = event.get("url")
        if not url or not url.startswith("http"):
            continue
        
        # Skip generic Google URLs
        if "google.com/search" in url or "google.com/maps/search" in url:
            continue
        
        # Must have date
        event_date = event.get("start_date")
        if not event_date:
            continue
        
        # Skip past events
        if event_date < current_date:
            continue
        
        valid_events.append(event)
    
    return valid_events


def generate_ai_summary(query: str, location: str, total_results: int, results: list, intent: str) -> str:
    """Generate intelligent AI summary using Gemini + RAG"""
    
    # Fallback if Gemini not available
    if not gemini_model:
        if intent == "event":
            return f"🎉 Found {total_results} exciting events for you in {location}! Check them out below."
        else:
            return f"💼 Found {total_results} job opportunities in {location}! Explore the listings below."
    
    try:
        # Get contextual knowledge from vector store
        context_docs = vector_store.search(query, top_k=3)
        context_text = "\n".join([
            f"• {doc['content'][:200]}" 
            for doc in context_docs if doc.get('content')
        ])
        
        # Prepare top results summary
        top_items = results[:5]
        items_summary = "\n".join([
            f"• {item['title']} - {item.get('start_date', 'Date TBA')} at {item.get('venue', item.get('company', 'Location TBA'))}"
            for item in top_items
        ])
        
        # Build AI prompt
        if intent == "event":
            prompt = f"""You are a friendly travel and events assistant. Generate a brief, enthusiastic 2-3 sentence summary for the user.

User is searching for: "{query}" in {location}
Total results found: {total_results}

Top 5 events:
{items_summary}

Additional context (if relevant):
{context_text if context_text else "No additional context available"}

Write a warm, helpful 2-3 sentence summary that:
1. Highlights the best/most interesting events
2. Mentions any notable patterns (e.g., many concerts, diverse venues)
3. Encourages the user to explore

Be conversational and enthusiastic but concise. Don't repeat the full event list."""

        else:  
            prompt = f"""You are a career advisor assistant. Generate a brief, professional 2-3 sentence summary for the user.

User is searching for: "{query}" in {location}
Total results found: {total_results}

Top 5 opportunities:
{items_summary}

Write a helpful 2-3 sentence summary that:
1. Highlights key opportunities
2. Mentions any notable companies or roles
3. Encourages professional exploration

Be professional yet warm. Don't repeat the full job list."""

        # Generate AI response
        response = gemini_model.generate_content(prompt)
        ai_text = response.text.strip()
        
        # Validate response
        if len(ai_text) > 500:
            ai_text = ai_text[:497] + "..."
        
        print(f" AI Summary generated: {ai_text[:100]}...")
        return ai_text
        
    except Exception as e:
        print(f" Gemini AI error: {e}")
        # Fallback
        if intent == "event":
            return f"🎉 Found {total_results} exciting events in {location}! Check out the listings below."
        else:
            return f"💼 Found {total_results} opportunities in {location}! Browse the jobs below."


def handle_query(query: str, page: int = 1, page_size: int = 10):
    """Main RAG handler with Gemini AI integration"""
    
    # Detect intent and extract location
    intent = detect_intent(query)
    location = extract_location(query)
    topic = sanitize_query(query, location)

    print(f"\n{'='*60}")
    print(f" RAG Processing with Gemini AI")
    print(f"{'='*60}")
    print(f"Intent: {intent}")
    print(f"Location: {location}")
    print(f"Topic: {topic}")
    print(f"{'='*60}\n")

    results = []

    # Fetch results based on intent
    if intent == "event":
        print(" Fetching from Eventbrite...")
        eventbrite_results = fetch_eventbrite_events(topic, location)
        
        print(" Fetching from Google Events (SerpAPI)...")
        serpapi_results = fetch_serpapi_results(topic, location, mode="events")
        
        # Combine sources
        results = eventbrite_results + serpapi_results
        print(f"\n Combined: {len(results)} total events")
        
        # Apply filters
        print(f"\n Filtering events...")
        results = filter_valid_events(results)
        print(f"✓ After filtering: {len(results)} valid events")
        
        # Remove duplicates
        print(f"\n Removing duplicates...")
        results = remove_duplicates(results)
        print(f"✓ After deduplication: {len(results)} unique events")

    elif intent == "job":
        print(" Fetching jobs from SerpAPI...")
        results = fetch_serpapi_results(topic, location, mode="jobs")

    # Sort by date (earliest first)
    results = sorted(
        results,
        key=lambda x: (
            x.get("start_date") or "9999-12-31",
            x.get("start_time") or "00:00"
        )
    )

    total = len(results)

    # Generate AI summary with RAG
    print(f"\n Generating AI summary with RAG...")
    ai_summary = generate_ai_summary(query, location, total, results, intent)

    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_results = results[start:end]

    print(f"\n{'='*60}")
    print(f" RAG Processing Complete")
    print(f"{'='*60}")
    print(f"Total results: {total}")
    print(f"AI Summary: {ai_summary[:80]}...")
    print(f"Page {page}: Showing {len(paginated_results)} results")
    print(f"{'='*60}\n")

    return {
        "intent": intent,
        "query": query,
        "location": location,
        "total_results": total,
        "results": paginated_results,
        "ai_summary": ai_summary, 
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
        }
    }

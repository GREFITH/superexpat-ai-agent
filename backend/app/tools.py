import requests
from app.config import settings
from datetime import datetime
import re


def parse_date_string(date_str):
    """
    Parse date and ensure it's in 2025-2026 range (not 2027)
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip()
    current_date = datetime.now()
    current_year = current_date.year
    
    # Clean ordinals
    clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    
    # Try YYYY-MM-DD format
    yyyy_mm_dd = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', clean_date)
    if yyyy_mm_dd:
        year, month, day = yyyy_mm_dd.groups()
        parsed_year = int(year)
        
      
        if parsed_year > 2026:
            parsed_year = current_year if int(month) >= current_date.month else current_year + 1
        
        return f"{parsed_year}-{month.zfill(2)}-{day.zfill(2)}"
    
    # Try with year
    date_with_year = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*(\d{4})', 
                               clean_date, re.IGNORECASE)
    if date_with_year:
        day, month, year = date_with_year.groups()
        parsed_year = int(year)
        
        
        if parsed_year > 2026:
            parsed_year = current_year
        
        try:
            date_obj = datetime.strptime(f"{day} {month} {parsed_year}", "%d %b %Y")
            return date_obj.strftime("%Y-%m-%d")
        except:
            pass
    
    # Without year - add current year
    month_day = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})', 
                         clean_date, re.IGNORECASE)
    if month_day:
        month, day = month_day.groups()
        try:
            date_obj = datetime.strptime(f"{day} {month} {current_year}", "%d %b %Y")
            parsed_date = date_obj.strftime("%Y-%m-%d")
            
       
            if parsed_date < current_date.strftime("%Y-%m-%d"):
                next_year = min(current_year + 1, 2026)
                date_obj = date_obj.replace(year=next_year)
                parsed_date = date_obj.strftime("%Y-%m-%d")
            
            return parsed_date
        except:
            pass
    
    return None


def fetch_eventbrite_events(topic: str, location: str):
    """
    Fetch events from Eventbrite API
    Testing URL: https://www.eventbriteapi.com/v3/events/search/?q=music&location.address=London
    """
    
    if not settings.eventbrite_api_key or "your_" in settings.eventbrite_api_key.lower():
        print(" Eventbrite: API key not configured")
        return []
    
    try:
        # Use search endpoint
        url = "https://www.eventbriteapi.com/v3/events/search/"
        headers = {"Authorization": f"Bearer {settings.eventbrite_api_key}"}
        
        params = {
            "q": topic,
            "location.address": location,
            "location.within": "50km",
            "sort_by": "date",
            "expand": "venue",
            "page": 1
        }
        
        print(f"🔍 Testing Eventbrite: {url}")
        print(f"   Query: {topic} in {location}")
        
        r = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 401:
            print(f" Eventbrite: Invalid API key")
            print(f"   Get new key: https://www.eventbrite.com/account-settings/apps")
            return []
        
        if r.status_code != 200:
            print(f" Eventbrite: HTTP {r.status_code}")
            return []
        
        data = r.json()
        events_list = data.get("events", [])
        
        if not events_list:
            print(f" Eventbrite: No events returned")
            print(f"   Try in browser: {url}?q={topic}&location.address={location}")
            return []
        
        events = []
        for e in events_list[:20]:  # Limit to 20
            if not e.get("url") or not e.get("name", {}).get("text"):
                continue
            
            start = e.get("start", {}).get("local", "")
            if "T" in start:
                date_part = start.split("T")[0]
                time_part = start.split("T")[1][:5]
            else:
                date_part = start or None
                time_part = None
            
            # FIX: Ensure proper date
            if date_part and "2027" in date_part:
                date_part = date_part.replace("2027", "2025")
            
            events.append({
                "id": f"eb_{e.get('id')}",
                "type": "events",
                "title": e.get("name", {}).get("text"),
                "poster": e.get("logo", {}).get("url"),
                "start_date": date_part,
                "start_time": time_part,
                "venue": e.get("venue", {}).get("name"),
                "address": e.get("venue", {}).get("address", {}).get("localized_address_display"),
                "price": "Free" if e.get("is_free") else "Paid",
                "timezone": "UTC",
                "source": "Eventbrite",
                "url": e.get("url"),  # Direct event URL
                "company": None,
                "description": e.get("description", {}).get("text", "")[:200] if e.get("description") else None
            })
        
        print(f" Eventbrite: Found {len(events)} events")
        return events
        
    except Exception as e:
        print(f" Eventbrite exception: {e}")
        return []


def fetch_serpapi_results(query: str, location: str, mode="events"):
    """
    Fetch from SerpAPI with proper link extraction
    """
    
    if not settings.serpapi_key or "your_" in settings.serpapi_key.lower():
        print(" SerpAPI: API key not configured")
        return []
    
    try:
        engine = "google_events" if mode == "events" else "google_jobs"
        
        params = {
            "engine": engine,
            "q": f"{query} {location}" if mode == "events" else query,
            "location": location if mode == "jobs" else None,
            "api_key": settings.serpapi_key,
            "hl": "en"
        }
        
        params = {k: v for k, v in params.items() if v is not None}
        
        r = requests.get("https://serpapi.com/search", params=params, timeout=15)
        
        if r.status_code != 200:
            print(f" SerpAPI Error: {r.status_code}")
            return []
        
        data = r.json()
        results = []
        
        key = "events_results" if mode == "events" else "jobs_results"
        
        for item in data.get(key, []):
            title = item.get("title")
            
            # FIX: Get proper event link
            if mode == "events":
                # Try multiple link fields in order
                link = (item.get("link") or 
                       item.get("ticket_info", {}).get("link") or
                       item.get("venue_link"))
            else:
                link = item.get("share_link") or item.get("apply_link")
            
            if not title or not link or not link.startswith("http"):
                continue
            
            # Skip Google search links
            if "google.com/search" in link or "google.com/url" in link:
                continue
            
            # Extract date
            start_date = None
            if mode == "events":
                date_info = item.get("date", {})
                
                raw_date = None
                if isinstance(date_info, dict):
                    raw_date = date_info.get("start_date") or date_info.get("when") or date_info.get("date")
                elif isinstance(date_info, str):
                    raw_date = date_info
                
                if raw_date:
                    start_date = parse_date_string(raw_date)
            else:
                start_date = item.get("detected_extensions", {}).get("posted_at")
            
            # Extract venue
            venue = item.get("venue")
            if isinstance(venue, dict):
                venue = venue.get("name", "")
            
            # Extract address
            address = item.get("address")
            if isinstance(address, list):
                address = ", ".join(str(a) for a in address if a)
            
            results.append({
                "id": f"serp_{hash(link)}",
                "type": mode,
                "title": title,
                "poster": item.get("thumbnail"),
                "start_date": start_date,
                "start_time": None,
                "venue": str(venue) if venue else None,
                "address": str(address) if address else None,
                "price": None,
                "timezone": "UTC",
                "source": "Google Events" if mode == "events" else "Google Jobs",
                "url": link,  # This should now be correct
                "company": item.get("company_name") if mode == "jobs" else None,
                "description": item.get("description") if mode == "jobs" else None
            })
        
        print(f" SerpAPI ({mode}): Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f" SerpAPI Exception: {e}")
        return []

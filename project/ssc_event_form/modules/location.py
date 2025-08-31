# location.py

def validate(location_text):
    """
    Stub for location validation.
    Replace with GIS API or spatial lookup later.
    """
    keywords = ["park", "reserve", "oval", "foreshore", "beach", "hall"]
    location_lower = location_text.lower()
    return any(keyword in location_lower for keyword in keywords)
# 🌞 Walking on Sunshine

Walking on Sunshine is a creative web application that generates walking routes based on the length of your favorite music albums. Perfect for music lovers who want to time their walks to their favorite albums!

## 🎯 Features

- **Spotify-powered lookup**: search, autocomplete, and lock to the exact album (ID + metadata) before running
- **Album insight panel**: track count, release year, duration label, artist, and cover art at a glance
- **Route generator**: OpenRoute Service produces a looping walk that matches the album play time
- **Map preview**: Folium embed (with SVG fallback) shows the full path and start/finish markers
- **Copyable directions**: one-click button copies the Google Maps link to your clipboard
- **Location tools**: Places autocomplete, reverse geocode “Use my location,” and manual entry options

## 🛠️ Technology Stack

### Backend (Python)
- FastAPI service exposing `/search_albums`, `/generate_route`, `/maps_config`
- Spotify client for album details (duration, tracks, release year, artwork)
- OpenRoute Service client + Folium map rendering for walking loops
- Structured logging, type hints, and pytest coverage for path/album logic

### Frontend
- Vanilla HTML/CSS/JS served statically by FastAPI
- Debounced Spotify search with keyboard-aware dropdown
- Two-step UX (album → location) with animated transitions
- Google Places autocomplete + reverse geocoding for “Use my location”
- Route result card with stats, map embed, and clipboard-friendly actions

### APIs and Services
- Spotify Web API (albums, tracks, images, popularity)
- OpenRoute Service (directions, reverse geocode fallback)
- Folium (Leaflet map HTML embeddable in frontend)
- Google Maps Places (autocomplete + geocoding when API key provided)

## 🏗️ Architecture

The project follows a clean architecture pattern with clear separation of concerns:

```
walking_on_sunshine/
├── api/          # FastAPI endpoints and routing
├── app/          # Core business logic
├── command/      # CLI commands and entry points
├── common/       # Shared utilities and logging
└── frontend/     # Static web interface
```

### Key Components

1. **Album Service**
   - Handles Spotify API integration
   - Caches album data for performance
   - Provides search suggestions

2. **Path Generator**
   - Calculates optimal walking routes
   - Ensures routes return to starting point
   - Adapts to walking speed (2.5 km/h)

3. **Frontend Interface**
   - Responsive search interface
   - Real-time validation
   - Dynamic route display

## 🚀 Technical Highlights

- **Type Safety**: Leverages Python's type hints for better code quality
- **Error Handling**: Built-in FastAPI exception handling
- **API Security**: Secure API key management for external services
- **Modern UI**: CSS Grid and Flexbox for responsive layouts
- **Testing**: Unit tests for core path generation functionality
- **Clean Architecture**: Well-organized code with clear separation of concerns
- **Async Support**: FastAPI's asynchronous request handling

## 💡 Features for Future Development

1. **User Accounts**
   - Save favorite routes
   - Track walking history
   - Social sharing

2. **Extended Music Integration**
   - Support for multiple music services
   - Playlist support
   - BPM-based route suggestions

3. **Route Customization**
   - Terrain preferences
   - Points of interest integration
   - Multiple route options

## 🎓 Learning Outcomes

This project demonstrates proficiency in:

- Full-stack web development
- API integration and management
- Clean architecture principles
- Modern frontend design
- Error handling and logging
- Testing strategies
- Performance optimization

## 🛠️ Setup and Installation

```bash
# Clone the repository
git clone https://github.com/rclyburn/walking_on_sunshine.git
cd walking_on_sunshine

# Install dependencies (uv recommended)
uv sync
# or, if you prefer pip
pip install -e .

# Provide credentials (.env or exported variables)
export SPOTIFY_CLIENT_ID=your_spotify_client_id
export SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
export OPENROUTE_API_KEY=your_openroute_api_key
# Optional: unlock Places autocomplete + reverse geocode
export GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Launch the server
uv run main serve
# App available at http://localhost:8000
```

## 🎧 Using the App

1. Start typing an album name – use the dropdown (arrow keys + Enter or mouse) to pick the exact record.
2. Either enter a starting address or click **Use my location** (reverse geocodes to a street address).
3. Hit **Generate Route**. The result card shows album stats, distance, and a map preview.
4. Copy the Google Maps link or open it in a new tab to follow the generated walk.

## 💼 About the Project

Walking on Sunshine is a portfolio application created by Reid Clyburn to showcase full-stack development, third-party API orchestration, and polished UX. Feedback and collaboration are welcome.

## 📝 License

MIT License - Feel free to use this code for your own projects!

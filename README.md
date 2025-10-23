# 🌞 Walking on Sunshine

Walking on Sunshine is a creative web application that generates walking routes based on the length of your favorite music albums. Perfect for music lovers who want to time their walks to their favorite albums!

## 🎯 Features

- **Album Length Detection**: Integrates with Spotify's API to fetch precise album lengths
- **Dynamic Route Generation**: Creates walking routes that match album durations using OpenRoute Service
- **Interactive UI**: Modern, responsive interface with real-time album search suggestions
- **Smart Path Generation**: Automatically calculates circular routes that bring you back to your starting point

## 🛠️ Technology Stack

### Backend (Python)
- FastAPI for high-performance API endpoints
- Clean architecture with separation of concerns
- Dependency injection for configuration management
- Custom logging system for debugging and monitoring
- Unit testing with pytest

### Frontend
- Pure HTML5, CSS3, and Vanilla JavaScript
- Modern, responsive design
- Real-time search with dropdown suggestions
- Cache-busting for static assets
- Mobile-first approach

### APIs and Services
- Spotify Web API for music data
- OpenRoute Service for path generation
- Custom rate limiting and error handling

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
- **Error Handling**: Comprehensive error handling with custom exceptions
- **API Security**: Implements rate limiting and API key management
- **Caching**: Smart caching strategies for API responses
- **Testing**: Comprehensive unit tests for core functionality
- **Modern UI**: CSS Grid and Flexbox for responsive layouts
- **Performance**: Optimized asset loading and API calls

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

# Install dependencies
cd walking_on_sunshine
pip install -e .

# Set up environment variables
# Create a .env file with:
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
OPENROUTE_API_KEY=your_openroute_api_key

# Run the application
uv run main serve
```

## 👤 About the Developer

Created by Reid Clyburn as a demonstration of development capabilities.

## 📝 License

MIT License - Feel free to use this code for your own projects!

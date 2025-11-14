# Technical Documentation

## System Architecture

### Components Overview

#### 1. API Layer (`/api`)
- FastAPI implementation
- RESTful endpoints
- Request/Response validation
- Error handling middleware
- CORS configuration
- Static file serving

#### 2. Application Core (`/app`)
- Business logic implementation
- Service layer abstractions
- Data transformations
- External API integrations

#### 3. Command Layer (`/command`)
- CLI command implementations
- Application entry points
- Configuration management
- Service bootstrapping

#### 4. Common Utilities (`/common`)
- Logging configuration
- Shared utilities
- Cross-cutting concerns

### Key Classes

#### `App` (app/app.py)
Main application orchestrator that:
- Initializes core services
- Handles business logic coordination
- Manages error handling
- Processes album and route generation (accepts Spotify album ID when available)
- Aggregates rich album metadata for API consumers

#### `AlbumLength` (app/album_length.py)
Spotify integration service that:
- Manages Spotify API authentication
- Retrieves album metadata (duration, tracks, release info, artwork)
- Supports lookup by album ID for deterministic selections
- Calculates total album duration and formatted labels
- Handles API pagination and rate limiting

#### `PathGen` (app/path_gen.py)
Route generation service that:
- Integrates with OpenRoute Service
- Calculates looped walking paths sized to the album duration
- Down-samples coordinates for frontend previews
- Generates Folium HTML map embeds as the primary preview medium

## Frontend Architecture

### Structure
```
frontend/
├── src/
│   ├── assets/
│   │   ├── scripts/
│   │   │   └── main.js    # Core JavaScript
│   │   └── styles/
│   │       └── main.css   # Styling
│   └── components/
│       └── index.html     # Main page
```

### JavaScript Architecture
- Event-driven module in `main.js` (no framework)
- Debounced Spotify search with keyboard-accessible dropdown
- `selectedAlbum` state persists Spotify IDs for deterministic backend calls
- Two-step workflow controller (album → location) with animated transitions
- Integration helpers for Google Places Autocomplete, reverse geocode, and clipboard copy
- Fallback SVG renderer when Folium map HTML is unavailable

### CSS Architecture
- Mobile-first layout using Flexbox/Grid
- Theming handled via CSS custom properties (accent colour adapts to album art)
- Animation hooks for dropdowns, step transitions, and album art flip
- Utility classes for map canvases, metadata chips, and action buttons

## API Documentation

### Album Search Endpoint
`GET /search_albums?query={query}`

Query Parameters:
- `query`: Album name to search for (string)

Returns album search results including:
- Album ID
- Album Name
- Artist Name
- Album Cover Image URL

### Route Generation Endpoint
`GET /generate_route`

Query Parameters:
- `album_name`: Name of the album (string)
- `album_id` (optional): Spotify album ID returned by `/search_albums`
- `start_address`: Starting location (free-text address or `lat,lon` coordinate pair)

Returns:
- Album name + artist (normalized from Spotify)
- Album metadata (duration label, track count, release year, artwork URL)
- Distance in kilometers and Google Maps directions URL
- Folium map embed (Base64 HTML) and down-sampled route coordinates
- Normalized start address for display

### Maps Configuration Endpoint
`GET /maps_config`

Returns Google Maps API availability so the frontend can decide whether to enable Places autocomplete/reverse geocoding.

## Development Workflow

### Local Development
1. `uv sync` (or `pip install -e .`) to install dependencies
2. Provide API keys via `.env` (`SPOTIFY_CLIENT_ID/SECRET`, `OPENROUTE_API_KEY`, optional `GOOGLE_MAPS_API_KEY`)
3. `uv run main serve` to start FastAPI + static frontend
4. Visit http://localhost:8000

### Testing
- `make test` for backend/unit coverage (album + path generation)
- Manual API verification with HTTP clients (e.g., `/generate_route`)
- Frontend regression checks in Chrome/Firefox + responsive tooling
- Manual UX verification of autocomplete, map embed, and clipboard actions

### Deployment
- Static file optimization
- Environment configuration
- API key management

## Performance Considerations

### Frontend
- Debounced API calls
- Optimized asset loading
- Efficient DOM updates

### Backend
- Connection pooling
- Rate limiting
- Error boundary implementation

## Security Measures

- API key protection
- Input validation
- CORS configuration
- Rate limiting
- Error message sanitization

## Monitoring and Logging

- Structured logging
- Error tracking
- Performance monitoring
- API usage tracking

## Future Technical Considerations

### Scalability
- Database integration
- Caching layer
- Load balancing
- Horizontal scaling

### Features
- User authentication
- Route persistence
- Social sharing
- Analytics integration

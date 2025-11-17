# AI Chat Interface - Angular 17 Application

A professional ChatGPT/Claude-style chat interface built with Angular 17, featuring modern UI/UX, dark/light mode, and real-time messaging.

## Features

- **Authentication System**
  - Login and Registration pages
  - JWT token-based authentication
  - Protected routes with auth guards
  - Automatic token handling

- **Chat Interface**
  - ChatGPT/Claude-style sidebar with chat history
  - Real-time messaging
  - Markdown support for formatted responses
  - File upload functionality
  - Message history per session
  - Session management (create, load, delete)

- **Modern UI/UX**
  - Professional purple/blue gradient theme
  - Dark and Light mode toggle
  - Responsive design for mobile and desktop
  - Smooth animations and transitions
  - Material Design components

- **Advanced Features**
  - Google Fonts (Poppins, Roboto, Roboto Mono)
  - Session-based chat history
  - Message streaming support (ready for implementation)
  - Auto-scrolling to latest messages
  - File attachment preview

## Project Structure

```
src/
├── app/
│   ├── auth/
│   │   ├── auth.guard.ts              # Route protection
│   │   ├── auth.service.ts            # Authentication logic
│   │   ├── login.component.ts/html/scss
│   │   └── register.component.ts/html/scss
│   ├── chat/
│   │   ├── chat.service.ts            # Chat API communication
│   │   ├── chat.component.ts/html/scss
│   │   └── message.component.ts/html/scss
│   ├── shared/
│   │   ├── api.service.ts             # HTTP interceptor
│   │   └── theme.service.ts           # Dark/Light mode
│   ├── environments/
│   │   ├── environment.ts             # Development config
│   │   ├── environment.development.ts
│   │   └── environment.prod.ts        # Production config
│   ├── app.config.ts                  # App configuration
│   ├── app.routes.ts                  # Routing configuration
│   └── app.component.ts
├── styles.scss                        # Global styles
└── index.html
```

## Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure API URL**

   Update the API URL in `src/environments/environment.ts`:
   ```typescript
   export const environment = {
     production: false,
     apiUrl: 'http://localhost:8000/api/v1'  // Your backend API
   };
   ```

3. **Start Development Server**
   ```bash
   npm start
   # or
   ng serve
   ```

4. **Access Application**

   Open browser and navigate to: `http://localhost:4200`

## Environment Configuration

### Development
File: `src/environments/environment.ts`
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

### Production
File: `src/environments/environment.prod.ts`
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com/api/v1'
};
```

## Backend API Requirements

The application expects the following API endpoints:

### Authentication
- `POST /api/v1/auth/login` - User login (form-data: username, password)
- `POST /api/v1/auth/register` - User registration (JSON: username, email, password)
- `GET /api/v1/auth/me` - Get current user info

### Chat
- `GET /api/v1/chat/sessions` - Get all chat sessions
- `GET /api/v1/chat/sessions/:id/messages` - Get messages for a session
- `POST /api/v1/chat/send` - Send a message (form-data: content, session_id?, file?)
- `DELETE /api/v1/chat/sessions/:id` - Delete a session

### Response Formats

**Login/Register Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "Bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "username": "username"
  }
}
```

**Send Message Response:**
```json
{
  "message": {
    "id": "msg_id",
    "content": "AI response here",
    "role": "assistant",
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "session_id": "session_id"
}
```

## Routing

- `/` - Redirects to login
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/chat` - Main chat interface (protected)

## Theming

The application supports both light and dark themes:

### Toggle Theme
Users can toggle between themes using the switch in the sidebar.

### CSS Variables
Themes are implemented using CSS custom properties:

```css
/* Light Theme */
--bg-primary: #ffffff
--text-primary: #111827
--border-color: #e5e7eb

/* Dark Theme */
--bg-primary: #111827
--text-primary: #f9fafb
--border-color: #374151
```

## Key Components

### AuthService
Handles authentication, token management, and user state.

```typescript
// Usage
authService.login(email, password).subscribe(...)
authService.register(username, email, password).subscribe(...)
authService.logout()
authService.currentUser$ // Observable of current user
```

### ChatService
Manages chat sessions and messages.

```typescript
// Usage
chatService.loadSessions().subscribe(...)
chatService.sendMessage({ content, session_id?, file? }).subscribe(...)
chatService.messages$ // Observable of messages
chatService.sessions$ // Observable of sessions
```

### ThemeService
Controls the application theme.

```typescript
// Usage
themeService.toggleTheme()
themeService.isDarkMode$ // Observable of theme state
```

## Building for Production

```bash
# Build
ng build --configuration production

# Output will be in dist/frontend-angular
```

## Development Commands

```bash
# Start dev server
npm start

# Build project
npm run build

# Run tests
npm test

# Lint code
ng lint
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Technologies Used

- **Angular 17** - Framework
- **Angular Material** - UI Components
- **RxJS** - Reactive programming
- **ngx-markdown** - Markdown rendering
- **TypeScript** - Programming language
- **SCSS** - Styling

## Customization

### Color Scheme
Edit `src/styles.scss` to customize the color palette:

```scss
$primary-palette: (
  500: #667eea,  // Change primary color
  // ... other shades
);
```

### Fonts
The application uses Google Fonts. To change fonts, update the import in `src/styles.scss`:

```scss
@import url('https://fonts.googleapis.com/css2?family=Your+Font&display=swap');
```

## License

This project is part of the Interface Wizard application.

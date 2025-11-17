# Quick Start Guide

## 1. Install Dependencies

```bash
cd /c/Users/Sirii/Work/Gen-AI/interface-wizard/frontend-angular
npm install
```

## 2. Configure Backend API

The application is already configured to use `http://localhost:8000/api/v1` as the backend API.

If you need to change this, edit `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'  // Change this if needed
};
```

## 3. Start the Application

```bash
npm start
```

The application will be available at `http://localhost:4200`

## 4. Default Routes

- `http://localhost:4200/` → Redirects to login
- `http://localhost:4200/auth/login` → Login page
- `http://localhost:4200/auth/register` → Registration page
- `http://localhost:4200/chat` → Chat interface (requires authentication)

## 5. Testing the Application

### Without Backend
The application will show authentication errors if the backend is not running. To test the UI:

1. Start only the frontend: `npm start`
2. You can view the login and registration pages
3. The chat page requires authentication

### With Backend
1. Start your backend server on `http://localhost:8000`
2. Start the frontend: `npm start`
3. Register a new account or login
4. Access the chat interface

## Features Overview

### Login/Register Pages
- Modern gradient design with purple/blue theme
- Form validation
- Error handling
- Smooth animations

### Chat Interface
- **Sidebar**:
  - New chat button
  - Session history
  - Dark/Light mode toggle
  - User menu with logout

- **Main Area**:
  - Message display with markdown support
  - Empty state with suggestions
  - Auto-scrolling to latest messages

- **Input Area**:
  - Text input with auto-resize
  - File attachment button
  - Send button
  - Keyboard shortcuts (Enter to send, Shift+Enter for new line)

### Theme Toggle
Click the theme toggle in the sidebar to switch between light and dark modes. The preference is saved in localStorage.

## Building for Production

```bash
npm run build
```

Output will be in `dist/frontend-angular/`

## Troubleshooting

### Port Already in Use
If port 4200 is already in use:
```bash
ng serve --port 4300
```

### Module Not Found Errors
Run:
```bash
npm install
```

### Styles Not Loading
Clear browser cache and restart the dev server.

## Next Steps

1. Ensure your backend API is running
2. Test authentication endpoints
3. Test chat functionality
4. Customize theme colors in `src/styles.scss`
5. Add your own features

For detailed documentation, see [SETUP.md](SETUP.md)

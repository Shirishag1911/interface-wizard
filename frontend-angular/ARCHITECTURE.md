# Application Architecture

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Angular 17 Application                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  Auth Module   │  │  Chat Module   │  │  Shared Module   │  │
│  ├────────────────┤  ├────────────────┤  ├──────────────────┤  │
│  │ - Login        │  │ - Chat         │  │ - API Service    │  │
│  │ - Register     │  │ - Message      │  │ - Theme Service  │  │
│  │ - Auth Service │  │ - Chat Service │  │                  │  │
│  │ - Auth Guard   │  │                │  │                  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    App Configuration                       │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │ - Routes (app.routes.ts)                                  │  │
│  │ - Providers (app.config.ts)                               │  │
│  │ - HTTP Interceptor (authInterceptor)                      │  │
│  │ - Material Theme                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests
                              ▼
                    ┌──────────────────┐
                    │  Backend API     │
                    │ localhost:8000   │
                    └──────────────────┘
```

## Component Hierarchy

```
AppComponent
│
├── RouterOutlet
    │
    ├── LoginComponent (auth/login)
    │   └── Material Form Components
    │
    ├── RegisterComponent (auth/register)
    │   └── Material Form Components
    │
    └── ChatComponent (chat) [Protected]
        ├── Sidenav (Sidebar)
        │   ├── New Chat Button
        │   ├── Session List
        │   │   └── Session Items (with delete)
        │   ├── Theme Toggle
        │   └── User Menu
        │
        ├── Main Content
        │   ├── Header
        │   ├── Messages Container
        │   │   └── MessageComponent (repeated)
        │   │       ├── Avatar
        │   │       ├── Role Name
        │   │       └── Content (Markdown)
        │   │
        │   └── Input Area
        │       ├── File Attachment Button
        │       ├── Text Input (Auto-resize)
        │       └── Send Button
```

## Data Flow

### Authentication Flow

```
User Input (Login/Register)
    │
    ▼
LoginComponent / RegisterComponent
    │
    ▼
AuthService.login() / register()
    │
    ▼
HTTP Request → Backend API
    │
    ▼
Response (JWT Token + User)
    │
    ▼
AuthService (Store in localStorage)
    │
    ├── Update currentUser$ Observable
    ├── Update isAuthenticated$ Observable
    │
    ▼
Navigate to /chat
```

### Chat Flow

```
User Types Message
    │
    ▼
ChatComponent.onSubmit()
    │
    ▼
ChatService.sendMessage()
    │
    ├── Optimistically add user message
    │   └── Update messages$ Observable
    │
    ▼
HTTP Request (with auth token) → Backend API
    │
    ▼
Response (Assistant Message)
    │
    ▼
ChatService
    │
    ├── Add assistant message to messages$
    ├── Update/Create session
    │
    ▼
UI Updates (Auto-scroll to bottom)
```

### Theme Toggle Flow

```
User Clicks Theme Toggle
    │
    ▼
ChatComponent.toggleTheme()
    │
    ▼
ThemeService.toggleTheme()
    │
    ├── Update isDarkMode$ Observable
    ├── Save to localStorage
    ├── Apply CSS class to body
    │   └── .dark-theme or .light-theme
    │
    ▼
CSS Variables Update
    │
    └── UI Re-renders with new colors
```

## Service Architecture

### AuthService

```typescript
class AuthService {
  // State Management
  - currentUser$: Observable<User | null>
  - isAuthenticated$: Observable<boolean>

  // Methods
  + login(email, password): Observable<AuthResponse>
  + register(username, email, password): Observable<AuthResponse>
  + logout(): void
  + getToken(): string | null
  + getCurrentUser(): User | null
}
```

### ChatService

```typescript
class ChatService {
  // State Management
  - messages$: Observable<Message[]>
  - sessions$: Observable<ChatSession[]>
  - currentSession$: Observable<ChatSession | null>
  - isLoading$: Observable<boolean>

  // Methods
  + loadSessions(): Observable<ChatSession[]>
  + loadSession(sessionId): Observable<Message[]>
  + sendMessage(request): Observable<SendMessageResponse>
  + createNewSession(): void
  + deleteSession(sessionId): Observable<void>
  + clearMessages(): void
}
```

### ThemeService

```typescript
class ThemeService {
  // State Management
  - isDarkMode$: Observable<boolean>

  // Methods
  + toggleTheme(): void
  + isDarkMode(): boolean
  - applyTheme(isDark): void
  - getInitialTheme(): boolean
}
```

## HTTP Interceptor Chain

```
HTTP Request
    │
    ▼
authInterceptor
    │
    ├── Get token from localStorage
    ├── Add Authorization header
    │   └── "Bearer {token}"
    │
    ▼
Request sent to Backend
    │
    ▼
Response received
    │
    └── Return to calling code
```

## Routing Guard Flow

```
Navigate to /chat
    │
    ▼
authGuard.canActivate()
    │
    ├── Check isAuthenticated$
    │
    ├─[YES]─→ Allow navigation to /chat
    │
    └─[NO]──→ Redirect to /auth/login
              (with returnUrl query param)
```

## State Management Pattern

```
Component
    │
    ├── Subscribe to Service Observable
    │   │
    │   ▼
    │   Service (BehaviorSubject)
    │       │
    │       ├── Initial Value
    │       ├── .next() to update
    │       └── .asObservable() for components
    │
    └── Display in Template
```

## Styling Architecture

```
styles.scss (Global)
    │
    ├── Google Fonts Import
    ├── Material Theme Configuration
    ├── CSS Custom Properties
    │   ├── Light Theme Variables
    │   └── Dark Theme Variables
    ├── Global Resets
    ├── Utility Classes
    └── Animations
        │
        ▼
Component SCSS
    │
    ├── Use CSS Variables
    ├── Component-specific styles
    └── Responsive breakpoints
```

## File Upload Flow

```
User Selects File
    │
    ▼
Input Change Event
    │
    ▼
ChatComponent.onFileSelected()
    │
    ├── Store file in component
    └── Show preview
        │
        ▼
User Sends Message
    │
    ▼
ChatService.sendMessage({ content, file })
    │
    ├── Create FormData
    ├── Append content
    ├── Append file
    │
    ▼
POST to /api/v1/chat/send
```

## Lazy Loading Strategy

```
Route Access
    │
    ▼
loadComponent(() => import('./path'))
    │
    ├── Component not loaded yet
    │   └── Download component bundle
    │
    ├── Component already loaded
    │   └── Use cached version
    │
    ▼
Render Component
```

## Error Handling Strategy

```
HTTP Error
    │
    ▼
Service Method (subscribe.error)
    │
    ├── Parse error message
    ├── Set component error state
    │
    ▼
Component Template
    │
    └── Display error message to user
```

## Build Process

```
Source Code (.ts, .html, .scss)
    │
    ▼
Angular Compiler
    │
    ├── TypeScript → JavaScript
    ├── Templates → Render Functions
    ├── SCSS → CSS
    │
    ▼
Bundler (Webpack/esbuild)
    │
    ├── Tree Shaking
    ├── Minification
    ├── Code Splitting
    │
    ▼
Production Bundle
    │
    └── dist/frontend-angular/
```

## Deployment Architecture

```
Production Environment
    │
    ├── Static File Server (Nginx/Apache)
    │   └── Serves Angular SPA
    │       └── index.html + JS/CSS bundles
    │
    └── Backend API Server
        └── Handles API requests
            └── http://your-api.com/api/v1
```

## Key Features Implementation

### Markdown Rendering
- Uses ngx-markdown library
- Configures in app.config.ts
- Renders in message.component.html

### Dark Mode
- ThemeService manages state
- CSS custom properties for colors
- Body class toggle (.dark-theme/.light-theme)
- Persisted in localStorage

### JWT Authentication
- Token stored in localStorage
- Auto-attached via HTTP interceptor
- Validated on protected routes
- Cleared on logout

### Reactive State
- BehaviorSubject for state storage
- Observable streams for components
- Async pipe in templates
- Automatic change detection

### File Upload
- File input (hidden)
- Preview before send
- FormData for multipart upload
- Optional per message

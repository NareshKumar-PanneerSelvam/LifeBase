# React Admin Client - LifeBase Workspace

This directory houses the React single-page application (SPA) built using **Vite**, **TypeScript**, **React Router v6**, and styled components. It serves as the frontend for the LifeBase secure administrative console.

---

## 🔑 Authentication Architecture

The client incorporates a secure, token-based session management workflow:

1.  **JWT Access Token**: Stored in memory and added automatically to the `Authorization: Bearer <token>` header of every outgoing request.
2.  **HttpOnly Session Cookie**: A refresh token is sent by the server via a secure, HttpOnly cookie.
3.  **Automatic Token Refresh Interceptor**:
    *   Located in [`src/services/api.ts`](file:///d:/LifeBase/client/src/services/api.ts).
    *   If a request fails with a `401 Unauthorized` status (due to an expired access token), the interceptor intercepts the failure, triggers a `POST /auth/refresh` request, updates the local storage, and retries the original request seamlessly.
    *   Handles concurrent requests during refresh by queueing them, preventing multiple redundant token refresh requests.

---

## 📂 Code Organization

*   **`src/components/`**: Layout modules and dynamic dashboard panels.
*   **`src/components/modules/`**: Dynamic module cards loaded into the dashboard via routing.
*   **`src/context/`**: React contexts, including `AuthContext.tsx` which manages login, signup, logout, and toast alerts.
*   **`src/services/`**: Network client brokers:
    *   `api.ts`: Base Axios instance with request and response interceptors.
    *   `tokenStorage.ts`: Handles caching token strings and user metadata in `localStorage`.
*   **`src/config/modulesConfig.ts`**: Central registry of modules (Logs, Passwords, Vocab, API Console) used to generate navigation items and dashboard metrics.

---

## 🛠️ Local Development Setup

### Prerequisite
*   Ensure **Node.js** (v18+) is installed on your computer.

### Step 1: Install Dependencies
```bash
npm install
```

### Step 2: Set Server Base URL
If your backend runs on a different port or host, update the `API_BASE_URL` in [`src/services/api.ts`](file:///d:/LifeBase/client/src/services/api.ts#L4):
```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### Step 3: Run Development Server
```bash
npm run dev
```
Open your browser and navigate to `http://localhost:5173`.

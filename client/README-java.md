## JavaFX Client (with Google Sign-In and Autotext Management)

This document outlines a JavaFX desktop client that connects to the FastAPI server, supports Google Sign-In, recording/uploading audio, and managing user-specific autotexts.

### Tech choices
- Java 17 LTS, Gradle
- JavaFX for UI (controls, WebView optional)
- Google Sign-In (OAuth 2.0 ID token via Desktop flow or embedded web)
- OkHttp (HTTP client), Jackson (JSON), TarsosDSP or JavaSound for recording

### Project skeleton
```
java-client/
  build.gradle.kts
  settings.gradle.kts
  src/main/java/com/ortho/App.java
  src/main/java/com/ortho/AuthController.java
  src/main/java/com/ortho/MainController.java
  src/main/java/com/ortho/ApiClient.java
  src/main/java/com/ortho/AudioRecorder.java
  src/main/resources/main.fxml
  src/main/resources/login.fxml
```

### Flow
1) User clicks "Sign in with Google" in JavaFX.
2) A WebView (or system browser) completes Google sign-in and returns an ID token.
3) Client posts the ID token to `/auth/google` to receive a server JWT.
4) JWT is used for profile calls (`/v1/profile/*`) and optionally passed on `/v1/transcribe` via `Authorization: Bearer <JWT>` so server applies user macros.
5) User can add/edit/delete autotexts. Recording uploads audio to `/v1/transcribe` (with `X-API-Key` as well).

### Google OAuth setup
1) Create an OAuth 2.0 Client ID in Google Cloud Console for Desktop App.
2) The client obtains an `id_token` after user login. For desktop, you can:
   - Use Google Identity OIDC in a WebView: exchange the credential for an ID token
   - Or run an OAuth installed app flow via system browser and local redirect
3) Post `id_token` to server `/auth/google` to get a JWT.

### Build commands (example)
```
cd java-client
./gradlew run
```

### Notes
- The server still requires `X-API-Key` for `/v1/transcribe`. JWT is for profile and user-specific macros.
- Save JWT securely (e.g., OS keychain) and refresh by re-login when expired.


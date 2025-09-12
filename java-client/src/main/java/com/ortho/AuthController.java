package com.ortho;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.stage.Stage;

import java.io.IOException;
import java.util.Properties;

public class AuthController {
    @FXML
    private Label statusLabel;

    private ApiClient api;

    @FXML
    public void initialize() throws IOException {
        Properties p = new Properties();
        p.load(getClass().getResourceAsStream("/app.properties"));
        String url = p.getProperty("serverUrl");
        String apiKey = p.getProperty("apiKey");
        api = new ApiClient(url, apiKey);
    }

    @FXML
    public void onGoogleSignIn(ActionEvent e) {
        try {
            // Placeholder for real Google sign-in flow; here you would
            // acquire an ID token using OAuth Installed App (PKCE) or WebView.
            // For demo, assume we have an ID token string.
            String idToken = obtainIdTokenInteractive();
            String jwt = api.googleAuth(idToken);
            statusLabel.setText("Signed in.");

            // Open main UI
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/main.fxml"));
            Scene scene = new Scene(loader.load(), 900, 600);
            MainController mc = loader.getController();
            mc.setApi(api);

            Stage stage = (Stage) statusLabel.getScene().getWindow();
            stage.setScene(scene);
        } catch (Exception ex) {
            statusLabel.setText("Sign-in failed: " + ex.getMessage());
        }
    }

    private String obtainIdTokenInteractive() throws Exception {
        // TODO: Implement Google OAuth Desktop flow (PKCE) to obtain id_token.
        // For now, throw to prompt implementation.
        throw new IllegalStateException("Google OAuth flow not implemented yet.");
    }
}


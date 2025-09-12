package com.ortho;

import com.fasterxml.jackson.databind.JsonNode;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.*;

import java.io.File;
import java.nio.file.Files;

public class MainController {
    @FXML private ChoiceBox<String> providerChoice;
    @FXML private TextArea transcriptArea;
    @FXML private TableView<JsonNode> autotextTable;
    @FXML private TableColumn<JsonNode, String> triggerCol;
    @FXML private TableColumn<JsonNode, String> expansionCol;
    @FXML private TextField triggerField;
    @FXML private TextField expansionField;
    @FXML private Label statusLabel;

    private ApiClient api;
    private final ObservableList<JsonNode> autotexts = FXCollections.observableArrayList();

    public void setApi(ApiClient api) {
        this.api = api;
        initUi();
        refreshAutotexts();
    }

    private void initUi() {
        providerChoice.setItems(FXCollections.observableArrayList("", "openai", "deepgram", "faster_whisper"));
        triggerCol.setCellValueFactory(cell -> new javafx.beans.property.SimpleStringProperty(cell.getValue().get("trigger").asText("")));
        expansionCol.setCellValueFactory(cell -> new javafx.beans.property.SimpleStringProperty(cell.getValue().get("expansion").asText("")));
        autotextTable.setItems(autotexts);
    }

    @FXML
    public void onRecord(ActionEvent e) {
        statusLabel.setText("Recording (placeholder)...");
        // TODO: implement Java sound capture and write to temp .wav file.
    }

    @FXML
    public void onStop(ActionEvent e) {
        try {
            // TODO: point to recorded wav path
            File wav = File.createTempFile("dictation_", ".wav");
            Files.write(wav.toPath(), new byte[]{}); // placeholder
            String text = api.transcribe(wav, providerChoice.getValue(), "en");
            transcriptArea.setText(text);
            statusLabel.setText("Transcribed.");
        } catch (Exception ex) {
            statusLabel.setText("Transcription failed: " + ex.getMessage());
        }
    }

    @FXML
    public void onRefreshAutotexts() {
        refreshAutotexts();
    }

    private void refreshAutotexts() {
        try {
            JsonNode arr = api.listAutotexts();
            autotexts.setAll(arr.findValues("")); // We will repopulate manually below
            autotexts.clear();
            for (JsonNode item : arr) {
                autotexts.add(item);
            }
            statusLabel.setText("Loaded autotexts.");
        } catch (Exception ex) {
            statusLabel.setText("Load failed: " + ex.getMessage());
        }
    }

    @FXML
    public void onAddAutotext() {
        try {
            JsonNode item = api.createAutotext(triggerField.getText(), expansionField.getText());
            autotexts.add(item);
            triggerField.clear();
            expansionField.clear();
        } catch (Exception ex) {
            statusLabel.setText("Add failed: " + ex.getMessage());
        }
    }

    @FXML
    public void onUpdateAutotext() {
        JsonNode sel = autotextTable.getSelectionModel().getSelectedItem();
        if (sel == null) return;
        try {
            int id = sel.get("id").asInt();
            JsonNode upd = api.updateAutotext(id, triggerField.getText(), expansionField.getText());
            int idx = autotexts.indexOf(sel);
            autotexts.set(idx, upd);
        } catch (Exception ex) {
            statusLabel.setText("Update failed: " + ex.getMessage());
        }
    }

    @FXML
    public void onDeleteAutotext() {
        JsonNode sel = autotextTable.getSelectionModel().getSelectedItem();
        if (sel == null) return;
        try {
            int id = sel.get("id").asInt();
            api.deleteAutotext(id);
            autotexts.remove(sel);
        } catch (Exception ex) {
            statusLabel.setText("Delete failed: " + ex.getMessage());
        }
    }

    @FXML
    public void onSignOut() {
        // Simple sign out: drop JWT and return to login screen
        try {
            Platform.runLater(() -> {
                try {
                    javafx.fxml.FXMLLoader loader = new javafx.fxml.FXMLLoader(getClass().getResource("/login.fxml"));
                    javafx.scene.Scene scene = new javafx.scene.Scene(loader.load(), 640, 420);
                    ((javafx.stage.Stage) statusLabel.getScene().getWindow()).setScene(scene);
                } catch (Exception ex) {
                    statusLabel.setText("Sign out failed: " + ex.getMessage());
                }
            });
        } catch (Exception ignored) {}
    }
}


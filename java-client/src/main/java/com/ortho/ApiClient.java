package com.ortho;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.*;

import java.io.File;
import java.io.IOException;
import java.util.Objects;

public class ApiClient {
    private final OkHttpClient http = new OkHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();
    private final String serverUrl;
    private final String apiKey;
    private String jwt;

    public ApiClient(String serverUrl, String apiKey) {
        this.serverUrl = serverUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
    }

    public void setJwt(String jwt) { this.jwt = jwt; }

    public String googleAuth(String idToken) throws IOException {
        RequestBody form = new FormBody.Builder()
                .add("id_token", idToken)
                .build();
        Request req = new Request.Builder()
                .url(serverUrl + "/auth/google")
                .post(form)
                .build();
        try (Response resp = http.newCall(req).execute()) {
            if (!resp.isSuccessful()) throw new IOException("Auth failed: " + resp);
            JsonNode node = mapper.readTree(Objects.requireNonNull(resp.body()).string());
            String token = node.get("token").asText();
            this.jwt = token;
            return token;
        }
    }

    public JsonNode listAutotexts() throws IOException {
        Request req = new Request.Builder()
                .url(serverUrl + "/v1/profile/autotexts")
                .header("Authorization", "Bearer " + jwt)
                .build();
        try (Response resp = http.newCall(req).execute()) {
            if (!resp.isSuccessful()) throw new IOException("listAutotexts failed: " + resp);
            return mapper.readTree(Objects.requireNonNull(resp.body()).string());
        }
    }

    public JsonNode createAutotext(String trigger, String expansion) throws IOException {
        MediaType json = MediaType.parse("application/json");
        String payload = String.format("{\"trigger\":\"%s\",\"expansion\":\"%s\"}", trigger.replace("\"","\\\""), expansion.replace("\"","\\\""));
        Request req = new Request.Builder()
                .url(serverUrl + "/v1/profile/autotexts")
                .header("Authorization", "Bearer " + jwt)
                .post(RequestBody.create(payload, json))
                .build();
        try (Response resp = http.newCall(req).execute()) {
            if (!resp.isSuccessful()) throw new IOException("createAutotext failed: " + resp);
            return mapper.readTree(Objects.requireNonNull(resp.body()).string());
        }
    }

    public JsonNode updateAutotext(int id, String trigger, String expansion) throws IOException {
        MediaType json = MediaType.parse("application/json");
        String payload = String.format("{\"trigger\":\"%s\",\"expansion\":\"%s\"}", trigger.replace("\"","\\\""), expansion.replace("\"","\\\""));
        Request req = new Request.Builder()
                .url(serverUrl + "/v1/profile/autotexts/" + id)
                .header("Authorization", "Bearer " + jwt)
                .put(RequestBody.create(payload, json))
                .build();
        try (Response resp = http.newCall(req).execute()) {
            if (!resp.isSuccessful()) throw new IOException("updateAutotext failed: " + resp);
            return mapper.readTree(Objects.requireNonNull(resp.body()).string());
        }
    }

    public void deleteAutotext(int id) throws IOException {
        Request req = new Request.Builder()
                .url(serverUrl + "/v1/profile/autotexts/" + id)
                .header("Authorization", "Bearer " + jwt)
                .delete()
                .build();
        try (Response resp = http.newCall(req).execute()) {
            if (!resp.isSuccessful()) throw new IOException("deleteAutotext failed: " + resp);
        }
    }

    public String transcribe(File wavFile, String provider, String language) throws IOException {
        MediaType octet = MediaType.parse("application/octet-stream");
        MultipartBody.Builder mb = new MultipartBody.Builder().setType(MultipartBody.FORM)
                .addFormDataPart("provider", provider == null ? "" : provider)
                .addFormDataPart("language", language == null ? "" : language)
                .addFormDataPart("commands", "true")
                .addFormDataPart("file", wavFile.getName(), RequestBody.create(wavFile, octet));
        Request.Builder rb = new Request.Builder()
                .url(serverUrl + "/v1/transcribe")
                .post(mb.build())
                .header("X-API-Key", apiKey);
        if (jwt != null) rb.header("Authorization", "Bearer " + jwt);
        try (Response resp = http.newCall(rb.build()).execute()) {
            if (!resp.isSuccessful()) throw new IOException("transcribe failed: " + resp);
            JsonNode node = mapper.readTree(Objects.requireNonNull(resp.body()).string());
            return node.get("text").asText("");
        }
    }
}


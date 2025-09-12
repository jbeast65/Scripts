package com.ortho;

import javax.sound.sampled.*;
import java.io.File;
import java.io.IOException;

public class AudioRecorder {
    private TargetDataLine line;
    private AudioFormat format;

    public AudioRecorder() {
        format = new AudioFormat(16000, 16, 1, true, false);
    }

    public void start() throws LineUnavailableException {
        DataLine.Info info = new DataLine.Info(TargetDataLine.class, format);
        line = (TargetDataLine) AudioSystem.getLine(info);
        line.open(format);
        line.start();
        new Thread(() -> {
            // Capture thread runs until stop() closes the line
        }, "AudioCapture").start();
    }

    public File stopToWav() throws IOException {
        if (line == null) return null;
        File wav = File.createTempFile("dictation_", ".wav");
        AudioInputStream ais = new AudioInputStream(line);
        try {
            AudioSystem.write(ais, AudioFileFormat.Type.WAVE, wav);
        } finally {
            line.stop();
            line.close();
            line = null;
        }
        return wav;
    }
}


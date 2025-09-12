plugins {
    application
    id("org.openjfx.javafx-plugin") version "0.1.0"
}

repositories {
    mavenCentral()
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

dependencies {
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.1")
    implementation("com.fasterxml.jackson.core:jackson-annotations:2.17.1")
    implementation("com.fasterxml.jackson.core:jackson-core:2.17.1")
}

application {
    mainClass.set("com.ortho.App")
}

javafx {
    version = "21.0.3"
    modules = listOf("javafx.controls", "javafx.fxml", "javafx.web")
}

tasks.withType<JavaExec> {
    jvmArgs = listOf("--add-exports=javafx.graphics/com.sun.javafx.css=ALL-UNNAMED")
}


plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.serialization)
    application
}

group = "warmhouse"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation(libs.ktor.server.netty)
    implementation(libs.ktor.server.content.negotiation)
    implementation(libs.ktor.serialization.kotlinx.json)
    implementation(libs.exposed.core)
    implementation(libs.exposed.jdbc)
    implementation(libs.exposed.kotlin.datetime)
    implementation(libs.kotlinx.datetime)
    implementation(libs.kafka.clients)
    implementation(libs.hikaricp)
    implementation(libs.postgresql)
    implementation(libs.logback.classic)
}

kotlin {
    jvmToolchain(21)
}

application {
    mainClass.set("warmhouse.telemetry.MainKt")
}

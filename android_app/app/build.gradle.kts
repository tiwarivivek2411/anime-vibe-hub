// app/build.gradle.kts
plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    compileSdk = 34
    defaultConfig {
        applicationId = "com.example.animewallpaper"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")
    // Add any networking libraries later, e.g., Retrofit, OkHttp
}

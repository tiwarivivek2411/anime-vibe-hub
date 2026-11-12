# 🌌 VibeHub Hub - Multiverse Desktop Visualizer

VibeHub is a high-performance, cross-platform wallpaper management suite designed for power users who want a deep, organized, and thematic desktop experience.

## ✨ Key Features

- **Multiverse Collections**: Native support for **Anime**, **TV Shows**, and **Movies**.
- **Discovery Engine**: Built-in search tab for unlimited real-time visual syncing.
- **Resolution Guard**: Automated MacBook-native filtering (Portrait/Low-res rejection).
- **HD Preview Modal**: Double-click any image for a crisp, wide-screen preview.
- **Vibe Favorites**: Bookmark your top visuals with a single right-click (★).
- **Background Tray Icon**: Minimize to your macOS/Windows tray for seamless activity.
- **VibeEngine 2.5**: Intelligent, persistent background wallpaper rotation.

## 🛠 Project Architecture

- `app_gui.py`: The core Electron-style Python interface (CustomTkinter).
- `set_wallpaper.py`: OS-agnostic hardware bridge (macOS/Win/Linux).
- `scripts/seed_universe.py`: Automated visual acquisition engine.
- `media_library/`: Hierarchical local data lake.

## 🚀 Getting Started

### 1. Quick Start (Terminal)
```bash
./start_vibehub.sh
```

### 2. Native macOS Installation
1. Run `./scripts/build_app.sh`.
2. Find `VibeHub.app` in the `dist/` directory.
3. Move to `/Applications`.

## 📈 Roadmap
- [x] V1.0 - Core macOS Implementation
- [x] V1.2 - Multiverse Expansion (Shows/Movies)
- [x] V1.3 - GUI Pro (Search & Persistence)
- [ ] V2.0 - Android Companion App
- [ ] V2.5 - Cloud Metadata Sink

---
*Created during a high-speed development sprint.*

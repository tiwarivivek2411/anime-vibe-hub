[app]
title = VibeHub
package.name = vibehub
package.domain = org.vibe
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 2.0.0

requirements = python3,kivy,requests,pillow,certifi

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = INTERNET, SET_WALLPAPER, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1

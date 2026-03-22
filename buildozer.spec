[app]
title = Project Soldier
package.name = projectsoldier
package.domain = org.projectsoldier
source.dir = .
source.include_exts = py,png,jpg,jpeg,mp3,wav,txt,ttf
source.exclude_dirs = tests, bin, venv, .venv, .git, .buildozer, venv_buildozer
version = 0.1
requirements = python3, pygame-ce
orientation = portrait
android.permissions = INTERNET, VIBRATE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
fullscreen = 1
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1

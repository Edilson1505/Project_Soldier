[app]

# (str) Title of your application
title = Project Soldier

# (str) Package name
package.name = projectsoldier

# (str) Package domain (needed for android/ios packaging)
package.domain = org.projectsoldier

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,mp3,wav,txt,ttf

# (list) List of directory to exclude (let empty to include all the files)
source.exclude_dirs = tests, bin, venv, .venv, .git, .buildozer, venv_buildozer

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3, pygame-ce

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, VIBRATE

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) Architecture to build for
android.archs = arm64-v8a

# (bool) indicates if the application should be fullscreen or not
fullscreen = 1

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

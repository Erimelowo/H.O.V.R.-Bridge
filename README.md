# H.O.V.R. Bridge
A bridge application to enable [H.O.V.R.](https://payhip.com/b/nDEYw) to work in VRChat using OSC or Resonite using a WebSocket.  

This was forked from [VRC-Haptic-Pancake](https://github.com/Z4urce/VRC-Haptic-Pancake) and rebranded using H.O.V.R.'s branding but is still compatible with it.

# Getting the hardware
You can either buy H.O.V.R. [here](https://payhip.com/b/nDEYw) for US$39 + shipping if you live in North America or you can [make it yourself](https://github.com/Z4urce/VRC-Haptic-Pancake/wiki/Make-the-Pancake).

# Avatar setup
Avatar setup is a drag and drop using [VRCFury](https://vrcfury.com/download) and a prefab available [here](https://payhip.com/b/Ye28f).

# Setting up the software
You can download the latest version from the Releases of [here](https://github.com/Erimelowo/H.O.V.R.-Bridge/releases/latest/download/HOVR-Bridge.exe) directly.

Then just put HOVR-Bridge.exe in a folder and run it.

## Starting automatically with SteamVR
Put [manifest.vrmanifest](manifest.vrmanifest) in the same folder as HOVR-Bridge.exe and run it with SteamVR. Then go in SteamVR Startup/Shutdown settings and you can set it so that it runs automatically with SteamVR.

## Starting automatically with VRChat
You can use VRCX's App Launcher in its advanced settings to automatically launch the HOVR-Bridge with VRChat.

# Building the software yourself
If you want to build the software yourself, simply clone the repo, run `pip install -r BridgeApp\requirements.txt`, run `pip install pyinstaller`, then just run `.\build.bat` to build the app.  

The resulting binary will be at `dist\HOVR-Bridge.exe`

# Credits
- This app has been forked from [VRC-Haptic-Pancake by Z4urce](https://github.com/Z4urce/VRC-Haptic-Pancake).
- The license is the GNU General Public License from the original project.

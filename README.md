# Qt5DeviceConfigurator
A simple frontend for setting mice, keyboard and monitor.

Version 0.8 - Testing

Required:
- python3
- PyQt5
- xinput
- xset
- setxkbmap
- optional: arandr

This program let user to settings mice, keyboard and monitor overriding default settings. All settings can be applied only, or a bash script and a desktop file can be created (in the HOME folder) to be used to use custom options as desired. The desktop file can be placed in the autostart folder.

Mouse: configuration is per mouse, so different configurations can be used for different mice.

The 'Test' button is for getting the actual used configuration. The 'Reset' button is for reset all value to the starting ones. The 'Apply' button let user to apply the settings immediately, or for creating bash scripts and desktop file, for mouse, keyboard and monitor. For monitor resolution and other the program arandr is needed, or others if setted. At the beginning of the python script some options can be changed.

This program cannot be change the settings globally, only for user. So, all changes will be lost after logout/login and reboot. The bash scripts and the desktop files are for apply the custom setting at login.

Screenshots:

![My image](https://github.com/frank038/Qt5DeviceConfigurator/blob/main/image1.png)
![My image](https://github.com/frank038/Qt5DeviceConfigurator/blob/main/image2.png)
![My image](https://github.com/frank038/Qt5DeviceConfigurator/blob/main/image3.png)

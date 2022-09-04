# Qt5DeviceConfigurator
A simple frontend for setting mice, keyboard and monitor.

Version 0.9

Required:
- python3
- PyQt5
- xinput
- xset
- setxkbmap
- optional: arandr (or similar program).

This program let user set mice, keyboard and monitor overriding default settings. All settings can only be applied, or a bash script and a desktop file can be created (in the HOME folder). The desktop file can be placed in the autostart folder.

Mouse: configuration is per mouse, so different configurations can be used for different mice.

The 'Test' button is for getting the actual used configuration. The 'Reset' button is for reset all value to the starting ones. The 'Apply' button let user apply the settings immediately, or for creating bash scripts and desktop file, for mouse, keyboard and monitor. For monitor resolutions and other monitor settings the program arandr is needed, or others if setted. At the beginning of the python script some options can be changed.

This program cannot change the settings globally, only for user. So, all changes will be lost after logout/login and reboot. The bash scripts and the desktop files are for apply the custom setting at login or when requested.

Can also change the monitor resolution and rate. In this case, without further confirmation, the previous settings will be applied.

Screenshots:

![My image](https://github.com/frank038/Qt5DeviceConfigurator/blob/main/image1.png)
![My image](https://github.com/frank038/Qt5DeviceConfigurator/blob/main/image2.png)
![My image](https://github.com/frank038/Qt5DeviceConfigurator/blob/main/image3.png)

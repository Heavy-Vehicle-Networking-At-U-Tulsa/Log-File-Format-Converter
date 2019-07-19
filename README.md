# Log-File-Format-Converter
A GUI for converting different types of log files to the Tuck Cape format
This version is for converting encrypted data from CAN Logger 3 AES CBC
The IV and Key are stored in the baudrate.txt from the Logger 3 SD card. They need to be hard coded in the Converter Python Source Code. This is for testing the AES function
The IV and Key ideally will be transmitted via envelope encryption

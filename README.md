# SystemPulse

A Windows system diagnostics and optimization tool with a modern dark-themed GUI.

## Features

- **CPU Core Inspector** - Analyze physical CPU cores and configuration
- **Disk Health Scan** - Check disk integrity and corruption
- **USB Chipset Mapper** - Map USB controllers and latency info
- **Network Latency Tester** - Test network response times
- **Driver Registry Viewer** - Browse driver registry keys
- **Dependency Map** - Visualize Windows service dependencies

## Requirements

- Windows 10/11
- Python 3.10+

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Or download the pre-built executable from [Releases](https://github.com/yourusername/SystemPulse/releases).

## Building Executable

```bash
pyinstaller --onefile --windowed --name SystemPulse --icon resources/icon.ico --add-data resources;resources main.py
```

The executable will be created in the `dist/` folder.

## License

MIT License

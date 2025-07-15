# General PDF Filler for Claude Desktop

This repository contains two main components:
1. **Chrome MCP Setup** - Control Chrome browser from Claude Desktop
2. **PDF Form Automation** - Map and fill PDF forms programmatically

## 📄 PDF Form Automation

The `pdfmcp/` folder contains tools for mapping and filling PDF forms automatically.

### Features
- Visual PDF form field mapper with drawing interface
- Targetid-based folder organization
- Timestamp-based output naming (no conflicts)
- Support for text fields, checkboxes, and numbered condition boxes

### Quick Start
1. Place blank PDF in `pdfmcp/blanks and json/` folder
2. Run `form_field_mapper_v4.py` to create field mappings
3. Use `enhanced_pdf_filler_v3.py` to fill forms programmatically

See [pdfmcp/README_FOLDER_STRUCTURE.md](pdfmcp/README_FOLDER_STRUCTURE.md) for detailed documentation.

---

## 🌐 Chrome MCP for Claude Desktop on Windows

Quick setup for using Claude Desktop to control Chrome on Windows.

### Prerequisites
- Windows 10/11
- Claude Desktop app
- Chrome browser
- Node.js (https://nodejs.org/)

### Setup Instructions

#### 1. Install Chrome MCP Bridge (PowerShell Admin)
```powershell
npm install -g mcp-chrome-bridge
```

#### 2. Load Chrome Extension
1. Download from: https://github.com/hangwin/mcp-chrome/releases
2. Open Chrome → `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked" → Select extension folder
5. Copy the Extension ID

#### 3. Register Extension
```powershell
mcp-chrome-bridge register
# Enter your Extension ID when prompted
```

#### 4. Configure Claude Desktop
1. Copy `claude_desktop_config.json` from this repo
2. Edit the file - replace `YOUR_USERNAME` with your Windows username
3. Save to: `%APPDATA%\Claude\claude_desktop_config.json`
4. Restart Claude Desktop

#### 5. Connect
1. Open Chrome
2. Click Chrome MCP extension → "Connect"
3. Should show "Connected" on port 12306
4. In Claude Desktop: Chrome tools should be available

### Configuration File

Save this as `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "chrome-mcp": {
      "command": "node",
      "args": ["C:\\Users\\YOUR_USERNAME\\AppData\\Roaming\\npm\\node_modules\\mcp-chrome-bridge\\dist\\mcp\\mcp-server-stdio.js"]
    }
  }
}
```

Replace `YOUR_USERNAME` with your actual Windows username.

### Troubleshooting

#### Can't find mcp-server-stdio.js
```powershell
# Find the correct path
dir C:\Users\%USERNAME%\AppData\Roaming\npm\node_modules\mcp-chrome-bridge\dist\mcp\
```

#### Extension shows "NATIVE_DISCONNECTED"
```powershell
# Reinstall
npm uninstall -g mcp-chrome-bridge
npm install -g mcp-chrome-bridge
mcp-chrome-bridge register
```

#### Claude Desktop doesn't show Chrome tools
1. Verify config file is in correct location: `%APPDATA%\Claude\`
2. Check path in config matches your installation
3. Restart Claude Desktop completely
4. Ensure Chrome extension shows "Connected"

### For Multiple Computers

1. Note your Extension ID: `YOUR_EXTENSION_ID`
2. Note your Windows username for each computer
3. Copy this README
4. Update username in config file for each computer
5. Follow steps 1-5 on each machine

## 📁 Repository Structure

```
.
├── README.md                    # This file
├── claude_desktop_config.json   # Claude Desktop configuration template
├── LICENSE                      # MIT License
└── pdfmcp/                     # PDF Form Automation
    ├── form_field_mapper_v4.py # Visual mapping tool
    ├── enhanced_pdf_filler_v3.py # Form filling tool
    ├── README_FOLDER_STRUCTURE.md # Detailed documentation
    └── blanks and json/        # Store blank PDFs and mappings here
```

## Requirements

### For PDF Automation
- Python 3.7+
- PyMuPDF (`pip install pymupdf`)
- Pillow (`pip install pillow`)
- tkinter (usually included with Python)

### For Chrome MCP
- Node.js 18.19.0+
- Chrome browser
- Claude Desktop app
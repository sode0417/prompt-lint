# Zed Editor Integration

## Setup

1. Install prompt-lint with LSP support:
   ```bash
   pip install prompt-lint[lsp]
   ```

2. Add to your Zed `settings.json` (`Ctrl+,` or `Cmd+,`):

```json
{
  "lsp": {
    "prompt-lint": {
      "binary": {
        "path": "prompt-lint-lsp"
      }
    }
  },
  "languages": {
    "Markdown": {
      "language_servers": ["prompt-lint", "..."]
    }
  },
  "file_types": {
    "Markdown": ["prompt.md"]
  }
}
```

**Note:** If `prompt-lint-lsp` is not on your PATH, use the full path:
```json
"path": "C:\\Users\\<user>\\AppData\\Local\\...\\Scripts\\prompt-lint-lsp.exe"
```

## Features

- Real-time error/warning diagnostics (red/yellow squiggles)
- Hover over `{{variable}}` to see its definition from the Input section
- Type `{{` to get variable name completions
- Type `# ` to get section heading completions

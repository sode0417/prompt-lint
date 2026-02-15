# VS Code Extension for prompt-lint

## Setup

1. Install prompt-lint with LSP support:
   ```bash
   pip install prompt-lint[lsp]
   ```

2. Build and install the extension:
   ```bash
   cd editors/vscode
   npm install
   npm run compile
   ```

3. Copy the `editors/vscode` folder to your VS Code extensions directory, or use `vsce package` to create a `.vsix` file.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `promptLint.serverPath` | `prompt-lint-lsp` | Path to the LSP server executable |

If `prompt-lint-lsp` is not on your PATH, set the full path in settings:
```json
{
  "promptLint.serverPath": "C:\\Users\\<user>\\...\\Scripts\\prompt-lint-lsp.exe"
}
```

## Features

- Real-time error/warning diagnostics on `.prompt.md` files
- Hover over `{{variable}}` to see its Input definition
- `{{` triggers variable name completions
- `# ` triggers section heading completions

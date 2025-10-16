# VS Code Extension - TypeScript Stack

## Overview

TypeScript-based stack for building Visual Studio Code extensions with rich IDE integration capabilities.

## Use Cases

- **Ideal For:**
  - Developer productivity tools
  - Language support extensions
  - Code snippet managers
  - Linters and formatters integration
  - Custom debugging tools
  - Workspace management tools
  - Git/SCM integrations
  - AI/ML-powered coding assistants

- **Not Ideal For:**
  - Web applications
  - Mobile apps
  - Data processing pipelines
  - Standalone desktop applications

## Tech Stack

- **Language:** TypeScript 5+
- **Framework:** VS Code Extension API
- **Build Tool:** esbuild or webpack
- **Testing:** @vscode/test-electron, Mocha
- **Package Manager:** npm or pnpm
- **Publishing:** vsce (VS Code Extensions CLI)

## Project Structure

```
extension/
├── src/
│   ├── extension.ts           # Main entry point
│   ├── commands/               # Command implementations
│   ├── providers/              # Language providers
│   ├── views/                  # Webview components
│   └── utils/                  # Utilities
├── resources/                  # Icons, assets
├── test/
│   └── suite/                  # Test suites
├── package.json                # Extension manifest
├── tsconfig.json
├── .vscodeignore
└── README.md
```

## Key Features

### Extension Activation

```typescript
// src/extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  console.log('Extension activated');

  // Register command
  const disposable = vscode.commands.registerCommand(
    'myExtension.helloWorld',
    () => {
      vscode.window.showInformationMessage('Hello from Extension!');
    }
  );

  context.subscriptions.push(disposable);
}

export function deactivate() {
  console.log('Extension deactivated');
}
```

### Language Provider

```typescript
// src/providers/completionProvider.ts
import * as vscode from 'vscode';

export class MyCompletionProvider implements vscode.CompletionItemProvider {
  provideCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position
  ): vscode.CompletionItem[] {
    const items: vscode.CompletionItem[] = [];

    const item = new vscode.CompletionItem('mySnippet');
    item.kind = vscode.CompletionItemKind.Snippet;
    item.insertText = new vscode.SnippetString('console.log($1);');
    item.documentation = new vscode.MarkdownString('Logs to console');

    items.push(item);
    return items;
  }
}
```

### Webview Panel

```typescript
// src/views/webviewPanel.ts
import * as vscode from 'vscode';

export class MyWebviewPanel {
  public static createOrShow(extensionUri: vscode.Uri) {
    const panel = vscode.window.createWebviewPanel(
      'myView',
      'My View',
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [extensionUri]
      }
    );

    panel.webview.html = this.getWebviewContent();
  }

  private static getWebviewContent(): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>My Extension</title>
      </head>
      <body>
        <h1>Hello from Webview!</h1>
        <button onclick="sendMessage()">Click Me</button>
        <script>
          const vscode = acquireVsCodeApi();
          function sendMessage() {
            vscode.postMessage({ type: 'buttonClicked' });
          }
        </script>
      </body>
      </html>
    `;
  }
}
```

## Configuration

### package.json

```json
{
  "name": "my-extension",
  "displayName": "My Extension",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": ["Other"],
  "activationEvents": ["onCommand:myExtension.helloWorld"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "myExtension.helloWorld",
        "title": "Hello World"
      }
    ],
    "configuration": {
      "title": "My Extension",
      "properties": {
        "myExtension.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable extension"
        }
      }
    }
  },
  "scripts": {
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "package": "vsce package",
    "publish": "vsce publish"
  },
  "devDependencies": {
    "@types/vscode": "^1.80.0",
    "@types/node": "^18.x",
    "typescript": "^5.0.0",
    "@vscode/test-electron": "^2.3.0"
  }
}
```

## Testing

```typescript
// test/suite/extension.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
  test('Command should be registered', async () => {
    const commands = await vscode.commands.getCommands();
    assert.ok(commands.includes('myExtension.helloWorld'));
  });
});
```

## Coding Standards

**Reference:** `.languages/ts-js/principles.md`

## Deployment

```bash
# Package extension
vsce package

# Publish to marketplace
vsce publish
```

## Learning Resources

- VS Code API: https://code.visualstudio.com/api
- Extension Guides: https://code.visualstudio.com/api/extension-guides/overview
- Refer to `.languages/ts-js/principles.md`

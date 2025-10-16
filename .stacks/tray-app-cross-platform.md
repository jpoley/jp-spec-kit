# System Tray Applications (Windows & macOS)

## Overview

Cross-platform or platform-specific system tray applications for Windows and macOS, providing background services with UI integration.

## Use Cases

- **Ideal For:**
  - Background monitoring tools
  - Quick access utilities
  - System notifications
  - Menu bar/system tray widgets
  - Clipboard managers
  - Screenshot tools
  - Music/media controls
  - VPN clients
  - Cloud sync clients

- **Not Ideal For:**
  - Full-featured desktop applications
  - Web applications
  - Mobile apps
  - Data processing pipelines

## Technology Options

### Cross-Platform

#### Electron + TypeScript
- **Best For:** Complex UI, web technologies
- **Pros:** One codebase, rich ecosystem, web technologies
- **Cons:** Large bundle size, higher memory usage
- **Example:** Slack, Discord system tray

```typescript
// main.ts
import { app, Tray, Menu, nativeImage } from 'electron';
import path from 'path';

let tray: Tray | null = null;

app.whenReady().then(() => {
  const icon = nativeImage.createFromPath(
    path.join(__dirname, 'icon.png')
  );

  tray = new Tray(icon);

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show', click: () => showWindow() },
    { label: 'Settings', click: () => openSettings() },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ]);

  tray.setToolTip('My Tray App');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    showWindow();
  });
});
```

#### Tauri + Rust/TypeScript
- **Best For:** Performance-focused, smaller bundle
- **Pros:** Smaller size, better performance, Rust security
- **Cons:** Smaller ecosystem, more complex setup
- **Example:** Modern lightweight apps

```rust
// src-tauri/src/main.rs
use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, SystemTrayEvent};
use tauri::Manager;

fn main() {
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(quit);

    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                }
                "quit" => {
                    std::process::exit(0);
                }
                _ => {}
            },
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Platform-Specific

#### macOS (Swift + SwiftUI)
- **Best For:** Native macOS experience
- **Pros:** Native performance, native APIs, smaller size
- **Cons:** macOS only

```swift
// AppDelegate.swift
import Cocoa
import SwiftUI

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem?
    var popover: NSPopover?

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Create status bar item
        statusItem = NSStatusBar.system.statusItem(
            withLength: NSStatusItem.variableLength
        )

        if let button = statusItem?.button {
            button.image = NSImage(systemSymbolName: "star.fill", accessibilityDescription: "My App")
            button.action = #selector(togglePopover)
        }

        // Create popover
        popover = NSPopover()
        popover?.contentViewController = NSHostingController(
            rootView: ContentView()
        )
        popover?.behavior = .transient
    }

    @objc func togglePopover() {
        if let button = statusItem?.button {
            if popover?.isShown == true {
                popover?.performClose(nil)
            } else {
                popover?.show(
                    relativeTo: button.bounds,
                    of: button,
                    preferredEdge: .minY
                )
            }
        }
    }
}

// ContentView.swift
struct ContentView: View {
    var body: some View {
        VStack {
            Text("My Tray App")
                .font(.headline)
            Button("Action") {
                performAction()
            }
            Button("Quit") {
                NSApplication.shared.terminate(nil)
            }
        }
        .frame(width: 300, height: 200)
        .padding()
    }

    func performAction() {
        // Do something
    }
}
```

#### Windows (.NET C# / Go)

##### .NET WPF/WinForms
```csharp
// Program.cs using .NET
using System;
using System.Windows.Forms;

namespace TrayApp
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            var trayIcon = new NotifyIcon
            {
                Icon = new System.Drawing.Icon("icon.ico"),
                ContextMenuStrip = new ContextMenuStrip
                {
                    Items =
                    {
                        new ToolStripMenuItem("Show", null, (s, e) => ShowWindow()),
                        new ToolStripSeparator(),
                        new ToolStripMenuItem("Exit", null, (s, e) => Application.Exit())
                    }
                },
                Visible = true
            };

            trayIcon.MouseClick += (s, e) =>
            {
                if (e.Button == MouseButtons.Left)
                {
                    ShowWindow();
                }
            };

            Application.Run();
        }

        static void ShowWindow()
        {
            var form = new Form
            {
                Text = "My Tray App",
                Width = 400,
                Height = 300
            };
            form.Show();
        }
    }
}
```

##### Go with systray
```go
// main.go
package main

import (
    "github.com/getlantern/systray"
)

func main() {
    systray.Run(onReady, onExit)
}

func onReady() {
    systray.SetIcon(iconData)
    systray.SetTitle("My App")
    systray.SetTooltip("My Tray Application")

    mShow := systray.AddMenuItem("Show", "Show window")
    systray.AddSeparator()
    mQuit := systray.AddMenuItem("Quit", "Quit application")

    go func() {
        for {
            select {
            case <-mShow.ClickedCh:
                // Show window
                showWindow()
            case <-mQuit.ClickedCh:
                systray.Quit()
            }
        }
    }()
}

func onExit() {
    // Cleanup
}

func showWindow() {
    // Open GUI window (using fyne, webview, etc.)
}
```

## Project Structure (Electron Example)

```
tray-app/
├── src/
│   ├── main/                   # Main process
│   │   ├── index.ts            # Entry point
│   │   ├── tray.ts             # Tray logic
│   │   └── window.ts           # Window management
│   │
│   ├── renderer/               # Renderer process
│   │   ├── index.html
│   │   ├── index.tsx
│   │   └── styles/
│   │
│   └── shared/                 # Shared code
│       └── types.ts
│
├── assets/
│   ├── icon.png                # Tray icon
│   └── icon.ico                # Windows icon
│
├── resources/                  # Platform-specific resources
│   ├── darwin/
│   └── win/
│
├── package.json
├── tsconfig.json
└── electron-builder.json       # Build configuration
```

## Common Features

### System Notifications

```typescript
// Electron
import { Notification } from 'electron';

function showNotification(title: string, body: string) {
  new Notification({
    title,
    body,
    icon: path.join(__dirname, 'icon.png'),
  }).show();
}
```

```swift
// macOS Swift
import UserNotifications

func showNotification(title: String, body: String) {
    let content = UNMutableNotificationContent()
    content.title = title
    content.body = body

    let request = UNNotificationRequest(
        identifier: UUID().uuidString,
        content: content,
        trigger: nil
    )

    UNUserNotificationCenter.current().add(request)
}
```

### Auto-Launch on Startup

```typescript
// Electron
import { app } from 'electron';

app.setLoginItemSettings({
  openAtLogin: true,
  openAsHidden: true,
});
```

```swift
// macOS Swift
import ServiceManagement

SMLoginItemSetEnabled(
    "com.myapp.helper" as CFString,
    true
)
```

## Coding Standards

- **Electron/TypeScript:** Refer to `.languages/ts-js/principles.md`
- **Swift:** Refer to `.languages/mobile/` (iOS patterns apply)
- **Go:** Refer to `.languages/go/principles/`
- **C#:** Follow .NET conventions

## Building & Distribution

### Electron

```json
// electron-builder.json
{
  "appId": "com.mycompany.myapp",
  "productName": "My Tray App",
  "directories": {
    "output": "dist"
  },
  "files": [
    "out/**/*"
  ],
  "mac": {
    "category": "public.app-category.utilities",
    "target": ["dmg", "zip"]
  },
  "win": {
    "target": ["nsis", "portable"]
  }
}
```

```bash
# Build for all platforms
npm run build
electron-builder -mw
```

### macOS Native

```bash
# Build and sign
xcodebuild -scheme MyApp -archivePath ./build/MyApp.xcarchive archive
xcodebuild -exportArchive -archivePath ./build/MyApp.xcarchive -exportPath ./dist -exportOptionsPlist ExportOptions.plist
```

### Windows .NET

```bash
# Publish
dotnet publish -c Release -r win-x64 --self-contained
```

## Best Practices

1. **Resource Usage:** Keep memory and CPU usage low
2. **Auto-Start:** Provide option to start on login
3. **Notifications:** Don't spam, make them actionable
4. **Updates:** Auto-update mechanism (Electron: electron-updater)
5. **Preferences:** Persistent settings storage
6. **Quit Behavior:** Clear exit, cleanup resources
7. **Icons:** Multiple sizes, follow platform guidelines
8. **Performance:** Minimize background activity

## Selection Criteria

### Choose Electron When:
- Need cross-platform support
- Team knows web technologies
- Complex UI requirements
- Rapid development priority

### Choose Tauri When:
- Need smaller bundle size
- Performance critical
- Team comfortable with Rust
- Security focused

### Choose Native When:
- Single platform target
- Need deepest OS integration
- Maximum performance required
- Native experience critical

## Learning Resources

- Electron: https://www.electronjs.org/
- Tauri: https://tauri.app/
- macOS Menu Bar Apps: https://developer.apple.com/design/human-interface-guidelines/menu-bar-extras
- Windows System Tray: https://docs.microsoft.com/en-us/windows/apps/design/shell/tiles-and-notifications/

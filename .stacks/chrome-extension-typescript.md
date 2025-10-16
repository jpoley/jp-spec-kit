# Chrome Extension - TypeScript Stack

## Overview

TypeScript-based stack for building Chrome browser extensions with modern web technologies.

## Use Cases

- **Ideal For:**
  - Browser productivity tools
  - Content modification extensions
  - Tab/bookmark managers
  - Web scraping tools
  - Authentication helpers
  - Page analyzers
  - Developer tools
  - Social media enhancers

- **Not Ideal For:**
  - Native desktop applications
  - Mobile apps
  - Backend services
  - Data pipelines

## Tech Stack

- **Language:** TypeScript 5+
- **Manifest:** Manifest V3
- **Build Tool:** Vite, webpack, or Parcel
- **UI:** React (optional), vanilla TS
- **Testing:** Jest, Vitest
- **Package Manager:** npm or pnpm

## Project Structure

```
extension/
├── src/
│   ├── background/             # Service worker
│   │   └── index.ts
│   ├── content/                # Content scripts
│   │   └── index.ts
│   ├── popup/                  # Popup UI
│   │   ├── index.html
│   │   ├── index.tsx
│   │   └── styles.css
│   ├── options/                # Options page
│   │   ├── index.html
│   │   └── index.tsx
│   └── types/                  # TypeScript types
├── public/
│   ├── icons/                  # Extension icons
│   └── manifest.json
├── dist/                       # Build output
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Key Components

### Manifest V3

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "My Chrome extension",
  "permissions": ["storage", "tabs", "activeTab"],
  "host_permissions": ["https://*/*"],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"]
    }
  ],
  "options_page": "options.html"
}
```

### Background Service Worker

```typescript
// src/background/index.ts
chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');

  // Set default storage
  chrome.storage.sync.set({
    enabled: true,
    settings: {}
  });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    // Do something when page loads
    console.log('Page loaded:', tab.url);
  }
});

// Message listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'getData') {
    chrome.storage.sync.get(['data'], (result) => {
      sendResponse({ data: result.data });
    });
    return true; // Keep channel open for async response
  }
});
```

### Content Script

```typescript
// src/content/index.ts
console.log('Content script loaded');

// Modify page content
function modifyPage() {
  const elements = document.querySelectorAll('h1');
  elements.forEach((el) => {
    el.style.color = 'blue';
  });
}

// Listen for messages from background/popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'modifyPage') {
    modifyPage();
    sendResponse({ success: true });
  }
});

// Send message to background
chrome.runtime.sendMessage({
  type: 'getData',
}, (response) => {
  console.log('Got data:', response.data);
});
```

### Popup UI (React)

```typescript
// src/popup/index.tsx
import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

const Popup: React.FC = () => {
  const [enabled, setEnabled] = useState(true);

  useEffect(() => {
    // Load settings
    chrome.storage.sync.get(['enabled'], (result) => {
      setEnabled(result.enabled ?? true);
    });
  }, []);

  const handleToggle = () => {
    const newValue = !enabled;
    setEnabled(newValue);

    // Save to storage
    chrome.storage.sync.set({ enabled: newValue });

    // Send message to content script
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'toggleFeature',
          enabled: newValue,
        });
      }
    });
  };

  return (
    <div style={{ width: '300px', padding: '20px' }}>
      <h2>My Extension</h2>
      <label>
        <input
          type="checkbox"
          checked={enabled}
          onChange={handleToggle}
        />
        {' '}Enable feature
      </label>
    </div>
  );
};

const root = createRoot(document.getElementById('root')!);
root.render(<Popup />);
```

## Storage

```typescript
// Storage utilities
export const storage = {
  async get<T>(key: string): Promise<T | undefined> {
    const result = await chrome.storage.sync.get([key]);
    return result[key];
  },

  async set<T>(key: string, value: T): Promise<void> {
    await chrome.storage.sync.set({ [key]: value });
  },

  async remove(key: string): Promise<void> {
    await chrome.storage.sync.remove([key]);
  },
};
```

## Build Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { crx } from '@crxjs/vite-plugin';
import manifest from './public/manifest.json';

export default defineConfig({
  plugins: [
    react(),
    crx({ manifest }),
  ],
  build: {
    rollupOptions: {
      input: {
        popup: 'src/popup/index.html',
        options: 'src/options/index.html',
      },
    },
  },
});
```

## Coding Standards

**Reference:** `.languages/ts-js/principles.md`

## Testing

```typescript
// Mock Chrome API for testing
global.chrome = {
  storage: {
    sync: {
      get: jest.fn(),
      set: jest.fn(),
    },
  },
  runtime: {
    sendMessage: jest.fn(),
    onMessage: {
      addListener: jest.fn(),
    },
  },
} as any;
```

## Deployment

```bash
# Build extension
npm run build

# Load unpacked in Chrome: chrome://extensions/ (Developer mode)

# Package for Chrome Web Store
zip -r extension.zip dist/
```

## Learning Resources

- Chrome Extensions: https://developer.chrome.com/docs/extensions/
- Manifest V3: https://developer.chrome.com/docs/extensions/mv3/
- Refer to `.languages/ts-js/principles.md`

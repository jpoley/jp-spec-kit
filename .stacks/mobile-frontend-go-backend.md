# Mobile Frontend - Go Backend Stack

## Overview

Cross-platform mobile application stack using React Native (with TypeScript) or native iOS/Android development, backed by a high-performance Go backend API.

## Use Cases

- **Ideal For:**
  - Cross-platform mobile applications (iOS + Android)
  - Performance-critical mobile backends
  - Real-time mobile applications
  - Apps requiring high concurrent user support
  - Mobile apps with complex backend logic
  - Applications with geolocation and real-time updates
  - Mobile-first SaaS products

- **Not Ideal For:**
  - Simple mobile apps with minimal backend needs
  - iOS-only or Android-only apps (consider native)
  - Apps requiring extensive native platform features
  - Projects with very small teams lacking mobile expertise

## Tech Stack Components

### Mobile Frontend Options

#### Option A: React Native (TypeScript)
- **Framework:** React Native 0.72+
- **Language:** TypeScript 5+
- **Navigation:** React Navigation
- **State Management:** Zustand, Jotai, or Redux Toolkit
- **HTTP Client:** Axios or React Query
- **Form Handling:** React Hook Form
- **UI Components:** React Native Paper, NativeBase, or Tamagui
- **Storage:** AsyncStorage or MMKV
- **Push Notifications:** React Native Firebase or Expo Notifications
- **Testing:** Jest, React Native Testing Library, Detox

#### Option B: Native Development
- **iOS:** Swift with SwiftUI
- **Android:** Kotlin with Jetpack Compose
- **Networking:** URLSession (iOS), Retrofit (Android)
- **Local Storage:** Core Data (iOS), Room (Android)
- **DI:** Swinject (iOS), Hilt (Android)

### Backend (Go)
- **Language:** Go 1.21+
- **Framework:** Gin, Echo, or Fiber
- **Database:** PostgreSQL with pgx/GORM
- **Cache:** Redis for session/data caching
- **Real-time:** WebSocket support or Server-Sent Events
- **Push Notifications:** Firebase Cloud Messaging integration
- **Authentication:** JWT with refresh tokens
- **File Storage:** S3-compatible object storage
- **Geolocation:** PostGIS for location queries
- **API Documentation:** OpenAPI/Swagger

### Infrastructure
- **API Gateway:** Kong or NGINX
- **CDN:** CloudFront or Fastly
- **Monitoring:** Prometheus, Grafana, Sentry
- **CI/CD:** GitHub Actions, Fastlane (mobile), Docker (backend)
- **Backend Deployment:** Kubernetes, AWS ECS, or Cloud Run

## Architecture Patterns

### Project Structure

```
project/
├── mobile/                     # React Native app
│   ├── android/                # Android native code
│   ├── ios/                    # iOS native code
│   ├── src/
│   │   ├── screens/            # Screen components
│   │   ├── components/         # Reusable components
│   │   ├── navigation/         # Navigation setup
│   │   ├── hooks/              # Custom hooks
│   │   ├── services/           # API services
│   │   │   └── api/
│   │   │       ├── client.ts   # API client
│   │   │       └── types.ts    # API types
│   │   ├── store/              # State management
│   │   ├── utils/              # Utilities
│   │   ├── types/              # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                    # Go API (same as react-go stack)
│   ├── cmd/
│   │   └── api/
│   ├── internal/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── repository/
│   │   └── mobile/             # Mobile-specific handlers
│   │       ├── push/           # Push notification service
│   │       └── device/         # Device management
│   ├── pkg/
│   ├── migrations/
│   └── api/
│       └── openapi.yaml
│
├── scripts/
│   ├── generate-api-client.sh # Generate mobile API client
│   └── deploy-backend.sh
│
└── README.md
```

### Key Architectural Decisions

1. **Offline-First Architecture**
   - Local data caching with AsyncStorage/MMKV
   - Request queuing for offline operations
   - Sync mechanism when connection restored
   - Optimistic UI updates

2. **Efficient API Design**
   - Pagination for list endpoints
   - Field selection to reduce payload
   - Conditional requests (ETag, If-Modified-Since)
   - Batch endpoints where appropriate
   - GraphQL as alternative to REST (optional)

3. **Real-Time Communication**
   - WebSocket for bidirectional communication
   - Server-Sent Events for server push
   - Push notifications for background updates
   - Efficient reconnection strategy

4. **Security Focus**
   - Certificate pinning
   - Token refresh mechanism
   - Biometric authentication
   - Encrypted local storage
   - API rate limiting

## Coding Standards

### React Native Standards
**Reference:** `.languages/ts-js/principles.md`, `.languages/mobile/`

```typescript
// Example: Mobile screen component
import React, { useEffect } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { UserCard } from '@/components/UserCard';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ErrorView } from '@/components/ErrorView';
import { userApi } from '@/services/api/user';
import type { User } from '@/types/api';

export const UsersScreen: React.FC = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['users'],
    queryFn: userApi.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorView error={error} onRetry={refetch} />;

  return (
    <View style={styles.container}>
      <FlatList
        data={data}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <UserCard user={item} />}
        refreshing={isLoading}
        onRefresh={refetch}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});
```

### Go Backend Standards
**Reference:** `.languages/go/principles/`

```go
// Mobile-specific handlers
package mobile

import (
    "context"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/user/project/internal/domain/device"
)

type MobileHandler struct {
    deviceService device.Service
    pushService   PushService
}

// RegisterDevice handles device registration for push notifications
// @Summary Register mobile device
// @Tags mobile
// @Accept json
// @Produce json
// @Param device body RegisterDeviceRequest true "Device data"
// @Success 200
// @Router /api/v1/mobile/devices [post]
func (h *MobileHandler) RegisterDevice(c *gin.Context) {
    ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Second)
    defer cancel()

    var req RegisterDeviceRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    userID := c.GetString("userID") // From auth middleware

    err := h.deviceService.Register(ctx, device.RegisterParams{
        UserID:       userID,
        DeviceToken:  req.DeviceToken,
        Platform:     req.Platform,
        AppVersion:   req.AppVersion,
        OSVersion:    req.OSVersion,
    })
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register device"})
        return
    }

    c.Status(http.StatusOK)
}
```

## Selection Criteria

### Choose This Stack When:

1. **Mobile-First Product**
   - Primary user interface is mobile
   - Need native mobile experience
   - Require offline functionality
   - Push notifications essential

2. **Cross-Platform Requirements**
   - Target both iOS and Android
   - Want to share code between platforms
   - Need faster time to market than native development

3. **Backend Requirements**
   - High concurrent mobile users
   - Real-time features needed
   - Complex backend logic
   - Need scalable infrastructure

4. **Team Composition**
   - Mobile developers comfortable with React Native or native
   - Backend team has Go expertise
   - Clear API boundaries between teams

### Avoid This Stack When:

1. **Platform-Specific Needs**
   - Require deep platform integration
   - Need cutting-edge platform features
   - Single platform target (iOS or Android only)

2. **Simple Requirements**
   - Minimal backend logic
   - Low concurrent user count
   - No real-time or offline needs

3. **Resource Constraints**
   - Small team without mobile expertise
   - Limited development budget
   - Short timeline with complex features

## Best Practices

### 1. Offline Data Management

```typescript
// services/offline-queue.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

interface QueuedRequest {
  id: string;
  url: string;
  method: string;
  body: any;
  timestamp: number;
}

export class OfflineQueue {
  private static QUEUE_KEY = '@offline_queue';

  static async add(request: Omit<QueuedRequest, 'id' | 'timestamp'>) {
    const queue = await this.getQueue();
    const queuedRequest: QueuedRequest = {
      ...request,
      id: Date.now().toString(),
      timestamp: Date.now(),
    };
    queue.push(queuedRequest);
    await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(queue));
  }

  static async process() {
    const queue = await this.getQueue();
    const processed: string[] = [];

    for (const request of queue) {
      try {
        await fetch(request.url, {
          method: request.method,
          body: JSON.stringify(request.body),
        });
        processed.push(request.id);
      } catch (error) {
        // Keep in queue for retry
        console.error('Failed to process queued request:', error);
      }
    }

    // Remove successfully processed requests
    const remaining = queue.filter(req => !processed.includes(req.id));
    await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(remaining));
  }

  private static async getQueue(): Promise<QueuedRequest[]> {
    const data = await AsyncStorage.getItem(this.QUEUE_KEY);
    return data ? JSON.parse(data) : [];
  }
}
```

### 2. Push Notification Handling

```go
// internal/mobile/push/service.go
package push

import (
    "context"

    firebase "firebase.google.com/go/v4"
    "firebase.google.com/go/v4/messaging"
)

type Service struct {
    client *messaging.Client
}

func NewService(app *firebase.App) (*Service, error) {
    client, err := app.Messaging(context.Background())
    if err != nil {
        return nil, err
    }
    return &Service{client: client}, nil
}

func (s *Service) SendToDevice(ctx context.Context, token string, notification Notification) error {
    message := &messaging.Message{
        Token: token,
        Notification: &messaging.Notification{
            Title: notification.Title,
            Body:  notification.Body,
        },
        Data: notification.Data,
        APNS: &messaging.APNSConfig{
            Payload: &messaging.APNSPayload{
                Aps: &messaging.Aps{
                    Sound: "default",
                },
            },
        },
        Android: &messaging.AndroidConfig{
            Priority: "high",
        },
    }

    _, err := s.client.Send(ctx, message)
    return err
}

func (s *Service) SendToTopic(ctx context.Context, topic string, notification Notification) error {
    message := &messaging.Message{
        Topic: topic,
        Notification: &messaging.Notification{
            Title: notification.Title,
            Body:  notification.Body,
        },
    }

    _, err := s.client.Send(ctx, message)
    return err
}
```

### 3. Biometric Authentication

```typescript
// hooks/useBiometrics.ts
import * as LocalAuthentication from 'expo-local-authentication';
import { useState, useEffect } from 'react';

export function useBiometrics() {
  const [isAvailable, setIsAvailable] = useState(false);
  const [biometricType, setBiometricType] = useState<string[]>([]);

  useEffect(() => {
    checkAvailability();
  }, []);

  const checkAvailability = async () => {
    const compatible = await LocalAuthentication.hasHardwareAsync();
    setIsAvailable(compatible);

    if (compatible) {
      const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
      setBiometricType(types.map(type =>
        LocalAuthentication.AuthenticationType[type]
      ));
    }
  };

  const authenticate = async (): Promise<boolean> => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to continue',
        fallbackLabel: 'Use passcode',
      });
      return result.success;
    } catch (error) {
      console.error('Biometric authentication failed:', error);
      return false;
    }
  };

  return {
    isAvailable,
    biometricType,
    authenticate,
  };
}
```

## Testing Strategy

### Mobile Testing

```typescript
// __tests__/UsersScreen.test.tsx
import { render, waitFor, screen } from '@testing-library/react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UsersScreen } from '@/screens/UsersScreen';
import { userApi } from '@/services/api/user';

jest.mock('@/services/api/user');

describe('UsersScreen', () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  it('should display users', async () => {
    const mockUsers = [
      { id: '1', name: 'John Doe', email: 'john@example.com' },
    ];

    (userApi.getAll as jest.Mock).mockResolvedValue(mockUsers);

    render(
      <QueryClientProvider client={queryClient}>
        <UsersScreen />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeTruthy();
    });
  });
});
```

### E2E Testing with Detox

```typescript
// e2e/users.e2e.ts
describe('Users Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  it('should display users list', async () => {
    await element(by.id('users-tab')).tap();
    await expect(element(by.id('users-list'))).toBeVisible();
  });

  it('should navigate to user detail', async () => {
    await element(by.id('user-item-1')).tap();
    await expect(element(by.id('user-detail'))).toBeVisible();
  });
});
```

## Deployment Considerations

### Mobile App Deployment

#### iOS (App Store)
```bash
# Fastfile for iOS
lane :beta do
  increment_build_number
  build_app(scheme: "MyApp")
  upload_to_testflight
end

lane :release do
  increment_build_number
  build_app(scheme: "MyApp")
  upload_to_app_store
end
```

#### Android (Google Play)
```bash
# Fastfile for Android
lane :beta do
  gradle(task: "bundleRelease")
  upload_to_play_store(track: "internal")
end

lane :release do
  gradle(task: "bundleRelease")
  upload_to_play_store
end
```

### Backend Deployment
- See `react-frontend-go-backend.md` for Go backend deployment strategies

### Over-the-Air Updates
```typescript
// App.tsx - CodePush integration
import codePush from 'react-native-code-push';

const App = () => {
  // App code
};

export default codePush({
  checkFrequency: codePush.CheckFrequency.ON_APP_START,
  installMode: codePush.InstallMode.ON_NEXT_RESTART,
})(App);
```

## Performance Optimization

### Mobile
- Image optimization and lazy loading
- FlatList optimization (getItemLayout, removeClippedSubviews)
- Memoization with React.memo and useMemo
- Navigation optimization (lazy loading screens)
- Bundle size optimization
- Native module usage for CPU-intensive tasks
- Hermes JavaScript engine (React Native)

### Backend
- Connection pooling
- Caching with Redis
- Database query optimization
- gRPC for internal services
- Image/file compression before storage

## Security Considerations

- SSL pinning for API requests
- Secure token storage (Keychain/Keystore)
- Biometric authentication
- Jailbreak/Root detection
- Code obfuscation
- API rate limiting
- Input validation on both client and server
- Encrypted local database

## Learning Resources

- React Native: https://reactnative.dev/
- Swift: https://docs.swift.org/
- Kotlin: https://kotlinlang.org/docs/
- Go: https://go.dev/doc/
- Refer to `.languages/mobile/` for mobile-specific principles
- Refer to `.languages/go/` for Go backend principles

## Success Metrics

- App startup time <2 seconds
- Screen transition <300ms
- API response time <200ms (p95)
- Crash-free rate >99.5%
- App Store rating >4.5 stars
- Backend uptime >99.9%
- Push notification delivery rate >95%

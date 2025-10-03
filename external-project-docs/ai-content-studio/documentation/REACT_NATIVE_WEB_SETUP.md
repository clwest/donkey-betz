# 🚀 React Native Web Setup - AI Content Studio

## Quick Setup (Let's Do This!)

### 1. Initialize Project (5 minutes)
```bash
# Create the project
npx create-expo-app ai-studio-app --template blank-typescript
cd ai-studio-app

# Add web support
npx expo install react-native-web react-dom @expo/webpack-config

# Add navigation
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npx expo install react-native-screens react-native-safe-area-context

# Add UI libraries
npm install react-native-elements react-native-vector-icons
npm install react-native-paper

# Add essential packages
npm install axios zustand react-hook-form
npm install react-native-async-storage
```

### 2. Project Structure
```
ai-studio-app/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Input.tsx
│   │   ├── content/
│   │   │   ├── BlogEditor.tsx
│   │   │   ├── ContentCard.tsx
│   │   │   └── SocialPostCreator.tsx
│   │   └── generation/
│   │       ├── ImageGenerator.tsx
│   │       ├── TextGenerator.tsx
│   │       └── VoiceRecorder.tsx
│   ├── screens/         # App screens
│   │   ├── HomeScreen.tsx
│   │   ├── StudioScreen.tsx
│   │   ├── GalleryScreen.tsx
│   │   ├── CampaignScreen.tsx
│   │   └── ProfileScreen.tsx
│   ├── navigation/
│   │   └── AppNavigator.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── contentService.ts
│   ├── store/
│   │   └── useStore.ts
│   └── utils/
│       └── platform.ts
├── App.tsx
├── app.json
├── package.json
└── tsconfig.json
```

### 3. Platform-Specific Code Example

```typescript
// utils/platform.ts
import { Platform } from 'react-native';

export const isWeb = Platform.OS === 'web';
export const isMobile = Platform.OS === 'ios' || Platform.OS === 'android';
export const isIOS = Platform.OS === 'ios';
export const isAndroid = Platform.OS === 'android';

// Responsive sizing
export const getResponsiveSize = (mobile: number, tablet: number, web: number) => {
  if (isWeb) return web;
  // Add tablet detection logic
  return mobile;
};
```

### 4. Shared Component Example

```typescript
// components/generation/ContentGenerator.tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { isWeb } from '../../utils/platform';

interface Props {
  type: 'blog' | 'social' | 'image';
}

export function ContentGenerator({ type }: Props) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/content/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({ type, prompt }),
      });
      const data = await response.json();
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Generate {type}</Text>
        
        <TextInput
          style={[
            styles.input,
            isWeb && styles.webInput, // Web-specific styling
          ]}
          value={prompt}
          onChangeText={setPrompt}
          placeholder="Enter your prompt..."
          multiline
          numberOfLines={4}
        />
        
        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleGenerate}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Generate</Text>
          )}
        </TouchableOpacity>

        {result && (
          <View style={styles.resultContainer}>
            <Text style={styles.resultTitle}>Result:</Text>
            {/* Render result based on type */}
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    backgroundColor: 'white',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    minHeight: 100,
    textAlignVertical: 'top',
  },
  webInput: {
    outlineStyle: 'none', // Remove web outline
  },
  button: {
    backgroundColor: '#3b82f6',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  resultContainer: {
    marginTop: 20,
    padding: 16,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
});
```

### 5. Run Commands

```bash
# Web development
npm run web

# iOS development
npm run ios

# Android development  
npm run android

# Build for production
expo build:web
expo build:ios
expo build:android
```

## 🎯 Specific Benefits for AI Content Studio

### Mobile-First Features
1. **Voice Recording** - Native mobile APIs, better quality
2. **Camera Integration** - Snap and edit images instantly  
3. **Push Notifications** - "Your video is ready!"
4. **Offline Mode** - Create content without connection
5. **Biometric Auth** - FaceID/TouchID for security

### Web-First Features
1. **Large Canvas** - Complex campaign builders
2. **Keyboard Shortcuts** - Power user features
3. **Multi-window** - Compare content side by side
4. **File Management** - Drag & drop uploads
5. **SEO** - Server-side rendering possible

### Shared Features (Write Once!)
- Content generation
- Gallery viewing
- Social sharing
- User profiles
- Settings
- Analytics dashboards

## 📱 App Store Ready

With React Native Web, you get:
- **iOS App** → App Store submission ready
- **Android App** → Google Play submission ready
- **PWA** → Installable web app
- **Desktop** → Electron wrapper possible

## 🚀 Migration Timeline

### Today (3-4 hours with Claude)
1. **Hour 1**: Set up project, configure navigation
2. **Hour 2**: Create core components (Button, Card, Input, Generator)
3. **Hour 3**: Build 3 main screens (Home, Studio, Gallery)
4. **Hour 4**: Connect to backend API, test on web + mobile

### Tomorrow (3-4 hours)
1. **Hour 1**: Add remaining screens
2. **Hour 2**: Implement state management
3. **Hour 3**: Polish UI, add animations
4. **Hour 4**: Build and deploy

### Monday - Launch! 🎉
- Web app live at your domain
- TestFlight for iOS beta
- APK for Android testing

## 💡 Pro Tips

### Performance
```typescript
// Lazy load heavy screens
const StudioScreen = lazy(() => import('./screens/StudioScreen'));

// Memoize expensive components
const ExpensiveComponent = memo(({ data }) => {
  // Component logic
});
```

### Platform-Specific Features
```typescript
if (isWeb) {
  // Use localStorage
  localStorage.setItem('token', token);
} else {
  // Use AsyncStorage for mobile
  await AsyncStorage.setItem('token', token);
}
```

### Responsive Design
```typescript
const styles = StyleSheet.create({
  container: {
    padding: isWeb ? 24 : 16,
    maxWidth: isWeb ? 1200 : '100%',
  },
});
```

## 🎨 UI Libraries That Work Everywhere

1. **React Native Paper** - Material Design
2. **React Native Elements** - Customizable components
3. **NativeBase** - Universal components
4. **Tamagui** - Universal design system

## Ready to Start?

Just say "Let's do it" and I'll:
1. Create the project structure
2. Build the core components
3. Set up navigation
4. Connect to your backend
5. Make it beautiful

We can have a working prototype in 2-3 hours!
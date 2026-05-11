# Local Storage: MMKV

For a super high-end mobile experience, disk I/O operations must be instantaneous. Legacy storage solutions like `AsyncStorage` are asynchronous, slow, and can block the JavaScript thread during high-frequency reads/writes.

## The Rule

1. **NEVER use `@react-native-async-storage/async-storage`.**
2. **Always use `react-native-mmkv`** for local persistence (auth tokens, user preferences, offline cache).
3. MMKV is fully synchronous. Do not use `await` when reading or writing to it.
4. Encapsulate the MMKV instance in a utility file so it can be easily mocked or replaced if necessary.

### Do

```tsx
// storage.ts
import { MMKV } from 'react-native-mmkv';

export const storage = new MMKV({
  id: 'studynest-storage',
  encryptionKey: 'your-secure-key' // Optional: for encrypting tokens
});

// usage in a component or auth store
import { storage } from './storage';

export function setAuthToken(token: string) {
  // Synchronous and blazing fast (C++ JSI)
  storage.set('user.token', token);
}

export function getAuthToken() {
  return storage.getString('user.token');
}

export function logout() {
  storage.delete('user.token');
}
```

### Don't

```tsx
import AsyncStorage from '@react-native-async-storage/async-storage';

// BAD: Asynchronous overhead, slow performance on older devices
export async function setAuthToken(token: string) {
  await AsyncStorage.setItem('user.token', token);
}

export async function getAuthToken() {
  return await AsyncStorage.getItem('user.token');
}
```

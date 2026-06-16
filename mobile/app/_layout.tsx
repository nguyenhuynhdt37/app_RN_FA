import '../global.css';
import '../src/i18n';
import { useEffect } from 'react';
import { Stack, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as SplashScreen from 'expo-splash-screen';
import { ReanimatedLogLevel, configureReanimatedLogger } from 'react-native-reanimated';
import { useAuthStore } from '../src/stores/auth.store';
import { useThemeStore } from '../src/stores/theme.store';
import { useColorScheme } from 'react-native';
import { useFonts } from 'expo-font';
import { 
  BeVietnamPro_400Regular,
  BeVietnamPro_500Medium,
  BeVietnamPro_600SemiBold,
  BeVietnamPro_700Bold,
  BeVietnamPro_800ExtraBold
} from '@expo-google-fonts/be-vietnam-pro';

// Disable Reanimated strict mode
configureReanimatedLogger({
  level: ReanimatedLogLevel.warn,
  strict: false,
});

SplashScreen.preventAutoHideAsync();

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 1000 * 60 * 5, retry: 1 } },
});

function AuthGuard({ children }: { children: React.ReactNode }) {
  const user = useAuthStore(s => s.user);
  const isLoading = useAuthStore(s => s.isLoading);
  const isAuthenticated = useAuthStore(s => s.isAuthenticated);
  const router = useRouter();
  const rootNavigationState = useRootNavigationState();
  const segments = useSegments();

  useEffect(() => {
    if (isLoading || !rootNavigationState?.key) return;

    const inAppGroup = segments[0] === '(app)';
    const inAuthGroup = segments[0] === '(auth)';
    const isCompleteProfile = segments[segments.length - 1] === 'complete-profile';

    if (isAuthenticated) {
      if (!user?.is_profile_completed) {
        if (!isCompleteProfile) {
          router.replace('/(app)/complete-profile');
        }
      } else {
        if (!inAppGroup || isCompleteProfile) {
          router.replace('/(app)');
        }
      }
    } else if (!inAuthGroup && segments[0] !== 'demo') {
      router.replace('/(auth)/onboarding');
    }
  }, [isAuthenticated, user?.is_profile_completed, isLoading, segments, rootNavigationState?.key]);

  return <>{children}</>;
}

import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { NetworkErrorScreen } from '../components/ui/NetworkErrorScreen';
import { NetworkMonitor } from '../components/layout/NetworkMonitor';

import { useColorScheme as useNativeWindColorScheme } from 'nativewind';

export default function RootLayout() {
  const { setColorScheme } = useNativeWindColorScheme();
  const [fontsLoaded] = useFonts({
    'BeVietnamPro-Regular': BeVietnamPro_400Regular,
    'BeVietnamPro-Medium': BeVietnamPro_500Medium,
    'BeVietnamPro-SemiBold': BeVietnamPro_600SemiBold,
    'BeVietnamPro-Bold': BeVietnamPro_700Bold,
    'BeVietnamPro-ExtraBold': BeVietnamPro_800ExtraBold,
  });

  const initialize = useAuthStore(s => s.initialize);
  const isLoading = useAuthStore(s => s.isLoading);
  const connectionError = useAuthStore(s => s.connectionError);
  const preference = useThemeStore(s => s.preference);
  const systemScheme = useColorScheme();

  const colorScheme = preference === 'system' ? (systemScheme ?? 'dark') : preference;

  useEffect(() => {
    initialize();
  }, []);

  useEffect(() => {
    // Sync NativeWind colorScheme with our store/system
    setColorScheme(colorScheme);
  }, [colorScheme]);

  useEffect(() => {
    if (fontsLoaded && !isLoading) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded, isLoading]);

  if (!fontsLoaded || (isLoading && !connectionError)) return null;

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <StatusBar style={colorScheme === 'dark' ? 'light' : 'dark'} />
          <NetworkMonitor>
            {connectionError ? (
              <NetworkErrorScreen />
            ) : (
              <AuthGuard>
                <Stack screenOptions={{ headerShown: false }} />
              </AuthGuard>
            )}
          </NetworkMonitor>
        </QueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

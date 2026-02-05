import { Stack } from 'expo-router';
import { HSE_THEME } from '../src/config';

export default function Layout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: HSE_THEME.primary },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
        headerTitle: "PaperTrail",
      }}
    >
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="login" options={{ title: 'Secure Login' }} />
      <Stack.Screen name="signup" options={{ title: 'Create Account' }} />
      <Stack.Screen name="dashboard" options={{ title: 'Dashboard', headerLeft: () => null }} />
      <Stack.Screen name="scan" options={{ title: 'Scan Document' }} />
    </Stack>
  );
}
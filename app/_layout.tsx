import { Stack } from "expo-router";

export default function Layout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="login" options={{ title: "Login" }} />
      <Stack.Screen name="signup" options={{ title: "Sign Up" }} />
      <Stack.Screen name="home" options={{ title: "Home" }} />
      <Stack.Screen name="scan" options={{ title: "Scan" }} />
      <Stack.Screen name="existing" options={{ title: "Existing" }} />
      <Stack.Screen name="document/[id]" options={{ title: "Document" }} />
    </Stack>
  );
}

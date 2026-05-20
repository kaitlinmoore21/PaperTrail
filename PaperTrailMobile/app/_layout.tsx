import { Stack } from 'expo-router'; // Imports the "Stack" tool, which stacks screens on top of each other like a deck of cards
import { HSE_THEME } from '../src/config'; // Imports your official brand colors (Primary Green/Blue)

export default function Layout() {
  return (
    <Stack
      //  GLOBAL SETTINGS (Applies to all screens) 
      screenOptions={{
        headerStyle: { backgroundColor: HSE_THEME.primary }, // Sets the top bar to your brand's primary color
        headerTintColor: '#fff', // Makes the back button and icons white
        headerTitleStyle: { fontWeight: 'bold' }, // Makes the title text bold
        headerTitle: "PaperTrail", // The default text shown at the top of the app
      }}
    >
      {/* INDIVIDUAL SCREEN RULES */}
      
      {/* 1. Landing Page: Hides the header completely for a clean look */}
      <Stack.Screen name="index" options={{ headerShown: false }} /> 
      
      {/* 2. Login Page: Changes the title to "Secure Login" */}
      <Stack.Screen name="login" options={{ title: 'Secure Login' }} /> 
      
      {/* 3. Signup Page: Changes the title to "Create Account" */}
      <Stack.Screen name="signup" options={{ title: 'Create Account' }} /> 
      
      {/* 4. Dashboard: The main hub. 
          'headerLeft: () => null' removes the back button so users can't "go back" to the login screen after logging in. */}
      <Stack.Screen name="dashboard" options={{ title: 'Dashboard', headerLeft: () => null }} /> 
      
      {/* 5. Scan Page: Sets the title for the camera/upload area */}
      <Stack.Screen name="scan" options={{ title: 'Scan Document' }} /> 
    </Stack>
  );
}

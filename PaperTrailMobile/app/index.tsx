import React from 'react'; // Imports React library
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native'; // Imports the visual building blocks
import { useRouter } from 'expo-router'; // Imports the tool to move between screens
import { HSE_THEME } from '../src/config'; // Imports your official branding colors

export default function WelcomeScreen() {
  const router = useRouter(); // Initializes the "Navigator" so we can switch pages

  return (
    <View style={styles.container}>
      {/* --- TOP SECTION: Logo and Branding --- */}
      <View style={styles.logoContainer}>
        {/* The main title of the app */}
        <Text style={styles.logoText}>PaperTrail</Text>
        {/* A small subtitle explaining what the app does */}
        <Text style={styles.tagline}>AI-Powered Document Automation</Text>
      </View>

      {/* --- BOTTOM SECTION: Action Buttons --- */}
      <View style={styles.buttonContainer}>
        
        {/* LOGIN BUTTON: A solid colored button */}
        <TouchableOpacity 
          style={styles.primaryButton} 
          onPress={() => router.push('/login')} // Moves the user to the login screen
        >
          <Text style={styles.buttonText}>Login</Text>
        </TouchableOpacity>

        {/* SIGNUP BUTTON: An "outline" style button to show it's the second choice */}
        <TouchableOpacity 
          style={styles.secondaryButton} 
          onPress={() => router.push('/signup')} // Moves the user to the signup screen
        >
          {/* Overrides the white text color to use your primary brand color instead */}
          <Text style={[styles.buttonText, { color: HSE_THEME.primary }]}>Create Account</Text>
        </TouchableOpacity>
        
      </View>
    </View>
  );
}

// Design rules (Styles) for the screen
const styles = StyleSheet.create({
  // The main background
  container: { flex: 1, backgroundColor: HSE_THEME.white, padding: 30, justifyContent: 'space-around' },
  
  // Centers the logo and text in the middle of their section
  logoContainer: { alignItems: 'center' },
  
  // Big, bold branded text
  logoText: { fontSize: 42, fontWeight: 'bold', color: HSE_THEME.primary },
  
  // Grey, smaller text for the description
  tagline: { fontSize: 16, color: '#666', marginTop: 10 },
  
  // Adds a 15-pixel gap between the two buttons so they don't touch
  buttonContainer: { gap: 15 },
  
  // The solid "Primary" button style
  primaryButton: { backgroundColor: HSE_THEME.primary, padding: 18, borderRadius: 12, alignItems: 'center' },
  
  // The outlined "Secondary" button style (border instead of solid background)
  secondaryButton: { borderWidth: 2, borderColor: HSE_THEME.primary, padding: 18, borderRadius: 12, alignItems: 'center' },
  
  // Large, bold font for the text inside the buttons
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold' },
});
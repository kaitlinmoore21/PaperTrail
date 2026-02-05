import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { HSE_THEME } from '../src/config';

export default function WelcomeScreen() {
  const router = useRouter();

  return (
    <View style={styles.container}>
      <View style={styles.logoContainer}>
        {/* You can add a logo image here later */}
        <Text style={styles.logoText}>PaperTrail</Text>
        <Text style={styles.tagline}>AI-Powered Document Automation</Text>
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={styles.primaryButton} 
          onPress={() => router.push('/login')}
        >
          <Text style={styles.buttonText}>Login</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.secondaryButton} 
          onPress={() => router.push('/signup')}
        >
          <Text style={[styles.buttonText, { color: HSE_THEME.primary }]}>Create Account</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: HSE_THEME.white, padding: 30, justifyContent: 'space-around' },
  logoContainer: { alignItems: 'center' },
  logoText: { fontSize: 42, fontWeight: 'bold', color: HSE_THEME.primary },
  tagline: { fontSize: 16, color: '#666', marginTop: 10 },
  buttonContainer: { gap: 15 },
  primaryButton: { backgroundColor: HSE_THEME.primary, padding: 18, borderRadius: 12, alignItems: 'center' },
  secondaryButton: { borderWidth: 2, borderColor: HSE_THEME.primary, padding: 18, borderRadius: 12, alignItems: 'center' },
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold' },
});
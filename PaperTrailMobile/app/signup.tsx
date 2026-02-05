import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { signupUser } from '../src/hooks/useAuth';
import { HSE_THEME } from '../src/config';

export default function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const router = useRouter();

  const handleSignup = async () => {
    if (password !== confirmPassword) {
      return Alert.alert("Error", "Passwords do not match");
    }
    try {
      await signupUser(email, password);
      Alert.alert("Success", "Account created successfully!");
      router.push('/login');
    } catch (err: any) {
      Alert.alert("Signup Failed", err.message || "Something went wrong");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Join PaperTrail</Text>
      <Text style={styles.subtitle}>Secure documentation for healthcare professionals</Text>

      <TextInput 
        placeholder="HSE Email Address" 
        style={styles.input} 
        onChangeText={setEmail}
        autoCapitalize="none"
      />
      <TextInput 
        placeholder="Password" 
        style={styles.input} 
        secureTextEntry 
        onChangeText={setPassword}
      />
      <TextInput 
        placeholder="Confirm Password" 
        style={styles.input} 
        secureTextEntry 
        onChangeText={setConfirmPassword}
      />

      <TouchableOpacity style={styles.button} onPress={handleSignup}>
        <Text style={styles.buttonText}>Sign Up</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: HSE_THEME.white, padding: 30, justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: 'bold', color: HSE_THEME.primary, marginBottom: 10 },
  subtitle: { fontSize: 14, color: '#666', marginBottom: 30 },
  input: { borderBottomWidth: 1, borderBottomColor: '#ccc', padding: 12, marginBottom: 20, fontSize: 16 },
  button: { backgroundColor: HSE_THEME.primary, padding: 15, borderRadius: 8, marginTop: 10, alignItems: 'center' },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 18 },
});
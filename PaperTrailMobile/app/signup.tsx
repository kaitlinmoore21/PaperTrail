import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
// Import the helper function fixed in useAuth
import { signupUser } from '../src/hooks/useAuth';
import { HSE_THEME } from '../src/config';

export default function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSignup = async () => {
    // 1. Basic Validation
    if (!email || !password || !confirmPassword) {
      return Alert.alert("Error", "Please fill in all fields");
    }

    if (password !== confirmPassword) {
      return Alert.alert("Error", "Passwords do not match");
    }

    setLoading(true);
    try {
      // FIXED: Wrapped arguments in an object to match expected FastAPI Pydantic model
      await signupUser({ email, password });
      
      Alert.alert(
        "Success", 
        "Account created successfully!",
        [{ text: "Login Now", onPress: () => router.push('/login') }]
      );
    } catch (err: any) {
      console.error("Signup Error:", err);
      // Extract specific backend error message (e.g., "User already exists")
      const errorMsg = err.response?.data?.detail || "Registration failed. Please try again.";
      Alert.alert("Signup Failed", errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Join PaperTrail</Text>
      <Text style={styles.subtitle}>Secure documentation for healthcare professionals</Text>

      <TextInput 
        placeholder="Employee Email Address" 
        style={styles.input} 
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />

      <TextInput 
        placeholder="Password" 
        style={styles.input} 
        secureTextEntry 
        value={password}
        onChangeText={setPassword}
      />

      <TextInput 
        placeholder="Confirm Password" 
        style={styles.input} 
        secureTextEntry 
        value={confirmPassword}
        onChangeText={setConfirmPassword}
      />

      <TouchableOpacity 
        style={[styles.button, loading && { opacity: 0.7 }]} 
        onPress={handleSignup}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Sign Up</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/login')} style={styles.linkContainer}>
        <Text style={styles.linkText}>
          Already have an account? <Text style={{fontWeight: 'bold'}}>Login</Text>
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: HSE_THEME.white, 
    padding: 30, 
    justifyContent: 'center' 
  },
  title: { 
    fontSize: 28, 
    fontWeight: 'bold', 
    color: HSE_THEME.primary, 
    marginBottom: 10 
  },
  subtitle: { 
    fontSize: 14, 
    color: '#666', 
    marginBottom: 30 
  },
  input: { 
    borderBottomWidth: 1, 
    borderBottomColor: '#ccc', 
    padding: 12, 
    marginBottom: 20, 
    fontSize: 16 
  },
  button: { 
    backgroundColor: HSE_THEME.primary, 
    padding: 15, 
    borderRadius: 8, 
    alignItems: 'center',
    marginTop: 10
  },
  buttonText: { 
    color: 'white', 
    fontWeight: 'bold', 
    fontSize: 18 
  },
  linkContainer: {
    marginTop: 20,
    alignItems: 'center'
  },
  linkText: {
    color: HSE_THEME.primary,
    fontSize: 14
  }
});
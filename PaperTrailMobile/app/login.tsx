import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { loginUser } from '../src/hooks/useAuth';
import { HSE_THEME } from '../src/config';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [employeeNumber, setEmployeeNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async () => {
    if (!email || !password || !employeeNumber) {
      return Alert.alert("Error", "Please fill in all fields");
    }

    setLoading(true);
    try {
      const response = await loginUser({ 
        email, 
        password, 
        employee_number: employeeNumber 
      });
      
      if (response.status === 200) {
        const { access_token, role } = response.data;

        // SAVING USER DATA TO STORAGE 
        await AsyncStorage.setItem('userToken', access_token);
        await AsyncStorage.setItem('userRole', role);
        await AsyncStorage.setItem('userEmail', email); // This line ensures the email follows the user to the Dashboard

        Alert.alert("Success", `Welcome back! Logged in as ${role}`);
        router.push('/dashboard'); 
      }
    } catch (err: any) {
      console.error("Login Error:", err);
      const errorMsg = err.response?.data?.detail || "Invalid credentials or server unreachable";
      Alert.alert("Login Failed", errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login</Text>
      <Text style={styles.subtitle}>Enter your Employee credentials to continue</Text>

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
        placeholder="Employee Number"
        style={styles.input}
        value={employeeNumber}
        onChangeText={setEmployeeNumber}
        autoCapitalize="none"
        keyboardType="default"
      />

      <TouchableOpacity 
        style={[styles.button, loading && { opacity: 0.7 }]}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Login</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/signup')} style={styles.linkContainer}>
        <Text style={styles.linkText}>
          Don't have an account? <Text style={{fontWeight: 'bold'}}>Sign Up</Text>
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: HSE_THEME.white, padding: 30, justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: 'bold', color: HSE_THEME.primary, marginBottom: 10 },
  subtitle: { fontSize: 14, color: '#666', marginBottom: 30 },
  input: { borderBottomWidth: 1, borderBottomColor: '#ccc', padding: 12, marginBottom: 20, fontSize: 16 },
  button: { backgroundColor: HSE_THEME.primary, padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 10 },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 18 },
  linkContainer: { marginTop: 20, alignItems: 'center' },
  linkText: { color: HSE_THEME.primary, fontSize: 14 }
});

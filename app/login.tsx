import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from "react-native";
import { router } from "expo-router";

// This simulates a secure backend.
// Replace later with your real API.
async function mockLoginAPI(email: string, password: string) {
  const crypto = require("crypto-js");

  // Simulated stored user
  const storedUser = {
    email: "test@example.com",
    passwordHash: crypto.SHA256("Password123!").toString(),
  };

  const providedHash = crypto.SHA256(password).toString();

  if (email !== storedUser.email) {
    throw new Error("Account not found.");
  }

  if (providedHash !== storedUser.passwordHash) {
    throw new Error("Incorrect password.");
  }

  return { token: "secure-jwt-token-example" };
}

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin() {
    setError("");

    if (!email || !password) {
      setError("All fields are required.");
      return;
    }

    try {
      const result = await mockLoginAPI(email, password);

      // Secure token stored only for session; don't store passwords
      console.log("Logged in:", result.token);

      router.push("/home"); // Navigate to your home screen
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <TextInput
        placeholder="Email"
        value={email}
        autoCapitalize="none"
        onChangeText={setEmail}
        style={styles.input}
      />

      <TextInput
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        style={styles.input}
      />

      <TouchableOpacity style={styles.button} onPress={handleLogin}>
        <Text style={styles.buttonText}>Sign In</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push("/signup")}>
        <Text style={styles.link}>Create an account</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 20 },
  title: { fontSize: 28, fontWeight: "bold", marginBottom: 20 },
  input: {
    borderWidth: 1,
    padding: 12,
    marginBottom: 12,
    borderRadius: 6,
  },
  error: { color: "red", marginBottom: 10 },
  button: {
    backgroundColor: "#007bff",
    padding: 15,
    borderRadius: 6,
    marginTop: 10,
  },
  buttonText: { color: "white", textAlign: "center", fontWeight: "bold" },
  link: { color: "#007bff", marginTop: 20, textAlign: "center" },
});

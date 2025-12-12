import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from "react-native";
import { router } from "expo-router";
import CryptoJS from "crypto-js";

let mockUserDB: any = null;

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  function validatePassword(pw: string) {
    const minLength = pw.length >= 8;
    const hasUpper = /[A-Z]/.test(pw);
    const hasLower = /[a-z]/.test(pw);
    const hasNumber = /\d/.test(pw);
    const hasSymbol = /[\W_]/.test(pw);

    return minLength && hasUpper && hasLower && hasNumber && hasSymbol;
  }

  async function handleSignup() {
    setError("");

    if (!email || !password || !confirmPassword) {
      setError("All fields are required.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!validatePassword(password)) {
      setError(
        "Password must be 8+ chars and include uppercase, lowercase, number, and symbol."
      );
      return;
    }

    if (mockUserDB && mockUserDB.email === email) {
      setError("An account with that email already exists.");
      return;
    }


    const passwordHash = CryptoJS.SHA256(password).toString();

    mockUserDB = {
      email,
      passwordHash,
    };

    console.log("User registered:", mockUserDB);


    router.replace("/login");
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Account</Text>

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

      <TextInput
        placeholder="Confirm Password"
        secureTextEntry
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        style={styles.input}
      />

      <TouchableOpacity style={styles.button} onPress={handleSignup}>
        <Text style={styles.buttonText}>Sign Up</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push("/login")}>
        <Text style={styles.link}>Already have an account? Sign in</Text>
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

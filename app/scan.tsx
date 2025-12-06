import { useRef, useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { router } from "expo-router";

export default function Scan() {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<any>(null);
  const [loading, setLoading] = useState(false);

  if (!permission?.granted) {
    return (
      <View style={styles.container}>
        <Text>Camera access is needed to scan documents.</Text>
        <TouchableOpacity onPress={requestPermission} style={styles.permissionBtn}>
          <Text style={{ color: "white" }}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  async function takePhoto() {
    try {
      setLoading(true);

      const photo = await cameraRef.current.takePictureAsync({ base64: true });

      const response = await fetch("http://192.168.0.233:8000/ocr", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: photo.base64 }),
      });

      if (!response.ok) {
        throw new Error("Backend error occurred");
      }

      setLoading(false);

      // Go to previous scans page
      router.push("/existing");

    } catch (err: any) {
      setLoading(false);
      Alert.alert("Scan Error", err.message || "Could not scan the document.");
    }
  }

  return (
    <View style={{ flex: 1 }}>
      <CameraView style={{ flex: 1 }} ref={cameraRef} />

      <TouchableOpacity style={styles.captureButton} onPress={takePhoto}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.captureText}>Scan</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", padding: 20 },
  permissionBtn: {
    marginTop: 15,
    padding: 12,
    backgroundColor: "#007bff",
    borderRadius: 8,
  },
  captureButton: {
    position: "absolute",
    bottom: 40,
    alignSelf: "center",
    backgroundColor: "#007bff",
    paddingVertical: 18,
    paddingHorizontal: 28,
    borderRadius: 60,
  },
  captureText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 18,
  },
});

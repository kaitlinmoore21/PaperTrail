import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { API_BASE, HSE_THEME } from '../src/config';

export default function Scan() {
  const [image, setImage] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const router = useRouter();
  
  // This catches the URI if sent from the Dashboard's "Existing from Device"
  const { externalImage } = useLocalSearchParams(); 

  // EFFECT: Automatically show the image if it was passed from the Dashboard
  useEffect(() => {
    if (externalImage) {
      setImage(externalImage as string);
    }
  }, [externalImage]);

  const launchCamera = async () => {
    // 1. Request Permissions
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert("Permission Denied", "Camera access is required to scan documents.");
      return;
    }

    // 2. Launch Camera
    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,
      allowsEditing: true,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const uploadToBackend = async () => {
    if (!image) return;
    setUploading(true);

    try {
      const formData = new FormData();
      
      // Extract dynamic filename and extension
      const uriParts = image.split('.');
      const fileType = uriParts[uriParts.length - 1];
      const fileName = image.split('/').pop() || `upload.${fileType}`;

      // @ts-ignore
      formData.append('file', {
        uri: image,
        name: fileName,
        // Detect if it's a PDF or an Image
        type: fileName.endsWith('.pdf') ? 'application/pdf' : `image/${fileType}`,
      });

      const response = await fetch(`${API_BASE}/upload/`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.ok) {
        Alert.alert("Success", "Document uploaded and processing.");
        // Redirect to the archive to see the new document
        router.replace('/processed');
      } else {
        const errorData = await response.json();
        Alert.alert("Upload Failed", errorData.detail || "Server error");
      }
    } catch (err) {
      console.error("Upload Error:", err);
      Alert.alert("Connection Error", "Could not reach the server. Check your backend IP.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Secure Capture</Text>
      
      <View style={styles.previewBox}>
        {image ? (
          <Image source={{ uri: image }} style={styles.preview} resizeMode="contain" />
        ) : (
          <Text style={{ color: '#666' }}>Ready to scan document</Text>
        )}
      </View>

      {/* Button to Launch Camera (Only show if no image yet or to retake) */}
      <TouchableOpacity style={styles.button} onPress={launchCamera}>
        <Text style={styles.buttonText}>{image ? "Retake Photo" : "Launch Camera"}</Text>
      </TouchableOpacity>

      {/* Upload Button (Only shows when an image is ready) */}
      {image && (
        <TouchableOpacity 
          style={[styles.button, { backgroundColor: HSE_THEME.secondary }]} 
          onPress={uploadToBackend}
          disabled={uploading}
        >
          {uploading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Upload to PaperTrail</Text>
          )}
        </TouchableOpacity>
      )}

      <TouchableOpacity onPress={() => router.back()}>
        <Text style={{ color: HSE_THEME.primary, marginTop: 10 }}>Cancel</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: HSE_THEME.background, padding: 20, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 24, fontWeight: 'bold', color: HSE_THEME.primary, marginBottom: 30 },
  previewBox: { width: '100%', height: 400, backgroundColor: '#ddd', borderRadius: 15, justifyContent: 'center', alignItems: 'center', marginBottom: 20, overflow: 'hidden', borderWidth: 1, borderColor: '#ccc' },
  preview: { width: '100%', height: '100%' },
  button: { backgroundColor: HSE_THEME.primary, padding: 16, borderRadius: 10, width: '100%', alignItems: 'center', marginBottom: 15 },
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold' }
});
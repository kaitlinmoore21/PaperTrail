import React, { useState, useEffect } from 'react';
import { 
  View, Text, TouchableOpacity, Image, StyleSheet, Alert, 
  ActivityIndicator, TextInput, KeyboardAvoidingView, Platform, ScrollView 
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { API_BASE, HSE_THEME } from '../src/config';

export default function Scan() {
  // STATE (Memory) 
  const [image, setImage] = useState<string | null>(null); // Stores the temporary path to the photo
  const [uploading, setUploading] = useState(false);       // Tracks if the file is currently traveling to the server
  const [customName, setCustomName] = useState('');        // Stores the file name the user types
  const router = useRouter();
  
  // This looks for an image passed from the Dashboard (e.g., if picked from Gallery)
  const { externalImage } = useLocalSearchParams(); 

  // If an image was passed from another screen, display it immediately
  useEffect(() => {
    if (externalImage) {
      setImage(externalImage as string);
      setCustomName(`Upload_${new Date().getTime()}`); // Set a temporary unique name
    }
  }, [externalImage]);

  // THE CAMERA LOGIC 
  const launchCamera = async () => {
    // A. Ask the phone for permission to use the camera
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert("Permission Denied", "Camera access is required to scan documents.");
      return;
    }

    // B. Open the camera interface
    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,      // 0.8 is a good balance between clarity and small file size
      allowsEditing: true, // Let the user crop the photo to the edges of the paper
    });

    // C. If the user didn't hit 'Cancel', save the photo path and generate a name
    if (!result.canceled) {
      setImage(result.assets[0].uri);
      const timestamp = new Date().toLocaleDateString().replace(/\//g, '-');
      setCustomName(`Doc_${timestamp}`);
    }
  };

  // THE UPLOAD LOGIC 
  const uploadToBackend = async () => {
    if (!image) return;
    if (!customName.trim()) {
      Alert.alert("Name Required", "Please enter a name for this document.");
      return;
    }

    setUploading(true); // Start showing the spinner

    try {
      // Step A: Get the Security Token (Digital Badge)
      const token = await AsyncStorage.getItem('userToken');
      
      // Step B: Create a "FormData" object. Think of this as a digital envelope 
      // used to send raw files (binary data) over the web.
      const formData = new FormData();
      const uriParts = image.split('.');
      const fileType = uriParts[uriParts.length - 1]; // e.g., 'jpg' or 'png'
      const finalFileName = `${customName.trim()}.${fileType}`;

      // Step C: "Stuff" the image into the envelope
      // @ts-ignore
      formData.append('file', {
        uri: image,
        name: finalFileName,
        type: finalFileName.endsWith('.pdf') ? 'application/pdf' : `image/${fileType}`,
      });

      // Step D: Send the envelope to the server's /upload/ endpoint
      const response = await fetch(`${API_BASE}/upload/`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`, // Crucial: Proves who is uploading
        },
      });

      if (response.ok) {
        Alert.alert("Success", `"${customName}" has been uploaded.`);
        router.replace('/dashboard'); // Go back to start
      } else {
        const errorData = await response.json();
        Alert.alert("Upload Failed", errorData.detail || "Server error");
      }
    } catch (err) {
      console.error("Upload Error:", err);
      Alert.alert("Connection Error", "Could not reach the server.");
    } finally {
      setUploading(false); // Stop the spinner
    }
  };

  return (
    /* KeyboardAvoidingView prevents the keyboard from covering the input box */
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
      style={{ flex: 1 }}
    >
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Secure Capture</Text>
        
        {/* PREVIEW WINDOW */}
        <View style={styles.previewBox}>
          {image ? (
            <Image source={{ uri: image }} style={styles.preview} resizeMode="contain" />
          ) : (
            <Text style={{ color: '#666' }}>Ready to scan document</Text>
          )}
        </View>

        {/* FILE NAMING SECTION (Only visible after a photo is taken) */}
        {image && (
          <View style={styles.inputSection}>
            <Text style={styles.label}>Assign File Name</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Invoice_2024"
              value={customName}
              onChangeText={setCustomName}
              placeholderTextColor="#999"
            />
          </View>
        )}

        {/* BUTTONS */}
        <TouchableOpacity style={styles.button} onPress={launchCamera}>
          <Text style={styles.buttonText}>{image ? "Retake Photo" : "Launch Camera"}</Text>
        </TouchableOpacity>

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
          <Text style={{ color: HSE_THEME.primary, marginTop: 10, paddingBottom: 40 }}>Cancel</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

// STYLES 
const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: HSE_THEME.background, padding: 20, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 24, fontWeight: 'bold', color: HSE_THEME.primary, marginBottom: 20 },
  previewBox: { width: '100%', height: 300, backgroundColor: '#eee', borderRadius: 15, justifyContent: 'center', alignItems: 'center', marginBottom: 20, overflow: 'hidden', borderWidth: 1, borderColor: '#ccc' },
  preview: { width: '100%', height: '100%' },
  inputSection: { width: '100%', marginBottom: 20 },
  label: { fontSize: 14, fontWeight: '600', color: HSE_THEME.primary, marginBottom: 5 },
  input: { width: '100%', backgroundColor: '#fff', padding: 12, borderRadius: 10, borderWidth: 1, borderColor: '#bbb', fontSize: 16, color: '#000' },
  button: { backgroundColor: HSE_THEME.primary, padding: 16, borderRadius: 10, width: '100%', alignItems: 'center', marginBottom: 15 },
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold' }
});

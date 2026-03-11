import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  Image, 
  StyleSheet, 
  Alert, 
  ActivityIndicator, 
  TextInput, 
  KeyboardAvoidingView, 
  Platform, 
  ScrollView 
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { API_BASE, HSE_THEME } from '../src/config';

export default function Scan() {
  const [image, setImage] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [customName, setCustomName] = useState(''); // State for your file name
  const router = useRouter();
  
  const { externalImage } = useLocalSearchParams(); 

  useEffect(() => {
    if (externalImage) {
      setImage(externalImage as string);
      // Pre-fill a name if coming from gallery
      setCustomName(`Upload_${new Date().getTime()}`);
    }
  }, [externalImage]);

  const launchCamera = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert("Permission Denied", "Camera access is required to scan documents.");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,
      allowsEditing: true,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      // Default name to save you typing every time, but you can change it
      const timestamp = new Date().toLocaleDateString().replace(/\//g, '-');
      setCustomName(`Doc_${timestamp}`);
    }
  };

  const uploadToBackend = async () => {
    if (!image) return;
    if (!customName.trim()) {
      Alert.alert("Name Required", "Please enter a name for this document.");
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      
      const uriParts = image.split('.');
      const fileType = uriParts[uriParts.length - 1];
      
      // We use your custom name here and keep the original extension
      const finalFileName = `${customName.trim()}.${fileType}`;

      // @ts-ignore
      formData.append('file', {
        uri: image,
        name: finalFileName,
        type: finalFileName.endsWith('.pdf') ? 'application/pdf' : `image/${fileType}`,
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
        Alert.alert("Success", `"${customName}" has been uploaded.`);
        router.replace('/processed');
      } else {
        const errorData = await response.json();
        Alert.alert("Upload Failed", errorData.detail || "Server error");
      }
    } catch (err) {
      console.error("Upload Error:", err);
      Alert.alert("Connection Error", "Could not reach the server.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
      style={{ flex: 1 }}
    >
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Secure Capture</Text>
        
        <View style={styles.previewBox}>
          {image ? (
            <Image source={{ uri: image }} style={styles.preview} resizeMode="contain" />
          ) : (
            <Text style={{ color: '#666' }}>Ready to scan document</Text>
          )}
        </View>

        {/* Name Input Field - Shows up after photo is taken */}
        {image && (
          <View style={styles.inputSection}>
            <Text style={styles.label}>Assign File Name</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. HSE_Invoice_2024"
              value={customName}
              onChangeText={setCustomName}
              placeholderTextColor="#999"
            />
          </View>
        )}

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

const styles = StyleSheet.create({
  container: { 
    flexGrow: 1, 
    backgroundColor: HSE_THEME.background, 
    padding: 20, 
    alignItems: 'center', 
    justifyContent: 'center' 
  },
  title: { fontSize: 24, fontWeight: 'bold', color: HSE_THEME.primary, marginBottom: 20 },
  previewBox: { 
    width: '100%', 
    height: 300, 
    backgroundColor: '#eee', 
    borderRadius: 15, 
    justifyContent: 'center', 
    alignItems: 'center', 
    marginBottom: 20, 
    overflow: 'hidden', 
    borderWidth: 1, 
    borderColor: '#ccc' 
  },
  preview: { width: '100%', height: '100%' },
  inputSection: { width: '100%', marginBottom: 20 },
  label: { fontSize: 14, fontWeight: '600', color: HSE_THEME.primary, marginBottom: 5 },
  input: { 
    width: '100%', 
    backgroundColor: '#fff', 
    padding: 12, 
    borderRadius: 10, 
    borderWidth: 1, 
    borderColor: '#bbb', 
    fontSize: 16,
    color: '#000'
  },
  button: { 
    backgroundColor: HSE_THEME.primary, 
    padding: 16, 
    borderRadius: 10, 
    width: '100%', 
    alignItems: 'center', 
    marginBottom: 15 
  },
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold' }
});
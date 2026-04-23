import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { HSE_THEME } from '../src/config';
import { Ionicons } from '@expo/vector-icons';

export default function Dashboard() {
  const router = useRouter();
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserRole = async () => {
      const storedRole = await AsyncStorage.getItem('userRole');
      setRole(storedRole);
    };
    fetchUserRole();
  }, []);

  const pickFromGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') return;
    const result = await ImagePicker.launchImageLibraryAsync({ quality: 0.7 });
    if (!result.canceled) {
      router.push({ pathname: '/scan', params: { externalImage: result.assets[0].uri } });
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>PaperTrail</Text>
      
      <TouchableOpacity style={styles.mainButton} onPress={() => router.push('/scan')}>
        <Ionicons name="camera" size={32} color="white" />
        <Text style={styles.buttonText}>Scan New Document</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[styles.mainButton, { backgroundColor: HSE_THEME.secondary }]} onPress={pickFromGallery}>
        <Ionicons name="folder-open" size={32} color="white" />
        <Text style={styles.buttonText}>Existing from Device</Text>
      </TouchableOpacity>

      {/* Logic: Only show this button if the user is NOT a secretary */}
      {role !== 'secretary' && (
        <TouchableOpacity 
          style={[styles.mainButton, { backgroundColor: '#6c757d' }]} 
          onPress={() => router.push('/processed')}
        >
          <Ionicons name="list" size={32} color="white" />
          <Text style={styles.buttonText}>Previously Processed</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: HSE_THEME.background, padding: 20, justifyContent: 'center' },
  header: { fontSize: 32, fontWeight: 'bold', color: HSE_THEME.primary, textAlign: 'center', marginBottom: 50 },
  mainButton: { flexDirection: 'row', backgroundColor: HSE_THEME.primary, padding: 25, borderRadius: 15, alignItems: 'center', marginBottom: 20, elevation: 4 },
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold', marginLeft: 15 }
});
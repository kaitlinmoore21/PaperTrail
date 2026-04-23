import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, Modal, ScrollView } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE, HSE_THEME } from '../../src/config';

export default function DocumentDetail() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const [password, setPassword] = useState('');
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [viewVisible, setViewVisible] = useState(false);
  const [docData, setDocData] = useState<any>(null);

  const handleUnlock = async () => {
    if (password === 'decryptme!') {
      try {
        const token = await AsyncStorage.getItem('userToken');
        const res = await fetch(`${API_BASE}/documents/${id}/details`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setDocData(data);
        setIsUnlocked(true);
      } catch (err) {
        setIsUnlocked(true); // Fallback for UI testing
      }
    } else {
      Alert.alert("Denied", "Incorrect password.");
    }
  };

  return (
    <View style={styles.container}>
      {!isUnlocked ? (
        <View style={styles.center}>
          <Text style={styles.lockIcon}>🔒</Text>
          <Text style={styles.title}>Document Protected</Text>
          <TextInput 
            secureTextEntry 
            style={styles.input} 
            value={password}
            onChangeText={setPassword}
          />
          <TouchableOpacity style={styles.button} onPress={handleUnlock}>
            <Text style={styles.buttonText}>Unlock Access</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.center}>
          <Text style={styles.successTitle}>Access Granted</Text>
          <TouchableOpacity 
            style={[styles.button, {marginBottom: 15}]} 
            onPress={() => setViewVisible(true)}
          >
            <Text style={styles.buttonText}>View In-App (Private)</Text>
          </TouchableOpacity>
         </View>
      )}

      <Modal visible={viewVisible} animationType="slide">
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Document Content</Text>
            <TouchableOpacity onPress={() => setViewVisible(false)}>
              <Text style={styles.closeBtn}>Close</Text>
            </TouchableOpacity>
          </View>
          <ScrollView style={styles.scrollArea}>
            <Text style={styles.infoLabel}>Patient/Document Details:</Text>
            <View style={styles.dataCard}>
              <Text style={styles.rawText}>
                {docData ? JSON.stringify(docData.extracted_data || docData, null, 2) : "Decrypting data..."}
              </Text>
            </View>
          </ScrollView>
        </View>
      </Modal>
    </View>
  ); 
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center', backgroundColor: '#fff' },
  center: { alignItems: 'center', width: '100%' },
  lockIcon: { fontSize: 60, marginBottom: 10 },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 20 },
  successTitle: { fontSize: 22, fontWeight: 'bold', color: HSE_THEME.secondary, marginBottom: 30 },
  input: { width: '100%', borderBottomWidth: 2, borderColor: HSE_THEME.primary, marginBottom: 30, textAlign: 'center', fontSize: 18 },
  button: { backgroundColor: HSE_THEME.primary, padding: 18, borderRadius: 12, width: '100%', alignItems: 'center' },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  modalContent: { flex: 1, backgroundColor: '#f9f9f9', paddingTop: 50 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 20, paddingBottom: 20, borderBottomWidth: 1, borderBottomColor: '#eee' },
  modalTitle: { fontSize: 20, fontWeight: 'bold' },
  closeBtn: { color: HSE_THEME.primary, fontWeight: 'bold', fontSize: 16 },
  scrollArea: { padding: 20 },
  infoLabel: { fontWeight: 'bold', color: '#666', marginBottom: 10 },
  dataCard: { backgroundColor: 'white', padding: 15, borderRadius: 10, borderWidth: 1, borderColor: '#ddd' },
  rawText: { fontFamily: 'monospace', fontSize: 14, color: '#333' }
});
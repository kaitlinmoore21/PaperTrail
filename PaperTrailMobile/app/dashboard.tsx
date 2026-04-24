import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal, Pressable, SafeAreaView, StatusBar } from 'react-native';
// 1. Add 'Stack' to this import line
import { useRouter, Stack } from 'expo-router'; 
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { HSE_THEME } from '../src/config';
import { Ionicons } from '@expo/vector-icons';

export default function Dashboard() {
  const router = useRouter();
  const [role, setRole] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    const fetchUserData = async () => {
      const storedRole = await AsyncStorage.getItem('userRole');
      const storedEmail = await AsyncStorage.getItem('userEmail'); 
      setRole(storedRole);
      setEmail(storedEmail);
    };
    fetchUserData();
  }, []);

  const handleLogout = async () => {
    await AsyncStorage.multiRemove(['userToken', 'userRole', 'userEmail']);
    setMenuVisible(false);
    router.replace('/login');
  };

  const pickFromGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') return;

    const result = await ImagePicker.launchImageLibraryAsync({ quality: 0.7 });
    if (!result.canceled) {
      router.push({ pathname: '/scan', params: { externalImage: result.assets[0].uri } });
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* 2. THIS LINE HIDES THE EXTRA AUTOMATIC HEADER */}
      <Stack.Screen options={{ headerShown: false }} />

      {/* THIS IS YOUR ONLY CUSTOM HEADER */}
      <View style={styles.topBar}>
        <Text style={styles.topBarTitle}>PaperTrail</Text>
        
        <TouchableOpacity style={styles.profileTrigger} onPress={() => setMenuVisible(true)}>
          <View style={styles.headerTextInfo}>
             <Text style={styles.headerRole}>{role || 'Staff'}</Text>
          </View>
          <Ionicons name="person-circle" size={38} color="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.menuContent}>
        <TouchableOpacity style={styles.mainButton} onPress={() => router.push('/scan')}>
          <Ionicons name="camera" size={32} color="white" />
          <Text style={styles.buttonText}>Scan New Document</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.mainButton, { backgroundColor: HSE_THEME.secondary }]} onPress={pickFromGallery}>
          <Ionicons name="folder-open" size={32} color="white" />
          <Text style={styles.buttonText}>Existing from Device</Text>
        </TouchableOpacity>

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

      <Modal
        transparent={true}
        visible={menuVisible}
        animationType="fade"
        onRequestClose={() => setMenuVisible(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setMenuVisible(false)}>
          <View style={styles.dropdown}>
            <Text style={styles.dropdownLabel}>Current User</Text>
            <Text style={styles.userEmailText}>{email || 'No email found'}</Text>
            
            <View style={styles.statusBadge}>
               <Text style={styles.statusText}>{role?.toUpperCase() || 'ACCESS GRANTED'}</Text>
            </View>

            <View style={styles.separator} />
            
            <TouchableOpacity style={styles.logoutRow} onPress={handleLogout}>
              <Ionicons name="log-out-outline" size={20} color="#d9534f" />
              <Text style={styles.logoutText}>Logout</Text>
            </TouchableOpacity>
          </View>
        </Pressable>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: HSE_THEME.background },
  topBar: {
    height: 80,
    backgroundColor: HSE_THEME.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 10,
    elevation: 8,
  },
  topBarTitle: { color: 'white', fontWeight: 'bold', fontSize: 24 },
  profileTrigger: { flexDirection: 'row', alignItems: 'center' },
  headerTextInfo: { marginRight: 10, alignItems: 'flex-end' },
  headerRole: { color: 'white', fontSize: 13, opacity: 0.9, fontWeight: '600', textTransform: 'capitalize' },
  menuContent: { flex: 1, padding: 25, justifyContent: 'center' },
  mainButton: { flexDirection: 'row', backgroundColor: HSE_THEME.primary, padding: 25, borderRadius: 15, alignItems: 'center', marginBottom: 20, elevation: 4 },
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold', marginLeft: 15 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'flex-start', alignItems: 'flex-end' },
  dropdown: { marginTop: 85, marginRight: 20, backgroundColor: 'white', padding: 20, borderRadius: 12, width: 260, elevation: 10 },
  dropdownLabel: { fontSize: 10, color: '#999', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 5 },
  userEmailText: { fontSize: 15, color: '#333', fontWeight: '600', marginBottom: 10 },
  statusBadge: { backgroundColor: '#e8f0fe', paddingVertical: 4, paddingHorizontal: 10, borderRadius: 20, alignSelf: 'flex-start' },
  statusText: { fontSize: 11, color: HSE_THEME.primary, fontWeight: 'bold' },
  separator: { height: 1, backgroundColor: '#eee', marginVertical: 15 },
  logoutRow: { flexDirection: 'row', alignItems: 'center' },
  logoutText: { color: '#d9534f', fontWeight: 'bold', marginLeft: 10, fontSize: 16 }
});
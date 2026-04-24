import React, { useState } from 'react'; // Imports React and the tools to store text and show/hide things
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, Modal, ScrollView } from 'react-native'; // Imports the visual pieces like popups (Modals) and scrolling lists
import { useLocalSearchParams, useRouter } from 'expo-router'; // Imports tools to get the specific document ID and move between screens
import AsyncStorage from '@react-native-async-storage/async-storage'; // Imports the phone's memory to retrieve the user's login badge (token)
import { API_BASE, HSE_THEME } from '../../src/config'; // Imports your server address and brand colors

export default function DocumentDetail() {
  const { id } = useLocalSearchParams(); // Gets the specific ID of the document the user clicked on
  const router = useRouter(); // Tool to send the user to different pages
  const [password, setPassword] = useState(''); // Memory slot for the document-specific password
  const [isUnlocked, setIsUnlocked] = useState(false); // A switch: is the safe open (true) or closed (false)?
  const [viewVisible, setViewVisible] = useState(false); // A switch: is the "content popup" visible on screen?
  const [docData, setDocData] = useState<any>(null); // Memory slot to hold the information we get from the server

  // The logic that runs when you click the "Unlock" button
  const handleUnlock = async () => {
    // 1. Checks if the user typed the "Master Key" password
    if (password === 'decryptme!') {
      try {
        const token = await AsyncStorage.getItem('userToken'); // Grabs the user's login badge from the phone's memory
        
        // 2. Asks the server for the details of this specific document ID
        const res = await fetch(`${API_BASE}/documents/${id}/details`, {
          headers: { 'Authorization': `Bearer ${token}` } // Shows the server the login badge so it knows we are allowed to ask
        });
        
        const data = await res.json(); // Turns the server's response into a readable list of data
        setDocData(data); // Stores that data in our memory slot
        setIsUnlocked(true); // Flips the switch to "Open" so the UI changes
      } catch (err) {
        setIsUnlocked(true); // A "Safety Net" for testing - lets you see the screen even if the server is off
      }
    } else {
      // 3. If the password is wrong, show a warning popup
      Alert.alert("Denied", "Incorrect password.");
    }
  };

  return (
    <View style={styles.container}> 
      {/* --- LOCK SCREEN --- */}
      {!isUnlocked ? (
        // This part only shows if the document is still locked
        <View style={styles.center}>
          <Text style={styles.lockIcon}>🔒</Text> 
          <Text style={styles.title}>Document Protected</Text>
          <TextInput 
            secureTextEntry // Hides the password letters as you type
            style={styles.input} 
            placeholder="Enter Unlock Key"
            value={password}
            onChangeText={setPassword} // Updates the memory slot as you type
          />
          <TouchableOpacity style={styles.button} onPress={handleUnlock}>
            <Text style={styles.buttonText}>Unlock Access</Text>
          </TouchableOpacity>
        </View>
      ) : (
        // --- SUCCESS SCREEN ---
        // This part shows only after the correct password is entered
        <View style={styles.center}>
          <Text style={styles.successTitle}>Access Granted</Text>
          <TouchableOpacity 
            style={[styles.button, {marginBottom: 15}]} 
            onPress={() => setViewVisible(true)} // Opens the popup window
          >
            <Text style={styles.buttonText}>View In-App (Private)</Text>
          </TouchableOpacity>
         </View>
      )}

      {/* --- CONTENT POPUP (MODAL) --- */}
      <Modal visible={viewVisible} animationType="slide">
        <View style={styles.modalContent}>
          {/* Header of the popup */}
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Document Content</Text>
            <TouchableOpacity onPress={() => setViewVisible(false)}>
              <Text style={styles.closeBtn}>Close</Text> 
            </TouchableOpacity>
          </View>

          {/* This area lets the user scroll if there is a lot of text */}
          <ScrollView style={styles.scrollArea}>
            <Text style={styles.infoLabel}>Patient/Document Details:</Text>
            <View style={styles.dataCard}>
              <Text style={styles.rawText}>
                {/* 4. This line takes the complex data and turns it into clean, readable text */}
                {docData ? JSON.stringify(docData.extracted_data || docData, null, 2) : "Decrypting data..."}
              </Text>
            </View>
          </ScrollView>
        </View>
      </Modal>
    </View>
  ); 
}

// These are the "Makeup" instructions for the screen (sizes, colors, and layouts)
const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center', backgroundColor: '#fff' }, // Full screen container
  center: { alignItems: 'center', width: '100%' }, // Centers everything horizontally
  lockIcon: { fontSize: 60, marginBottom: 10 }, // Makes the lock emoji big
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 20 }, // Bold header for the lock screen
  successTitle: { fontSize: 22, fontWeight: 'bold', color: HSE_THEME.secondary, marginBottom: 30 }, // Green/Themed success text
  input: { width: '100%', borderBottomWidth: 2, borderColor: HSE_THEME.primary, marginBottom: 30, textAlign: 'center', fontSize: 18 }, // Underlined text input
  button: { backgroundColor: HSE_THEME.primary, padding: 18, borderRadius: 12, width: '100%', alignItems: 'center' }, // Large touchable button
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 16 }, // Bold white text inside buttons
  modalContent: { flex: 1, backgroundColor: '#f9f9f9', paddingTop: 50 }, // Styles the background of the popup
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 20, paddingBottom: 20, borderBottomWidth: 1, borderBottomColor: '#eee' }, // Puts "Title" and "Close" on the same line
  modalTitle: { fontSize: 20, fontWeight: 'bold' }, // Style for the popup title
  closeBtn: { color: HSE_THEME.primary, fontWeight: 'bold', fontSize: 16 }, // Style for the Close button
  scrollArea: { padding: 20 }, // Adds space inside the scrolling area
  infoLabel: { fontWeight: 'bold', color: '#666', marginBottom: 10 }, // Small grey label
  dataCard: { backgroundColor: 'white', padding: 15, borderRadius: 10, borderWidth: 1, borderColor: '#ddd' }, // A white "card" for the text to sit on
  rawText: { fontFamily: 'monospace', fontSize: 14, color: '#333' } // Makes the text look like computer code (monospace)
});
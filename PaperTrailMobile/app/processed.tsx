import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE, HSE_THEME } from '../src/config';
import { Ionicons } from '@expo/vector-icons';

// 1. THE DATA BLUEPRINT:
// This defines the "shape" of our document. It ensures the app knows exactly 
// what data pieces (id, name, date) to expect from the server.
interface DocumentItem {
  id: number;
  filename: string;
  created_at: string;
}

export default function ProcessedDocs() {
<<<<<<< HEAD
  //  (App Memory)
=======
  // STATE (App Memory) 
>>>>>>> c5a3a70 (Improving AI Extractions and Comments)
  const [docs, setDocs] = useState<DocumentItem[]>([]); // Holds the full list of documents
  const [search, setSearch] = useState('');            // Holds the text currently in the search bar
  const [loading, setLoading] = useState(true);        // A switch to show/hide the loading spinner
  const router = useRouter();                          // The tool to navigate between screens

  // THE FETCH FUNCTION (Talking to the Server) 
  const fetchDocs = async () => {
    try {
      // Step A: Grab the user's login token (badge) from the phone's storage
      const token = await AsyncStorage.getItem('userToken');
      
      // Step B: Send a request to our Backend API
      const response = await fetch(`${API_BASE}/documents/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`, // Proves we are a logged-in user
          'Accept': 'application/json',
        },
      });

      // Step C: If the server says "OK", save the list of docs into our app's memory
      if (response.ok) {
        const data = await response.json();
        setDocs(data);
      }
    } catch (err) {
      console.error("Fetch error:", err); // Log any errors to the developer console
    } finally {
      setLoading(false); // Whether we succeed or fail, stop showing the loading spinner
    }
  };

  // Step D: Run the fetch function exactly once as soon as this screen opens
  useEffect(() => { fetchDocs(); }, []);

  // THE DATE FORMATTER (Human-Friendly Text) 
  const formatDate = (dateString: string) => {
    if (!dateString) return "No Date";
    const date = new Date(dateString);
    // Turns "2024-05-20T14:30" into a standard date format like "20/05/2024"
    return isNaN(date.getTime()) ? dateString.split('T')[0] : date.toLocaleDateString();
  };

  // THE SEARCH FILTER 
  // This creates a smaller list of documents that match what the user is typing
  const filteredDocs = docs.filter(d => 
    d.filename?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <View style={styles.container}>
      {/* HEADER SECTION */}
      <View style={styles.header}>
        {/* Back Button: Sends the user back to the Dashboard */}
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={HSE_THEME.primary} />
        </TouchableOpacity>
        <Text style={styles.title}>Archive</Text>
      </View>

      {/* SEARCH BAR */}
      <TextInput 
        style={styles.searchBar}
        placeholder="Search (e.g., Blood Test)"
        value={search}
        onChangeText={setSearch} // Updates the 'search' memory every time a letter is typed
        placeholderTextColor="#999"
      />

      {/* MAIN CONTENT AREA*/}
      {loading ? (
        // If still loading, show a spinning circle
        <ActivityIndicator size="large" color={HSE_THEME.primary} />
      ) : (
        // If finished loading, show the scrollable list
        <FlatList
          data={filteredDocs} // Use the filtered results for the list
          keyExtractor={(item) => item.id.toString()} // Give every row a unique identity
          renderItem={({ item }) => (
            // Every item in the list is a button
            <TouchableOpacity 
              style={styles.card} 
              onPress={() => router.push(`/document/${item.id}`)} // Go to the detail/unlock screen
            >
              <View>
                <Text style={styles.docName}>{item.filename}</Text>
                <Text style={styles.docDate}>{formatDate(item.created_at)}</Text>
              </View>
              {/* Lock icon: Reminds the user that the file is encrypted */}
              <Ionicons name="lock-closed" size={18} color="#bbb" />
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  );
}

// STYLING (The "CSS" for the App)
const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f5f5f5' },
  header: { flexDirection: 'row', alignItems: 'center', marginTop: 40, marginBottom: 20 },
  title: { fontSize: 22, fontWeight: 'bold', marginLeft: 15, color: HSE_THEME.primary },
  searchBar: { backgroundColor: 'white', padding: 15, borderRadius: 10, marginBottom: 20, borderWidth: 1, borderColor: '#ddd', color: '#000' },
  card: { backgroundColor: 'white', padding: 18, borderRadius: 12, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', elevation: 1 },
  docName: { fontWeight: 'bold', fontSize: 16, color: '#333' },
  docDate: { color: '#888', fontSize: 13, marginTop: 4 }
});

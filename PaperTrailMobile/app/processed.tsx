import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE, HSE_THEME } from '../src/config';
import { Ionicons } from '@expo/vector-icons';

// THIS FIXES THE 'NEVER' ERROR: Define what a Document looks like
interface DocumentItem {
  id: number;
  filename: string;
  created_at: string;
}

export default function ProcessedDocs() {
  // Initialize state with the DocumentItem type
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchDocs = async () => {
    try {
      const token = await AsyncStorage.getItem('userToken');
      const response = await fetch(`${API_BASE}/documents/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDocs(data);
      }
    } catch (err) {
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDocs(); }, []);

  // FIXED DATE LOGIC: Replaces "Date Pending" with a readable date
  const formatDate = (dateString: string) => {
    if (!dateString) return "No Date";
    const date = new Date(dateString);
    // If it's a valid date, format it. If not, show the raw string.
    return isNaN(date.getTime()) ? dateString.split('T')[0] : date.toLocaleDateString();
  };

  const filteredDocs = docs.filter(d => 
    d.filename?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={HSE_THEME.primary} />
        </TouchableOpacity>
        <Text style={styles.title}>Archive</Text>
      </View>

      <TextInput 
        style={styles.searchBar}
        placeholder="Search (e.g., Blood Test)"
        value={search}
        onChangeText={setSearch}
        placeholderTextColor="#999"
      />

      {loading ? (
        <ActivityIndicator size="large" color={HSE_THEME.primary} />
      ) : (
        <FlatList
          data={filteredDocs}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity 
              style={styles.card} 
              onPress={() => router.push(`/document/${item.id}`)}
            >
              <View>
                <Text style={styles.docName}>{item.filename}</Text>
                <Text style={styles.docDate}>{formatDate(item.created_at)}</Text>
              </View>
              <Ionicons name="lock-closed" size={18} color="#bbb" />
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f5f5f5' },
  header: { flexDirection: 'row', alignItems: 'center', marginTop: 40, marginBottom: 20 },
  title: { fontSize: 22, fontWeight: 'bold', marginLeft: 15, color: HSE_THEME.primary },
  searchBar: { backgroundColor: 'white', padding: 15, borderRadius: 10, marginBottom: 20, borderWidth: 1, borderColor: '#ddd', color: '#000' },
  card: { backgroundColor: 'white', padding: 18, borderRadius: 12, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', elevation: 1 },
  docName: { fontWeight: 'bold', fontSize: 16, color: '#333' },
  docDate: { color: '#888', fontSize: 13, marginTop: 4 }
});
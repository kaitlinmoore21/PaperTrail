import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import api from '../src/api'; 
import { HSE_THEME } from '../src/config';
import { Ionicons } from '@expo/vector-icons';

export default function ProcessedDocs() {
  const [docs, setDocs] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Fetches your documents from FastAPI
    api.get('/documents/')
      .then(res => {
        setDocs(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Filter logic for both Name and Date (DD/MM/YYYY)
  const filteredDocs = docs.filter(d => 
    d.filename?.toLowerCase().includes(search.toLowerCase()) || 
    d.created_at?.includes(search) 
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
        placeholder="Search (e.g., Blood Test or 03/02/2026)"
        value={search}
        onChangeText={setSearch}
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
                <Text style={styles.docDate}>{item.created_at}</Text>
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
  searchBar: { backgroundColor: 'white', padding: 15, borderRadius: 10, marginBottom: 20, borderWidth: 1, borderColor: '#ddd' },
  card: { backgroundColor: 'white', padding: 18, borderRadius: 12, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  docName: { fontWeight: 'bold', fontSize: 16 },
  docDate: { color: '#888', fontSize: 13, marginTop: 4 }
});
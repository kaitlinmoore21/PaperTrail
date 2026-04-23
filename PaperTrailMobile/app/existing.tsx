// app/existing.tsx
import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, ActivityIndicator } from 'react-native';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export default function Existing() {
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/documents`)
      .then((res) => {
        setDocs(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.log(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <ActivityIndicator size="large" color="#0000ff" />;

  return (
    <View style={{ padding: 20 }}>
      <Text>Existing Documents:</Text>
      <FlatList
        data={docs}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <Text>- {item.title}</Text>}
      />
    </View>
  );
}
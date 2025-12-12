import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { router } from "expo-router";

type DocumentItem = {
  id: number | string;
  filename: string;
  created_at?: string;
};

export default function Existing() {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadDocs() {
    try {
      const response = await fetch("http://192.168.0.233:8000/documents");
      const data: DocumentItem[] = await response.json();
      setDocs(data);
    } catch (err) {
      console.error("Error loading documents:", err);
      alert("Failed to load documents");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocs();
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 10 }}>Loading documents...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Previous Documents</Text>

      <FlatList<DocumentItem>
        data={docs}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.item}
            onPress={() =>
              router.push(`/document/${item.id}`)
            }
          >
            <Text style={styles.itemText}>{item.filename}</Text>
            {item.created_at && <Text style={styles.meta}>{item.created_at}</Text>}
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  container: { flex: 1, padding: 20 },
  title: { fontSize: 26, fontWeight: "bold", marginBottom: 20 },
  item: {
    padding: 18,
    backgroundColor: "#f2f2f2",
    borderRadius: 8,
    marginBottom: 10,
  },
  itemText: { fontSize: 18 },
  meta: { fontSize: 12, color: "#666", marginTop: 6 },
});

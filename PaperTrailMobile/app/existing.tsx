import React, { useEffect, useState } from 'react'; // Imports React and the hooks for data and life-cycles
import { View, Text, FlatList, ActivityIndicator } from 'react-native'; // Imports mobile UI components (FlatList is like a smart scrollable list)
import axios from 'axios'; // Imports a popular tool for making "Phone Calls" (HTTP requests) to your server

const API_BASE = 'http://127.0.0.1:8000'; // The home address of your backend server

export default function Existing() {
  const [docs, setDocs] = useState<any[]>([]); // A memory slot to store the list of documents once they arrive
  const [loading, setLoading] = useState(true); // A switch that stays 'true' until the data finished loading

  // This block runs automatically as soon as this screen is opened
  useEffect(() => {
    // 1. Sends a request to the server: "Hey, give me all the documents!"
    axios.get(`${API_BASE}/documents`)
      .then((res) => {
        // 2. If the server answers, save the list of documents into our memory slot
        setDocs(res.data);
        setLoading(false); // Turn off the loading spinner
      })
      .catch((err) => {
        // 3. If the server is off or there is an error, log it and stop loading
        console.log(err);
        setLoading(false);
      });
  }, []); // The empty brackets [] mean "only run this once when the screen starts"

  // If we are still waiting for the server, show a spinning loading circle
  if (loading) return <ActivityIndicator size="large" color="#0000ff" />;

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 20, fontWeight: 'bold', marginBottom: 10 }}>
        Existing Documents:
      </Text>
      
      {/* 4. The FlatList is a high-performance way to show lists on mobile */}
      <FlatList
        data={docs} // Tells the list where to find the data
        keyExtractor={(item) => item.id.toString()} // Gives every item a unique ID (required by React)
        renderItem={({ item }) => (
          // 5. This tells the app how each single row should look
          <Text style={{ paddingVertical: 8, fontSize: 16 }}>
            - {item.title || item.filename} 
          </Text>
        )}
      />
    </View>
  );
}
import React from 'react'; // Imports the core React library
import { View, Text } from 'react-native'; // Imports the basic building blocks (containers and text)

export default function PasswordPage() {
  return (
    // The "View" is like a transparent box. 
    // - flex: 1 tells the box to fill the entire screen.
    // - justifyContent: 'center' centers the contents vertically (top to bottom).
    // - alignItems: 'center' centers the contents horizontally (left to right).
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      
      {/* The "Text" component is the only way to show words in React Native */}
      <Text>Reset Password Screen</Text>
      
    </View>
  );
}
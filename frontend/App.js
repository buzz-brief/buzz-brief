import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { StatusBar } from "expo-status-bar";
import { AuthProvider } from "./src/context/AuthContext";
import HomePage from "./src/pages/HomePage";
import VideoFeed from "./src/pages/VideoFeed";
import NewPage from "./src/pages/NewPage";
import GmailIntegration from "./src/pages/GmailIntegration";

const Stack = createStackNavigator();

export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
        <StatusBar style="light" backgroundColor="#000" />
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerShown: false,
            cardStyle: { backgroundColor: "#000" },
          }}
        >
          <Stack.Screen name="Home" component={HomePage} />
          <Stack.Screen name="VideoFeed" component={VideoFeed} />
          <Stack.Screen name="NewPage" component={NewPage} />
          <Stack.Screen name="GmailIntegration" component={GmailIntegration} />
        </Stack.Navigator>
      </NavigationContainer>
    </AuthProvider>
  );
}

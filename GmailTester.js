import React, { useEffect, useState } from "react";
import { View, Button, Alert, Text } from "react-native";
import { GoogleSignin } from "@react-native-google-signin/google-signin";
import { decode as atob } from "base-64";

const IOS_CLIENT_ID = '1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com';
const SUPABASE_URL = 'SUPABASE_URL'; //change this with the actual URL
const SUPABASE_ANON_KEY = 'SUPABASE_ANON_KEY'; //change this with the actual key
const SUPABASE_TABLE = 'emails';

const GmailTester = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    console.log('GmailTester component mounted');
    try {
      GoogleSignin.configure({
        iosClientId: IOS_CLIENT_ID,
        scopes: ["https://www.googleapis.com/auth/gmail.readonly"],
      });
      console.log('Google Sign-In configured successfully');
      setIsLoaded(true);
    } catch (error) {
      console.error('Error configuring Google Sign-In:', error);
      setIsLoaded(true);
    }
  }, []);

  const signInWithGoogle = async () => {
    try {
      await GoogleSignin.hasPlayServices({ showPlayServicesUpdateDialog: true });
      await GoogleSignin.signIn();
      setIsSignedIn(true);
      Alert.alert("Success", "Successfully signed in with Google!");
    } catch (error) {
      console.error('Google Sign-In error:', error);
      Alert.alert("Error", `Sign-in failed: ${error.message}`);
    }
  };

  const signOut = async () => {
    try {
      await GoogleSignin.signOut();
      setIsSignedIn(false);
      Alert.alert("Success", "Successfully signed out!");
    } catch (error) {
      console.error('Sign-out error:', error);
      Alert.alert("Error", `Sign-out failed: ${error.message}`);
    }
  };

  const decodeBase64Url = (str) => {
    str = str.replace(/-/g, "+").replace(/_/g, "/");
    return decodeURIComponent(
      atob(str)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
  };

  const getHeader = (headers, name) => {
    const header = headers.find((h) => h.name.toLowerCase() === name.toLowerCase());
    return header ? header.value : "";
  };

  const getBody = (payload) => {
    if (!payload) return "";
    if (payload.parts && payload.parts.length > 0) {
      for (const part of payload.parts) {
        if (part.mimeType === "text/plain" && part.body?.data) {
          return decodeBase64Url(part.body.data);
        }
        if (part.parts) {
          const inner = getBody(part);
          if (inner) return inner;
        }
      }
    } else if (payload.body?.data) {
      return decodeBase64Url(payload.body.data);
    }
    return "";
  };

  const saveToSupabase = async (emailData) => {
    try {
      for (const email of emailData) {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/${SUPABASE_TABLE}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            'Prefer': 'return=minimal'
          },
          body: JSON.stringify(email)
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('Supabase error details:', errorText);
          throw new Error(`Supabase error: ${response.status} ${response.statusText} - ${errorText}`);
        }
      }

      return true;
    } catch (error) {
      console.error('Supabase save error:', error);
      throw error;
    }
  };

  const fetchGmailMessages = async () => {
    if (!isSignedIn) {
      Alert.alert("Error", "Please sign in first!");
      return;
    }

    setIsLoading(true);
    try {
      const { accessToken } = await GoogleSignin.getTokens();
      if (!accessToken) throw new Error("Access token not available");

      const response = await fetch(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5",
        {
          headers: { Authorization: `Bearer ${accessToken}` },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const messages = data.messages || [];
      let savedCount = 0;
      const emailData = [];

      for (const msg of messages) {
        try {
          const msgResponse = await fetch(
            `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}`,
            { headers: { Authorization: `Bearer ${accessToken}` } }
          );

          if (msgResponse.ok) {
            const message = await msgResponse.json();
            const headers = message.payload?.headers || [];
            const subject = getHeader(headers, "Subject") || "(no subject)";
            const body = getBody(message.payload) || "";
            const created_at = new Date(parseInt(message.internalDate));

            const emailInfo = {
              email_id: msg.id,
              subject,
              body: body.substring(0, 200) + (body.length > 200 ? "..." : ""),
              created_at: created_at.toISOString(),
            };

            emailData.push(emailInfo);
            savedCount++;
          }
        } catch (msgError) {
          console.error('Error processing message:', msgError);
        }
      }

      if (emailData.length > 0) {
        try {
          console.log('Email data to save:', JSON.stringify(emailData, null, 2));
          console.log('First email structure:', Object.keys(emailData[0]));
          await saveToSupabase(emailData);
          Alert.alert("Success", `${savedCount} Gmail messages processed and saved to Supabase database!`);
        } catch (supabaseError) {
          console.error('Supabase error details:', supabaseError.message);
          Alert.alert("Database Error", `Failed to save to database: ${supabaseError.message}\n\nCheck console for data structure details.`);
        }
      } else {
        Alert.alert("Info", "No Gmail messages found to process.");
      }
    } catch (error) {
      console.error('Gmail fetch error:', error);
      Alert.alert("Error", `Failed to fetch Gmail messages: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isLoaded) {
    return (
      <View style={{ marginTop: 50, padding: 20 }}>
        <Text style={{ fontSize: 18, textAlign: 'center' }}>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={{ marginTop: 50, padding: 20 }}>
      <Text style={{ fontSize: 18, marginBottom: 20, textAlign: 'center' }}>
        Gmail Tester App
      </Text>
      <Text style={{ fontSize: 14, marginBottom: 20, textAlign: 'center', color: 'green' }}>
        Component loaded successfully!
      </Text>
      
      {!isSignedIn ? (
        <Button title="Sign In with Google" onPress={signInWithGoogle} />
      ) : (
        <View>
          <Text style={{ fontSize: 16, marginBottom: 20, textAlign: 'center', color: 'blue' }}>
            ✅ Signed in with Google
          </Text>
          <Button 
            title={isLoading ? "Fetching Gmail..." : "Fetch Gmail Messages"} 
            onPress={fetchGmailMessages}
            disabled={isLoading}
          />
          <View style={{ marginTop: 10 }}>
            <Button title="Sign Out" onPress={signOut} />
          </View>
        </View>
      )}
    </View>
  );
};

export default GmailTester;
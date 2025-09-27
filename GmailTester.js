import React, { useEffect, useState } from 'react';
import { SafeAreaView, Button, Text, StyleSheet, ScrollView } from 'react-native';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import axios from 'axios';

export default function GmailTester() {
  const [userInfo, setUserInfo] = useState(null);
  const [status, setStatus] = useState('');

  useEffect(() => {
    GoogleSignin.configure({
      webClientId: '1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com',
      iosClientId: '1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com',
      offlineAccess: true,
      scopes: ['https://www.googleapis.com/auth/gmail.readonly'],
    });
  }, []);

  const signIn = async () => {
    try {
      await GoogleSignin.hasPlayServices();
      const user = await GoogleSignin.signIn();
      setUserInfo(user.user);

      const tokens = await GoogleSignin.getTokens();
      console.log('✅ Access Token (printed to terminal):', tokens.accessToken);

      setStatus('Fetching last 100 emails...');

  
      const res = await axios.post('http://localhost:3000/fetch-emails', {
        accessToken: tokens.accessToken,
      });

      console.log(res.data);
      setStatus(res.data.message);
    } catch (error) {
      console.error('❌ Sign-in error:', error);
      setStatus('Error signing in or fetching emails.');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <Button title="Sign in with Google" onPress={signIn} />
      {userInfo && (
        <>
          <Text style={styles.text}>Welcome {userInfo.name}</Text>
          <Text style={styles.text}>Email: {userInfo.email}</Text>
          <ScrollView style={{ marginTop: 20 }}>
            <Text style={styles.text}>{status}</Text>
          </ScrollView>
        </>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  text: { fontSize: 14, marginVertical: 2 },
});

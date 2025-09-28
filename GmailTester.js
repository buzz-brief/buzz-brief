import React, { useEffect } from "react";
import { View, Button, Alert } from "react-native";
import { GoogleSignin } from "@react-native-google-signin/google-signin";
import axios from "axios";
import { createClient } from "@supabase/supabase-js";
import { decode as atob } from "base-64";
import { IOS_CLIENT_ID, SUPABASE_URL, SUPABASE_ANON_KEY } from "@env";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const GmailTester = () => {
  useEffect(() => {
    GoogleSignin.configure({
      iosClientId: IOS_CLIENT_ID,
      scopes: ["https://www.googleapis.com/auth/gmail.readonly"],
    });
  }, []);

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

  const fetchGmail = async () => {
    try {
      await GoogleSignin.hasPlayServices({ showPlayServicesUpdateDialog: true });
      await GoogleSignin.signIn();

      const { accessToken } = await GoogleSignin.getTokens();
      if (!accessToken) throw new Error("Access token not available");

      const messagesRes = await axios.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        {
          headers: { Authorization: `Bearer ${accessToken}` },
          params: { maxResults: 10 },
        }
      );

      const messages = messagesRes.data.messages || [];

      for (const msg of messages) {
        const msgRes = await axios.get(
          `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}`,
          { headers: { Authorization: `Bearer ${accessToken}` } }
        );

        const message = msgRes.data;
        const headers = message.payload?.headers || [];
        const subject = getHeader(headers, "Subject") || "(no subject)";
        const body = getBody(message.payload) || "";
        const created_at = new Date(parseInt(message.internalDate));

        await supabase.from("emails").insert({
          id: msg.id,
          subject,
          body,
          created_at,
        });
      }

      Alert.alert("Success", "10 Gmail messages saved to Supabase!");
    } catch (error) {
      console.error(error);
      Alert.alert("Error", `Failed to fetch Gmail messages: ${error.message}`);
    }
  };

  return (
    <View style={{ marginTop: 50, padding: 20 }}>
      <Button title="Fetch Gmail Messages" onPress={fetchGmail} />
    </View>
  );
};

export default GmailTester;

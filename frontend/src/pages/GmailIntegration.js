import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  FlatList,
  Alert,
  ActivityIndicator,
  SafeAreaView,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../context/AuthContext";
import { supabase } from "../config/supabase";

export default function GmailIntegration({ navigation }) {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const { user, googleAuth } = useAuth();

  const fetchGmailEmails = async () => {
    if (!user) {
      Alert.alert("Error", "Please sign in first!");
      return;
    }

    setLoading(true);
    try {
      console.log("Starting Gmail email fetch...");
      console.log("User authenticated:", !!user);
      console.log("Access token available:", !!googleAuth.accessToken);
      
      const emailData = await googleAuth.fetchGmailEmails(5); // Fetch only last 5 emails
      console.log("Raw email data received:", emailData);
      console.log("Number of emails fetched:", emailData?.length || 0);
      
      setEmails(emailData);
      
      if (emailData && emailData.length > 0) {
        console.log("First email sample:", emailData[0]);
        Alert.alert("Success", `Fetched ${emailData.length} emails successfully!`);
      } else {
        console.log("No emails returned from Gmail API");
        Alert.alert("Info", "No emails found in your Gmail account.");
      }
    } catch (error) {
      console.error("Error fetching Gmail emails:", error);
      console.error("Error details:", error.message, error.stack);
      Alert.alert("Error", `Failed to fetch Gmail emails: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const saveEmailsToSupabase = async () => {
    if (emails.length === 0) {
      Alert.alert("Info", "No emails to save. Please fetch emails first.");
      return;
    }

    setSaving(true);
    try {
      console.log("Saving emails to Supabase:", emails);
      
      // Ensure data format matches Supabase schema
      const formattedEmails = emails.map(email => ({
        email_id: email.email_id,
        subject: email.subject || "(no subject)",
        body: email.body || "",
        created_at: email.created_at
      }));

      console.log("Formatted emails for Supabase:", formattedEmails);

      const { data, error } = await supabase
        .from('emails')
        .insert(formattedEmails);

      if (error) {
        console.error('Supabase error details:', error);
        throw new Error(`Supabase error: ${error.message}`);
      }

      console.log("Successfully saved to Supabase:", data);
      Alert.alert("Success", `${emails.length} emails saved to Supabase database!`);
    } catch (error) {
      console.error('Supabase save error:', error);
      Alert.alert("Database Error", `Failed to save to database: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const renderEmailItem = ({ item, index }) => (
    <View style={styles.emailItem}>
      <View style={styles.emailHeader}>
        <Text style={styles.emailSubject} numberOfLines={2}>
          {item.subject}
        </Text>
        <Text style={styles.emailDate}>
          {new Date(item.created_at).toLocaleDateString()}
        </Text>
      </View>
      <Text style={styles.emailBody} numberOfLines={3}>
        {item.body}
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="white" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Gmail Integration</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={fetchGmailEmails}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <Ionicons name="mail" size={20} color="#fff" />
            )}
            <Text style={styles.buttonText}>
              {loading ? "Fetching..." : "Fetch Gmail Emails"}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.saveButton, (saving || emails.length === 0) && styles.buttonDisabled]}
            onPress={saveEmailsToSupabase}
            disabled={saving || emails.length === 0}
          >
            {saving ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <Ionicons name="save" size={20} color="#fff" />
            )}
            <Text style={styles.buttonText}>
              {saving ? "Saving..." : "Save to Database"}
            </Text>
          </TouchableOpacity>
        </View>

        {emails.length > 0 && (
          <View style={styles.resultsContainer}>
            <Text style={styles.resultsText}>
              {emails.length} email{emails.length !== 1 ? 's' : ''} fetched
            </Text>
            <FlatList
              data={emails}
              renderItem={renderEmailItem}
              keyExtractor={(item) => item.email_id}
              style={styles.emailList}
              showsVerticalScrollIndicator={false}
            />
          </View>
        )}

        {emails.length === 0 && !loading && (
          <View style={styles.emptyContainer}>
            <Ionicons name="mail-outline" size={80} color="#666" />
            <Text style={styles.emptyTitle}>No Emails Fetched</Text>
            <Text style={styles.emptySubtitle}>
              Tap "Fetch Gmail Emails" to load your recent emails
            </Text>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingTop: 20,
    paddingHorizontal: 20,
    paddingBottom: 20,
    backgroundColor: "rgba(0,0,0,0.8)",
  },
  backButton: {
    backgroundColor: "rgba(255,255,255,0.2)",
    borderRadius: 20,
    padding: 10,
    marginRight: 15,
  },
  headerTitle: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "bold",
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  buttonContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: 20,
    gap: 10,
  },
  button: {
    flex: 1,
    backgroundColor: "#FFD700",
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderRadius: 25,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
  },
  saveButton: {
    backgroundColor: "#3498db",
  },
  buttonDisabled: {
    backgroundColor: "#666",
  },
  buttonText: {
    color: "#000",
    fontSize: 16,
    fontWeight: "600",
  },
  resultsContainer: {
    flex: 1,
  },
  resultsText: {
    color: "#ccc",
    fontSize: 14,
    marginBottom: 15,
    textAlign: "center",
  },
  emailList: {
    flex: 1,
  },
  emailItem: {
    backgroundColor: "rgba(30, 30, 30, 1)",
    borderRadius: 10,
    marginBottom: 12,
    padding: 15,
    borderLeftWidth: 3,
    borderLeftColor: "#FFD700",
  },
  emailHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 8,
  },
  emailSubject: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
    flex: 1,
    marginRight: 10,
  },
  emailDate: {
    color: "#999",
    fontSize: 12,
  },
  emailBody: {
    color: "#ccc",
    fontSize: 14,
    lineHeight: 20,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 50,
  },
  emptyTitle: {
    color: "#fff",
    fontSize: 24,
    fontWeight: "bold",
    marginTop: 20,
    marginBottom: 10,
    textAlign: "center",
  },
  emptySubtitle: {
    color: "#ccc",
    fontSize: 16,
    textAlign: "center",
    lineHeight: 24,
    paddingHorizontal: 40,
  },
});

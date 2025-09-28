import React, { createContext, useContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { googleAuth } from "../services/googleAuth";

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSigningIn, setIsSigningIn] = useState(false);

  // Load user data from storage on app start
  useEffect(() => {
    loadUserFromStorage();
  }, []);

  const loadUserFromStorage = async () => {
    // Skip loading from storage since it's disabled
    console.log("Storage disabled - no user data loaded from storage");
    setIsLoading(false);
  };

  const saveUserToStorage = async (userData, accessToken) => {
    // Skip storage entirely if it's causing issues
    console.log("Storage disabled - user will need to sign in again on next app launch");
    console.log("User data:", userData);
    console.log("Access token:", accessToken);
    return;
  };

  const clearUserFromStorage = async () => {
    // Storage is disabled, so just log
    console.log("Storage disabled - no need to clear storage");
  };

  // Function to process emails for video generation
  const processEmailsForVideoGeneration = async (emailData) => {
    try {
          console.log("🎬 Processing emails for video generation...");
          console.log("📧 Total emails to process:", emailData.length);
      const { supabase } = await import('../config/supabase');
      
      // Get existing email IDs from Supabase
      const { data: existingEmails, error: fetchError } = await supabase
        .from('emails')
        .select('email_id');
      
      if (fetchError) {
        console.error('Error fetching existing emails:', fetchError);
        return;
      }
      
      const existingEmailIds = new Set(existingEmails?.map(email => email.email_id) || []);
      console.log("Existing email IDs:", Array.from(existingEmailIds));
      
      // Filter out emails that already exist
      const newEmails = emailData.filter(email => !existingEmailIds.has(email.email_id));
      console.log(`🔍 FILTERING: Found ${newEmails.length} new emails out of ${emailData.length} total emails`);
      
      if (newEmails.length === 0) {
        console.log("No new emails to process - all emails already exist in database");
        return;
      }
      
      // Process each new email individually
      for (const email of newEmails) {
        try {
          console.log(`🎥 Processing email ${email.email_id} for video generation...`);
          console.log("📧 Email subject:", email.subject);
          console.log("🔗 Backend URL:", 'http://localhost:8001/convert-email-to-video');
          
          // Create email text content for the backend
          const emailText = `Subject: ${email.subject}\n\n${email.body}`;
          
          // Call convert-email-to-video endpoint
          const response = await fetch('http://localhost:8001/convert-email-to-video', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email_text: emailText
            }),
          });

          if (response.ok) {
            const result = await response.json();
            console.log(`Successfully converted email ${email.email_id} to video:`, result);
            
            // Save email to Supabase after successful video generation
            const { error: insertError } = await supabase
              .from('emails')
              .insert([{
                email_id: email.email_id,
                subject: email.subject,
                body: email.body,
                created_at: email.created_at
              }]);

            if (insertError) {
              console.error(`Error saving email ${email.email_id} to database:`, insertError);
            } else {
              console.log(`Successfully saved email ${email.email_id} to database`);
            }
          } else {
            const errorData = await response.json();
            console.error(`Error converting email ${email.email_id} to video:`, errorData);
          }
        } catch (emailError) {
          console.error(`Error processing email ${email.email_id}:`, emailError);
        }
      }
      
      console.log(`Finished processing ${newEmails.length} new emails for video generation`);
    } catch (error) {
      console.error("Error in processEmailsForVideoGeneration:", error);
    }
  };

  const signIn = async () => {
    setIsSigningIn(true);

    try {
      const result = await googleAuth.signIn();

      if (result.success) {
        setUser(result.user);
        
        // Try to save to storage, but don't let storage failures break sign-in
        await saveUserToStorage(result.user, result.accessToken);
        
        // Automatically fetch and process Gmail emails after successful sign-in
        try {
          console.log("🚀 STARTING: Automatically fetching Gmail emails after sign-in...");
          const emailData = await googleAuth.fetchGmailEmails(5);
          console.log("📧 FETCHED EMAILS:", emailData.length, "emails");
          console.log("📧 Email IDs:", emailData.map(e => e.email_id));
          
          if (emailData && emailData.length > 0) {
            // Call batch endpoint to clear tables and process all emails
            console.log("🗑️ CLEARING TABLES: Calling batch endpoint to clear and process all emails");
            
            // Call the batch convert endpoint 
            const response = await fetch('http://localhost:8001/convert-emails-to-videos-batch', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                emails: emailData
              }),
            });

            if (response.ok) {
              const result = await response.json();
              console.log("✅ BATCH SUCCESS: All emails processed and saved to database:", result);
              console.log("📊 BATCH RESULTS:", JSON.stringify(result, null, 2));
            } else {
              const errorText = await response.text();
              console.error("❌ BATCH ERROR: Failed to process emails batch:", response.status);
              console.error("❌ BATCH ERROR DETAILS:", errorText);
            }
          }
        } catch (gmailError) {
          console.error("Error automatically fetching Gmail emails:", gmailError);
          console.log("Gmail fetch error details:", gmailError.message);
          // Don't fail the sign-in if Gmail fetch fails
        }
        
        return { success: true, user: result.user };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error("Sign in error:", error);
      return { success: false, error: error.message };
    } finally {
      setIsSigningIn(false);
    }
  };

  const signOut = async () => {
    try {
      await googleAuth.signOut();
      setUser(null);
      await clearUserFromStorage();
      return { success: true };
    } catch (error) {
      console.error("Sign out error:", error);
      return { success: false, error: error.message };
    }
  };

  const value = {
    user,
    isLoading,
    isSigningIn,
    isAuthenticated: !!user,
    signIn,
    signOut,
    googleAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

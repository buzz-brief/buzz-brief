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

  const signIn = async () => {
    setIsSigningIn(true);

    try {
      const result = await googleAuth.signIn();

      if (result.success) {
        setUser(result.user);
        
        // Try to save to storage, but don't let storage failures break sign-in
        await saveUserToStorage(result.user, result.accessToken);
        
        // Automatically fetch and save Gmail emails after successful sign-in
        try {
          console.log("Automatically fetching Gmail emails after sign-in...");
          const emailData = await googleAuth.fetchGmailEmails(5);
          console.log("Fetched emails:", emailData);
          
          if (emailData && emailData.length > 0) {
            // Save to Supabase
            const { supabase } = await import('../config/supabase');
            const { data, error } = await supabase
              .from('emails')
              .insert(emailData);

            if (error) {
              console.error('Supabase error details:', error);
            } else {
              console.log(`Successfully saved ${emailData.length} emails to Supabase database!`);
            }
          }
        } catch (gmailError) {
          console.error("Error automatically fetching Gmail emails:", gmailError);
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

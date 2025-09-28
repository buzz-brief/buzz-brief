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
    try {
      const userData = await AsyncStorage.getItem("@user");
      const accessToken = await AsyncStorage.getItem("@accessToken");

      if (userData && accessToken) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);

        // Restore the auth service state
        googleAuth.user = parsedUser;
        googleAuth.accessToken = accessToken;
      }
    } catch (error) {
      console.error("Error loading user from storage:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveUserToStorage = async (userData, accessToken) => {
    try {
      await AsyncStorage.setItem("@user", JSON.stringify(userData));
      await AsyncStorage.setItem("@accessToken", accessToken);
    } catch (error) {
      console.error("Error saving user to storage:", error);
    }
  };

  const clearUserFromStorage = async () => {
    try {
      await AsyncStorage.removeItem("@user");
      await AsyncStorage.removeItem("@accessToken");
    } catch (error) {
      console.error("Error clearing user from storage:", error);
    }
  };

  const signIn = async () => {
    setIsSigningIn(true);

    try {
      const result = await googleAuth.signIn();

      if (result.success) {
        setUser(result.user);
        await saveUserToStorage(result.user, result.accessToken);
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
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

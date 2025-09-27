import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  FlatList,
  TextInput,
  SafeAreaView,
  Linking,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { supabase } from '../config/supabase';

export default function NewPage({ navigation }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [emails, setEmails] = useState([]);
  const [filteredEmails, setFilteredEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFlaggedEmails();
  }, []);

  const loadFlaggedEmails = async () => {
    try {
      // Fetch flagged videos from Supabase database
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .eq('is_flagged', true) // Only get flagged videos
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Supabase error:', error);
        Alert.alert('Error', 'Failed to load flagged emails from database');
        return;
      }

      if (data && data.length > 0) {
        const emailList = data.map((video) => ({
          id: video.id,
          subject: video.title || 'Untitled Video',
          flagged: video.is_flagged,
          video_url: video.video_url,
          created_at: video.created_at,
        }));

        console.log('Loaded flagged emails from Supabase:', emailList);
        setEmails(emailList);
        setFilteredEmails(emailList);
      } else {
        console.log('No flagged emails found in database');
        setEmails([]);
        setFilteredEmails([]);
      }
    } catch (error) {
      console.error('Error loading flagged emails from Supabase:', error);
      Alert.alert('Error', 'Failed to load flagged emails');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.trim() === '') {
      setFilteredEmails(emails);
    } else {
      const filtered = emails.filter(email =>
        email.subject.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredEmails(filtered);
    }
  };

  const handleDeleteEmail = async (emailId) => {
    try {
      // Update the database to unflag the video
      const { error } = await supabase
        .from('videos')
        .update({ is_flagged: false })
        .eq('id', emailId);

      if (error) {
        console.error('Error updating flag status:', error);
        Alert.alert('Error', 'Failed to remove email from flagged list');
        return;
      }

      // Update local state
      const updatedEmails = emails.filter(email => email.id !== emailId);
      setEmails(updatedEmails);

      // Update filtered emails based on current search
      if (searchQuery.trim() === '') {
        setFilteredEmails(updatedEmails);
      } else {
        const filtered = updatedEmails.filter(email =>
          email.subject.toLowerCase().includes(searchQuery.toLowerCase())
        );
        setFilteredEmails(filtered);
      }
    } catch (error) {
      console.error('Error handling delete email:', error);
      Alert.alert('Error', 'Failed to remove email from flagged list');
    }
  };

  const handleEmailPress = async (email) => {
    try {
      // Try to open Gmail app first
      const gmailUrl = 'googlegmail://';
      const canOpenGmail = await Linking.canOpenURL(gmailUrl);
      
      if (canOpenGmail) {
        await Linking.openURL(gmailUrl);
      } else {
        // Fallback to Gmail web version
        const gmailWebUrl = 'https://mail.google.com';
        await Linking.openURL(gmailWebUrl);
      }
    } catch (error) {
      Alert.alert(
        'Error',
        'Could not open Gmail. Please make sure Gmail is installed on your device.',
        [{ text: 'OK' }]
      );
    }
  };

  const renderEmailItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.emailItem}
      onPress={() => handleEmailPress(item)}
      activeOpacity={0.7}
    >
      <View style={styles.emailContent}>
        <Text style={styles.emailSubject}>{item.subject}</Text>
        <TouchableOpacity
          style={styles.deleteButton}
          onPress={(e) => {
            e.stopPropagation(); // Prevent triggering the email press
            handleDeleteEmail(item.id);
          }}
        >
          <Ionicons name="trash" size={20} color="#ff4444" />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
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
        <Text style={styles.headerTitle}>Flagged Emails</Text>
      </View>
      
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#666" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search flagged emails..."
          placeholderTextColor="#666"
          value={searchQuery}
          onChangeText={handleSearch}
        />
      </View>

          <View style={styles.content}>
            {loading ? (
              <View style={styles.loadingContainer}>
                <Text style={styles.loadingText}>Loading flagged emails...</Text>
              </View>
            ) : (
              <>
                <Text style={styles.resultsText}>
                  {filteredEmails.length} flagged email{filteredEmails.length !== 1 ? 's' : ''}
                </Text>

                <FlatList
                  data={filteredEmails}
                  renderItem={renderEmailItem}
                  keyExtractor={(item) => item.id}
                  style={styles.emailList}
                  showsVerticalScrollIndicator={false}
                />
              </>
            )}
          </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 20,
    paddingHorizontal: 20,
    paddingBottom: 20,
    backgroundColor: 'rgba(0,0,0,0.8)',
  },
  backButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 20,
    padding: 10,
    marginRight: 15,
  },
  headerTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 25,
    paddingHorizontal: 15,
    paddingVertical: 10,
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  resultsText: {
    color: '#ccc',
    fontSize: 14,
    marginBottom: 15,
    textAlign: 'center',
  },
  emailList: {
    flex: 1,
  },
  emailItem: {
    backgroundColor: 'rgba(30, 30, 30, 1)',
    borderRadius: 10,
    marginBottom: 12,
    padding: 15,
    borderLeftWidth: 3,
    borderLeftColor: '#FFD700',
  },
  emailContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  emailSubject: {
    color: '#fff',
    fontSize: 16,
    flex: 1,
    lineHeight: 22,
    marginRight: 15,
  },
  deleteButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(255,68,68,0.1)',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  loadingText: {
    color: '#CCCCCC',
    fontSize: 16,
  },
});

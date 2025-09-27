import React, { useState } from 'react';
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

// Hardcoded flagged emails data
const flaggedEmails = [
  { id: '1', subject: 'Urgent: Project deadline approaching', flagged: true },
  { id: '2', subject: 'Meeting notes from yesterday', flagged: true },
  { id: '3', subject: 'Important: Budget review required', flagged: true },
  { id: '4', subject: 'Client feedback on latest proposal', flagged: true },
  { id: '5', subject: 'Team building event this Friday', flagged: true },
  { id: '6', subject: 'Security update for all systems', flagged: true },
  { id: '7', subject: 'Quarterly report due next week', flagged: true },
  { id: '8', subject: 'New hire onboarding schedule', flagged: true },
  { id: '9', subject: 'Vendor contract renewal', flagged: true },
  { id: '10', subject: 'Performance review reminders', flagged: true },
];

export default function NewPage({ navigation }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [emails, setEmails] = useState(flaggedEmails);
  const [filteredEmails, setFilteredEmails] = useState(flaggedEmails);

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

  const handleDeleteEmail = (emailId) => {
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
});

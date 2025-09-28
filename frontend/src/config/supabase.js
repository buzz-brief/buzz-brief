import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://ousfnryoohuxwhbhagdw.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im91c2Zucnlvb2h1eHdoYmhhZ2R3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5NTgxMzUsImV4cCI6MjA3NDUzNDEzNX0.fRUb-ZrSIMVBqHYwh79F85PtuzeP4TRr33Ufc0ssOCM';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

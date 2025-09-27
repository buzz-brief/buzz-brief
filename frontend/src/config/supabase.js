import { createClient } from '@supabase/supabase-js';
import { EXPO_PUBLIC_SUPABASE_URL, EXPO_PUBLIC_SUPABASE_ANON_KEY } from '@env';

console.log("SUPABASE_URL: ")
console.log(EXPO_PUBLIC_SUPABASE_URL)
console.log("SUPABASE_ANON_KEY: ")
console.log(EXPO_PUBLIC_SUPABASE_ANON_KEY)

export const supabase = createClient(EXPO_PUBLIC_SUPABASE_URL, EXPO_PUBLIC_SUPABASE_ANON_KEY);

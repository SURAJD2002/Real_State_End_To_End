import { createClient } from '@supabase/supabase-js';

// Supabase Client for Planwise Enterprise Web Application
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://qhqneldjxxdnttqfhqkf.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFocW5lbGRqeHhkbnR0cWZocWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTE1ODI1MjksImV4cCI6MjEwNzE1ODUyOX0.06ubl_7j5pCx5gOldlTCmcljCVtn5uqPAIwh0rpgYCE';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    storage: typeof window !== 'undefined' ? window.localStorage : undefined
  }
});

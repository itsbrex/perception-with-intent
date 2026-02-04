import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'

// Firebase configuration from environment variables
// For local development, create a .env.local file with these values
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyDKepIwaNZ21uHhHfmg--XBZUojTEz2V24",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "perception-with-intent.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "perception-with-intent",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "perception-with-intent.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "348724539390",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:348724539390:web:3470ff3774e52529fd1aaf",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-KNVNVB9RM3"
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize services
export const auth = getAuth(app)
export const db = getFirestore(app)

export default app

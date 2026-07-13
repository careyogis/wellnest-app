import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAJ3rM1PfdwU1H4epg-YSlLlzmSyntiIR4",
  authDomain: "careyogi-dev.firebaseapp.com",
  projectId: "careyogi-dev",
  storageBucket: "careyogi-dev.firebasestorage.app",
  messagingSenderId: "229937245647",
  appId: "1:229937245647:web:b7206cd684442aa70376ba",
  measurementId: "G-WEMYVDHF2P",
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
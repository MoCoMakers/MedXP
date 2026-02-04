import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Nurse, Patient, Session, Notification, Transcript, Classification } from '../types';

interface AppState {
  // User state
  currentUser: Nurse | null;
  isAuthenticated: boolean;

  // UI state
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';

  // Data state
  nurses: Nurse[];
  patients: Patient[];
  sessions: Session[];
  notifications: Notification[];
  selectedSession: Session | null;
  selectedTranscript: Transcript | null;
  selectedClassification: Classification | null;

  // Loading states
  isLoading: boolean;
  loadingMessage: string;

  // Actions
  setCurrentUser: (user: Nurse | null) => void;
  setAuthenticated: (authenticated: boolean) => void;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleTheme: () => void;

  setNurses: (nurses: Nurse[]) => void;
  addNurse: (nurse: Nurse) => void;
  updateNurse: (id: string, data: Partial<Nurse>) => void;
  removeNurse: (id: string) => void;

  setPatients: (patients: Patient[]) => void;
  addPatient: (patient: Patient) => void;
  updatePatient: (id: string, data: Partial<Patient>) => void;
  removePatient: (id: string) => void;

  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  updateSession: (id: string, data: Partial<Session>) => void;
  removeSession: (id: string) => void;
  setSelectedSession: (session: Session | null) => void;

  setNotifications: (notifications: Notification[]) => void;
  addNotification: (notification: Notification) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  removeNotification: (id: string) => void;

  setSelectedTranscript: (transcript: Transcript | null) => void;
  setSelectedClassification: (classification: Classification | null) => void;

  setLoading: (loading: boolean, message?: string) => void;

  reset: () => void;
}

const initialState = {
  currentUser: null,
  isAuthenticated: false,
  sidebarOpen: true,
  sidebarCollapsed: false,
  theme: 'light' as const,
  nurses: [],
  patients: [],
  sessions: [],
  notifications: [],
  selectedSession: null,
  selectedTranscript: null,
  selectedClassification: null,
  isLoading: false,
  loadingMessage: '',
};

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        setCurrentUser: (user) => set({ currentUser: user }),
        setAuthenticated: (authenticated) => set({ isAuthenticated: authenticated }),

        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
        setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
        toggleTheme: () =>
          set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),

        setNurses: (nurses) => set({ nurses }),
        addNurse: (nurse) =>
          set((state) => ({ nurses: [...state.nurses, nurse] })),
        updateNurse: (id, data) =>
          set((state) => ({
            nurses: state.nurses.map((n) =>
              n.id === id ? { ...n, ...data } : n
            ),
          })),
        removeNurse: (id) =>
          set((state) => ({
            nurses: state.nurses.filter((n) => n.id !== id),
          })),

        setPatients: (patients) => set({ patients }),
        addPatient: (patient) =>
          set((state) => ({ patients: [...state.patients, patient] })),
        updatePatient: (id, data) =>
          set((state) => ({
            patients: state.patients.map((p) =>
              p.id === id ? { ...p, ...data } : p
            ),
          })),
        removePatient: (id) =>
          set((state) => ({
            patients: state.patients.filter((p) => p.id !== id),
          })),

        setSessions: (sessions) => set({ sessions }),
        addSession: (session) =>
          set((state) => ({ sessions: [...state.sessions, session] })),
        updateSession: (id, data) =>
          set((state) => ({
            sessions: state.sessions.map((s) =>
              s.id === id ? { ...s, ...data } : s
            ),
          })),
        removeSession: (id) =>
          set((state) => ({
            sessions: state.sessions.filter((s) => s.id !== id),
          })),
        setSelectedSession: (session) => set({ selectedSession: session }),

        setNotifications: (notifications) => set({ notifications }),
        addNotification: (notification) =>
          set((state) => ({
            notifications: [notification, ...state.notifications],
          })),
        markNotificationRead: (id) =>
          set((state) => ({
            notifications: state.notifications.map((n) =>
              n.id === id ? { ...n, isRead: true } : n
            ),
          })),
        markAllNotificationsRead: () =>
          set((state) => ({
            notifications: state.notifications.map((n) => ({ ...n, isRead: true })),
          })),
        removeNotification: (id) =>
          set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          })),

        setSelectedTranscript: (transcript) => set({ selectedTranscript: transcript }),
        setSelectedClassification: (classification) =>
          set({ selectedClassification: classification }),

        setLoading: (loading, message = '') =>
          set({ isLoading: loading, loadingMessage: message }),

        reset: () => set(initialState),
      }),
      {
        name: 'medxp-storage',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
        }),
      }
    ),
    { name: 'MedXP Store' }
  )
);

export default useAppStore;

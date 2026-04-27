import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import API_ENDPOINTS from '../config/api'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (username, password) => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch(API_ENDPOINTS.AUTH.LOGIN, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password }),
          })

          const data = await response.json()

          if (response.ok) {
            set({ user: data.user, isAuthenticated: true, isLoading: false })
            return { success: true }
          } else {
            set({ error: data.message, isLoading: false })
            return { success: false, message: data.message }
          }
        } catch (error) {
          set({ error: error.message, isLoading: false })
          return { success: false, message: 'Network error' }
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch(API_ENDPOINTS.AUTH.REGISTER, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(userData),
          })

          const data = await response.json()

          if (response.ok) {
            set({ user: data.user, isAuthenticated: true, isLoading: false })
            return { success: true }
          } else {
            set({ error: data.message, isLoading: false })
            return { success: false, message: data.message }
          }
        } catch (error) {
          set({ error: error.message, isLoading: false })
          return { success: false, message: 'Network error' }
        }
      },

      logout: async () => {
        try {
          await fetch(API_ENDPOINTS.AUTH.LOGOUT, {
            method: 'POST',
            credentials: 'include',
          })
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({ user: null, isAuthenticated: false, error: null })
          localStorage.removeItem('auth-storage')
        }
      },

      checkAuth: async () => {
        try {
          const response = await fetch(API_ENDPOINTS.AUTH.ME, {
            credentials: 'include',
          })

          if (response.ok) {
            const data = await response.json()
            set({ user: data.user, isAuthenticated: true })
            return true
          } else {
            set({ user: null, isAuthenticated: false })
            return false
          }
        } catch (error) {
          set({ user: null, isAuthenticated: false })
          return false
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

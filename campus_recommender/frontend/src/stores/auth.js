import { defineStore } from 'pinia'
import axios from 'axios'
import router from '../router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    isAdmin: false
  }),

  actions: {
    async login(username, password, isAdminLogin = true) {
      try {
        console.log('Auth store: login attempt', { username, isAdminLogin });

        // Clear any existing user data before login
        this.clearUserData()

        let response;
        if (isAdminLogin) {
          // Admin login
          response = await axios.post('/api/admins/login/', { username, password });
          this.isAdmin = true;

          this.token = response.data.token;
          this.user = response.data.user;
        } else {
          // Regular student login
          response = await axios.post('/api/students/login/', { student_id: username, password });
          this.isAdmin = false;
          
          this.token = response.data.token;
          this.user = {
            id: response.data.id,
            user_id: response.data.user_id,
            username: response.data.username,
            student_id: response.data.student_id,
            email: response.data.email
          };
        }
        
        console.log('Auth store: login response received', response.data);
        
        console.log('Auth store: Saving user data to localStorage', this.user);
        localStorage.setItem('token', this.token);
        localStorage.setItem('user', JSON.stringify(this.user));
        localStorage.setItem('isAdmin', JSON.stringify(this.isAdmin));
        
        console.log('Auth store: Setting Authorization header');
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`;
        
        return true;
      } catch (error) {
        console.error('Auth store: Login error:', error);
        if (error.response) {
          console.error('Auth store: Response status', error.response.status);
          console.error('Auth store: Response data', error.response.data);
        }
        throw error;
      }
    },

    async logout() {
      try {
        if (this.token) {
          await axios.post('/api/students/logout/', {}, {
            headers: { Authorization: `Token ${this.token}` }
          })
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.clearUserData()
        router.push('/login')
      }
    },

    // Clear all user-specific data from localStorage
    clearUserData() {
      console.log('Auth store: Clearing all user data')
      // Clear authentication data
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('isAdmin')

      // Clear user-specific application data
      localStorage.removeItem('appliedClubs')
      localStorage.removeItem('favoritedClubs')
      localStorage.removeItem('likedClubs')

      // Reset store state
      this.token = null
      this.user = null
      this.isAdmin = false
      delete axios.defaults.headers.common['Authorization']
    },

    async register(formData) {
      try {
        // Clear any existing user data before registration
        this.clearUserData()

        // Call student registration endpoint
        const response = await axios.post('/api/students/register/', formData)
        // Save token and user info
        this.token = response.data.token
        this.user = {
          id: response.data.user_id,
          student_id: response.data.student_id,
          email: response.data.email,
          full_name: response.data.full_name
        }
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`
        return response.data
      } catch (error) {
        console.error('Auth store: Registration error:', error)
        throw error
      }
    },

    updateUser(userData) {
      this.user = { ...this.user, ...userData }
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    // Initialize auth state from localStorage
    init() {
      const token = localStorage.getItem('token')
      if (token) {
        this.token = token
        axios.defaults.headers.common['Authorization'] = `Token ${token}`
        this.user = JSON.parse(localStorage.getItem('user'))
        this.isAdmin = JSON.parse(localStorage.getItem('isAdmin') || 'false')
      }
    }
  },

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  }
}) 
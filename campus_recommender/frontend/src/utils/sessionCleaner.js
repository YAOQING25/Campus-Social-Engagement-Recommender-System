// Session Cleaner Utility
// Provides comprehensive session and data cleaning functions

import axios from 'axios'

/**
 * Completely clear all user session data and application state
 */
export const clearAllUserData = () => {
  console.log('SessionCleaner: Clearing all user data')
  
  // Clear localStorage
  const localStorageKeys = [
    'token',
    'user',
    'isAdmin',
    'appliedClubs',
    'favoritedClubs',
    'likedClubs',
    'adminToken',
    'userPreferences',
    'searchHistory',
    'viewHistory'
  ]
  
  localStorageKeys.forEach(key => {
    localStorage.removeItem(key)
  })
  
  // Clear sessionStorage
  sessionStorage.clear()
  
  // Clear axios authorization header
  delete axios.defaults.headers.common['Authorization']
  
  // Clear any cached data in memory (if any)
  // This would be where you'd clear any global state stores
  
  console.log('SessionCleaner: All user data cleared')
}

/**
 * Clear only authentication-related data
 */
export const clearAuthData = () => {
  console.log('SessionCleaner: Clearing authentication data')
  
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('isAdmin')
  localStorage.removeItem('adminToken')
  delete axios.defaults.headers.common['Authorization']
  
  console.log('SessionCleaner: Authentication data cleared')
}

/**
 * Clear only application-specific data (keep auth)
 */
export const clearAppData = () => {
  console.log('SessionCleaner: Clearing application data')
  
  const appDataKeys = [
    'appliedClubs',
    'favoritedClubs',
    'likedClubs',
    'userPreferences',
    'searchHistory',
    'viewHistory'
  ]
  
  appDataKeys.forEach(key => {
    localStorage.removeItem(key)
  })
  
  console.log('SessionCleaner: Application data cleared')
}

/**
 * Prepare for new user registration
 */
export const prepareForNewUser = () => {
  console.log('SessionCleaner: Preparing for new user registration')
  
  // Clear all existing data
  clearAllUserData()
  
  // Additional cleanup for registration
  sessionStorage.clear()
  
  // Clear any form auto-fill data that might be cached
  if (window.history && window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href)
  }
  
  console.log('SessionCleaner: Ready for new user registration')
}

/**
 * Prepare for user login
 */
export const prepareForLogin = () => {
  console.log('SessionCleaner: Preparing for user login')
  
  // Clear existing session but preserve some app state if needed
  clearAuthData()
  clearAppData()
  
  console.log('SessionCleaner: Ready for user login')
}

export default {
  clearAllUserData,
  clearAuthData,
  clearAppData,
  prepareForNewUser,
  prepareForLogin
}

import { ref, reactive } from 'vue'

// Global notification state
const notifications = ref([])
let notificationId = 0

export function useNotifications() {
  const addNotification = (notification) => {
    const id = ++notificationId
    const newNotification = {
      id,
      type: 'info',
      duration: 5000,
      autoClose: true,
      ...notification,
      show: true
    }
    
    notifications.value.push(newNotification)
    
    // Auto-remove if autoClose is enabled
    if (newNotification.autoClose && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }
    
    return id
  }
  
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  const clearAll = () => {
    notifications.value = []
  }
  
  // Convenience methods
  const success = (title, message = '', options = {}) => {
    return addNotification({
      type: 'success',
      title,
      message,
      ...options
    })
  }
  
  const error = (title, message = '', options = {}) => {
    return addNotification({
      type: 'error',
      title,
      message,
      duration: 8000, // Longer duration for errors
      ...options
    })
  }
  
  const warning = (title, message = '', options = {}) => {
    return addNotification({
      type: 'warning',
      title,
      message,
      ...options
    })
  }
  
  const info = (title, message = '', options = {}) => {
    return addNotification({
      type: 'info',
      title,
      message,
      ...options
    })
  }
  
  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  }
}

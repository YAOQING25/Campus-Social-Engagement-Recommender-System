import axios from 'axios';

const TOKEN_KEY = 'token';
const USER_KEY = 'user';
const ADMIN_ID_KEY = 'adminId';

export const setAuth = (token, user) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  setAuthHeader(token);
  
  // If user has an ID and is an admin, save the ID separately
  if (user && user.id) {
    setAdminId(user.id);
  }
};

export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const getUser = () => {
  const userJson = localStorage.getItem(USER_KEY);
  return userJson ? JSON.parse(userJson) : null;
};

export const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(ADMIN_ID_KEY);
  localStorage.removeItem('isAdmin');
  delete axios.defaults.headers.common['Authorization'];
};

export const setAuthHeader = (token) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`;
  }
};

export const isAuthenticated = () => {
  const token = getToken();
  console.log('Auth utils: isAuthenticated check, token exists:', !!token);
  return !!token;
};

export const isAdmin = () => {
  const isAdminFlag = JSON.parse(localStorage.getItem('isAdmin') || 'false');
  console.log('Auth utils: isAdmin check, flag:', isAdminFlag);
  return isAdminFlag;
};

export const setAdminId = (id) => {
  if (id) {
    localStorage.setItem(ADMIN_ID_KEY, id.toString());
  }
};

export const getAdminId = () => {
  return localStorage.getItem(ADMIN_ID_KEY);
};

// Initialize axios header with the token on app startup
const initAuth = () => {
  const token = getToken();
  if (token) {
    console.log('Auth utils: Initializing with token');
    setAuthHeader(token);
  } else {
    console.log('Auth utils: No token found during initialization');
  }
};

// Call initialization
initAuth(); 
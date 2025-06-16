import { createRouter, createWebHistory } from 'vue-router'
import AdminProfile from '@/views/admin/AdminProfile.vue'
import { isAuthenticated, isAdmin, getUser } from '@/utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/frontend/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/frontend/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../views/frontend/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/club/:id',
      name: 'clubDetail',
      component: () => import('../views/frontend/ClubDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/frontend/Profile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/login',
      name: 'adminLogin',
      component: () => import('../views/admin/AdminLogin.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/admin',
      component: () => import('../views/admin/components/AdminLayout.vue'),
      meta: { requiresAuth: true, isAdmin: true },
      children: [
        {
          path: 'home',
          name: 'adminHome',
          component: () => import('../views/admin/AdminHome.vue')
        },
        {
          path: 'students',
          name: 'studentManagement',
          component: () => import('../views/admin/StudentManagement.vue')
        },
        {
          path: 'admins',
          name: 'adminManagement',
          component: () => import('../views/admin/AdminManagement.vue')
        },
        {
          path: 'clubs',
          name: 'clubManagement',
          component: () => import('../views/admin/ClubManagement.vue')
        },
        {
          path: 'categories',
          name: 'categoryManagement',
          component: () => import('../views/admin/CategoryManagement.vue')
        },
        {
          path: 'applications',
          name: 'applicationManagement',
          component: () => import('../views/admin/ApplicationManagement.vue')
        },
        {
          path: 'profile',
          name: 'adminProfile',
          component: () => import('../views/admin/AdminProfile.vue')
        }
      ]
    },
    {
      path: '/recommended',
      name: 'recommended',
      component: () => import('../views/frontend/RecommendedClubs.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: () => import('../views/frontend/FavoriteClubs.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/profile',
      name: 'AdminProfile',
      component: AdminProfile,
      meta: {
        requiresAuth: true,
        isAdmin: true
      }
    },
    {
      path: '/category-club',
      name: 'categoryClub',
      component: () => import('../views/CategoryClub.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresAdmin = to.matched.some(record => record.meta.isAdmin);
  
  console.log(`Navigation to ${to.path}, requiresAuth: ${requiresAuth}, requiresAdmin: ${requiresAdmin}`);
  
  const authenticated = isAuthenticated();
  console.log(`User authenticated: ${authenticated}`);
  
  // Check if route requires authentication
  if (requiresAuth && !authenticated) {
    console.log('Route requires authentication but user is not authenticated. Redirecting to login.');
    // Not authenticated, redirect to login
    next('/login');
  } 
  // Check if route requires admin privileges
  else if (requiresAdmin && (!authenticated || !isAdmin())) {
    console.log('Route requires admin privileges but user is not admin. Redirecting appropriately.');
    // Not admin, redirect to login or home
    next(authenticated ? '/home' : '/login');
  } 
  // Prevent authenticated users from accessing login/register pages
  else if (authenticated && (to.name === 'login' || to.name === 'register')) {
    console.log('User is authenticated and trying to access login/register. Redirecting to home.');
    // Already authenticated, redirect to home
    next(isAdmin() ? '/admin' : '/home');
  } 
  else {
    console.log('Proceeding with navigation normally.');
    // Otherwise proceed normally
    next();
  }
});

export default router 
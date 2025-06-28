<template>
  <div class="admin-management">
    <div class="header">
      <h1>Admin Management</h1>
      <div class="header-actions">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Search by name or ID..."
          >
        </div>
        <select v-model="roleFilter" class="role-filter">
          <option value="">All Roles</option>
          <option value="super">Super Admin</option>
          <option value="manager">Manager</option>
          <option value="staff">Staff</option>
        </select>
        <button class="reset-btn" @click="resetFilters" title="Reset Filters" v-if="searchQuery || roleFilter">
          <i class="bi bi-x-circle"></i> Reset
        </button>
        <button class="add-btn" @click="showAddModal = true">
          <i class="bi bi-plus-lg"></i> Add Admin
        </button>
        <AdminProfileDropdown class="profile-dropdown" />
      </div>
    </div>

    <div class="content">
      <div class="table-wrapper" :class="{ loading }">
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
          <div>Loading...</div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Admin ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Last Login</th>
              <th>Status</th>
              <th class="actions-th">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="admin in admins" :key="admin.id">
              <td>{{ admin.id }}</td>
              <td>{{ admin.name }}</td>
              <td>{{ admin.email }}</td>
              <td>
                <span class="role-badge" :class="admin.role">
                  {{ admin.role }}
                </span>
              </td>
              <td>{{ admin.lastLogin }}</td>
              <td>
                <span class="status" :class="admin.status">
                  {{ admin.status }}
                </span>
              </td>
              <td class="actions">
                <button class="icon-btn edit" @click="openEdit(admin)" title="Edit">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="icon-btn reset" @click="openReset(admin)" title="Reset Password">
                  <i class="bi bi-key"></i>
                </button>
                <button 
                  class="icon-btn delete" 
                  v-if="admin.role !== 'super'"
                  @click="openDelete(admin)"
                  title="Delete"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button class="page-btn" :disabled="currentPage === 1" @click="prevPage">
          <i class="bi bi-chevron-left"></i>
        </button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="nextPage">
          <i class="bi bi-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Add/Edit Admin Modal -->
    <Modal
      v-if="showAddModal || showEditModal"
      :title="showEditModal ? 'Edit Admin' : 'Add New Admin'"
      :show="showAddModal || showEditModal"
      @close="closeModal"
    >
      <AdminForm
        :admin="selectedAdmin"
        :is-edit="showEditModal"
        :roles="roles"
        @submit="handleSubmit"
        @cancel="closeModal"
      />
    </Modal>

    <!-- Reset Password Modal -->
    <Modal
      v-if="showResetModal"
      title="Reset Admin Password"
      :show="showResetModal"
      @close="closeModal"
    >
      <div class="reset-form">
        <label>New Password:</label>
        <input type="password" v-model="resetPassword" />
        <div class="form-actions">
          <button class="submit-btn" @click="handleReset">Reset</button>
          <button class="cancel-btn" @click="closeModal">Cancel</button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import AdminProfileDropdown from '@/components/AdminProfileDropdown.vue'
import Modal from '@/components/Modal.vue'
import AdminForm from '@/components/AdminForm.vue'
import axios from 'axios'

const admins = ref([])
const roles = ['super', 'manager', 'staff']
const searchQuery = ref('')
const roleFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const totalPages = ref(1)
const loading = ref(false)

const showAddModal = ref(false)
const showEditModal = ref(false)
const showResetModal = ref(false)
const selectedAdmin = ref(null)
const resetPassword = ref('')

const baseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? `http://${window.location.hostname}:8000`
  : `${window.location.protocol}//${window.location.host}`

// Add auth token to axios requests if available
const getAuthHeaders = () => {
  const token = localStorage.getItem('adminToken')
  return token ? {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  } : {
    'Content-Type': 'application/json'
  }
}

async function fetchAdmins() {
  loading.value = true
  // Create proper query parameters object, matching what the backend expects
  const params = { 
    page: currentPage.value,
  }
  
  // Only add these parameters if they have values
  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  
  if (roleFilter.value) {
    params.role = roleFilter.value
  }
  
  try {
    console.log('Fetching admins from:', `${baseUrl}/api/admins/`, 'with params:', params)
    const res = await axios.get(`${baseUrl}/api/admins/`, { 
      params,
      headers: getAuthHeaders()
    })
    console.log('Admins response:', res.data)
    if (res.data.results) {
      admins.value = res.data.results
      totalPages.value = Math.ceil(res.data.count / itemsPerPage)
    } else {
      admins.value = res.data
      totalPages.value = Math.ceil(admins.value.length / itemsPerPage)
    }
  } catch (err) {
    console.error('Error fetching admins:', err)
    console.error('Error details:', err.response?.data || err.message)
    alert(`Failed to fetch admins: ${err.response?.status || ''} ${err.response?.statusText || err.message}`)
  } finally {
    loading.value = false
  }
}

onMounted(fetchAdmins)

// Reset to page 1 when filters change to prevent empty results
watch([searchQuery], () => {
  currentPage.value = 1
  fetchAdmins()
})

// Separate watcher for roleFilter to see when it changes
watch([roleFilter], (newValue) => {
  console.log('Role filter changed to:', newValue)
  currentPage.value = 1
  fetchAdmins()
})

// Only watch currentPage without automatically triggering fetchAdmins
watch([currentPage], () => {
  fetchAdmins()
})

function resetFilters() {
  searchQuery.value = ''
  roleFilter.value = ''
  currentPage.value = 1
  fetchAdmins()
}

function prevPage() { if (currentPage.value > 1) currentPage.value-- }
function nextPage() { if (currentPage.value < totalPages.value) currentPage.value++ }

async function handleSubmit(form) {
  try {
    if (showEditModal.value) {
      const formattedData = {
        email: form.email,
        first_name: form.first_name,
        last_name: form.last_name,
        role: form.role,
        status: form.status
      }
      console.log('Updating admin:', selectedAdmin.value.id, formattedData);
      await axios.patch(`${baseUrl}/api/admins/${selectedAdmin.value.id}/`, formattedData, {
        headers: getAuthHeaders()
      })
    } else {
      console.log('Creating admin:', form);
      await axios.post(`${baseUrl}/api/admins/`, form, {
        headers: getAuthHeaders()
      })
    }
    closeModal()
    fetchAdmins()
  } catch (err) {
    console.error('Error saving admin:', err)
    console.error('Error details:', err.response?.data || err.message)
    alert(err.response?.data?.detail || `Failed to save admin: ${err.message}`)
  }
}

function openEdit(admin) { 
  selectedAdmin.value = { 
    id: admin.id,
    username: admin.username,
    email: admin.email,
    first_name: admin.name.split(' ')[0] || '',
    last_name: admin.name.split(' ')[1] || '',
    role: admin.role,
    status: admin.status
  }
  showEditModal.value = true 
}

function openDelete(admin) { if (confirm(`Delete ${admin.name}?`)) deleteAdmin(admin) }

async function deleteAdmin(admin) { 
  try { 
    console.log('Deleting admin:', admin.id);
    await axios.delete(`${baseUrl}/api/admins/${admin.id}/`, {
      headers: getAuthHeaders()
    }); 
    fetchAdmins() 
  } catch (err) { 
    console.error('Delete error:', err);
    console.error('Error details:', err.response?.data || err.message)
    alert(err.response?.data?.error || `Failed to delete admin: ${err.message}`)
  }
}

function openReset(admin) { selectedAdmin.value = admin; showResetModal.value = true }
async function handleReset() {
  try {
    console.log('Resetting password for admin:', selectedAdmin.value.id);
    await axios.post(`${baseUrl}/api/admins/${selectedAdmin.value.id}/reset_password/`, 
      { password: resetPassword.value },
      { headers: getAuthHeaders() }
    )
    alert('Password reset successfully')
    closeModal()
  } catch (err) {
    console.error('Reset error:', err)
    console.error('Error details:', err.response?.data || err.message)
    alert(err.response?.data?.error || `Failed to reset password: ${err.message}`)
  }
}

function closeModal() {
  showAddModal.value = false; showEditModal.value = false; showResetModal.value = false;
  selectedAdmin.value = null; resetPassword.value = ''
}
</script>

<style scoped>
.admin-management {
  min-height: 100vh;
  background: #f3f4f6;
  color: #64748b;
  padding: 2rem;
}

.header {
  margin-bottom: 2rem;
}

h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  background: #2d3748;
  border: 1px solid #4a5568;
  border-radius: 0.5rem;
  color: #e2e8f0;
  outline: none;
}

select {
  padding: 0.75rem 1rem;
  background: #2d3748;
  border: 1px solid #4a5568;
  border-radius: 0.5rem;
  color: #e2e8f0;
  outline: none;
  cursor: pointer;
  min-width: 150px;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.add-btn:hover {
  background: #4338ca;
}

.reset-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #64748b;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: #475569;
}

.role-filter {
  min-width: 150px;
  padding: 0.75rem 1rem;
  background: #2d3748;
  border: 1px solid #4a5568;
  border-radius: 0.5rem;
  color: #e2e8f0;
  outline: none;
  cursor: pointer;
}

.content {
  background: #2d3748;
  border-radius: 1rem;
  overflow: hidden;
  position: relative;
}

.table-wrapper {
  overflow-x: auto;
  position: relative;
  min-height: 300px;
}

.table-wrapper.loading {
  opacity: 0.7;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #4a5568;
  vertical-align: middle;
}

th {
  background: #1f2937;
  font-weight: 500;
  color: #94a3b8;
}

tbody tr {
  background: #2d3748;
}

tbody tr:hover {
  background: #374151;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.role-badge.super {
  background: #4c1d95;
  color: #ddd6fe;
}

.role-badge.manager {
  background: #1e40af;
  color: #bfdbfe;
}

.role-badge.staff {
  background: #1e3a8a;
  color: #93c5fd;
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status.active {
  background: #064e3b;
  color: #34d399;
}

.status.inactive {
  background: #7f1d1d;
  color: #fca5a5;
}

.actions {
  padding: 0.5rem;
  width: 120px;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn i {
  font-size: 1rem;
}

.icon-btn.edit {
  background: #3730a3;
  color: #c7d2fe;
}

.icon-btn.edit:hover {
  background: #4338ca;
  transform: translateY(-1px);
}

.icon-btn.reset {
  background: #0d9488;
  color: #99f6e4;
}

.icon-btn.reset:hover {
  background: #0f766e;
  transform: translateY(-1px);
}

.icon-btn.delete {
  background: #991b1b;
  color: #fca5a5;
}

.icon-btn.delete:hover {
  background: #b91c1c;
  transform: translateY(-1px);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid #4a5568;
}

.page-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #4a5568;
  border-radius: 0.375rem;
  background: #1f2937;
  color: #e2e8f0;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-management {
    padding: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    width: 100%;
  }
  
  select {
    width: 100%;
  }
  
  .add-btn {
    width: 100%;
    justify-content: center;
  }
  
  .actions {
    flex-wrap: nowrap;
  }
}

/* 工具提示 */
.icon-btn {
  position: relative;
}

.icon-btn:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.25rem 0.5rem;
  background: #1f2937;
  color: #e2e8f0;
  font-size: 0.75rem;
  border-radius: 4px;
  white-space: nowrap;
  margin-bottom: 0.5rem;
}

.profile-dropdown {
  margin-left: 1rem;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 
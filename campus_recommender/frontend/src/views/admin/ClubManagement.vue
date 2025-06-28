<template>
  <div class="club-management">
    <div class="header">
      <h1>Club Management</h1>
      <div class="header-actions">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Search clubs..."
          >
        </div>
        <select v-model="categoryFilter">
          <option value="">All Categories</option>
          <option v-for="category in categoriesList" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
        <button class="add-btn" @click="showAddModal = true">
          <i class="bi bi-plus-lg"></i>
          Add Club
        </button>
        <AdminProfileDropdown class="profile-dropdown" />
      </div>
    </div>

    <div class="content">
      <div class="table-wrapper" :class="{ loading }">
        <table>
          <thead>
            <tr>
              <th>Club ID</th>
              <th>Name</th>
              <th>Category</th>
              <th>Description</th>
              <th class="actions-th">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="club in paginatedClubs" :key="club.id">
              <td>{{ club.id }}</td>
              <td>{{ club.name }}</td>
              <td>{{ club.category }}</td>
              <td>{{ club.description }}</td>
              <td class="actions">
                <button class="icon-btn edit" @click="handleEditClick(club)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="icon-btn view" @click="handleViewClick(club)">
                  <i class="bi bi-eye"></i>
                </button>
                <button class="icon-btn delete" @click="handleDeleteClick(club)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button class="page-btn" :disabled="currentPage === 1" @click="handlePageChange(-1)">
          <i class="bi bi-chevron-left"></i>
        </button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="handlePageChange(1)">
          <i class="bi bi-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Add Club Modal -->
    <Modal v-if="showAddModal" title="Add New Club" :show="showAddModal" @close="showAddModal = false">
      <ClubForm :categories="categoriesList" @submit="handleAddClub" @cancel="showAddModal = false" />
    </Modal>

    <!-- Edit Club Modal -->
    <Modal v-if="showEditModal" title="Edit Club" :show="showEditModal" @close="showEditModal = false">
      <ClubForm v-if="selectedClub" :club="selectedClub" :categories="categoriesList" :is-edit="true" @submit="handleEditSubmit" @cancel="showEditModal = false" />
    </Modal>

    <!-- View Club Modal -->
    <Modal v-if="showViewModal" title="Club Details" :show="showViewModal" @close="showViewModal = false">
      <div v-if="selectedClub" class="detail-section">
        <h3>Basic Information</h3>
        <div class="detail-row"><span class="label">Club ID:</span><span class="value">{{ selectedClub.id }}</span></div>
        <div class="detail-row"><span class="label">Name:</span><span class="value">{{ selectedClub.name }}</span></div>
        <div class="detail-row"><span class="label">Category:</span><span class="value">{{ selectedClub.category }}</span></div>
        <div class="detail-row"><span class="label">Description:</span><span class="value">{{ selectedClub.description }}</span></div>
        <div class="detail-row"><span class="label">Created At:</span><span class="value">{{ formatDate(selectedClub.created_at) }}</span></div>
        <div class="detail-row"><span class="label">Updated At:</span><span class="value">{{ formatDate(selectedClub.updated_at) }}</span></div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AdminProfileDropdown from '@/components/AdminProfileDropdown.vue'
import Modal from '@/components/Modal.vue'
import ClubForm from '@/components/ClubForm.vue'
import axios from 'axios'

const clubs = ref([])
const categoriesList = ref([])  // category names from backend
const searchQuery = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const totalPages = ref(1)
const loading = ref(false)

const showAddModal = ref(false)
const showEditModal = ref(false)
const showViewModal = ref(false)
const selectedClub = ref(null)

// Determine base API URL
const baseUrl = window.location.hostname === 'localhost'
  ? `http://${window.location.hostname}:8000`
  : `${window.location.protocol}//${window.location.host}`

// Fetch categories for filter and form
const fetchCategoriesList = async () => {
  try {
    const response = await axios.get(`${baseUrl}/api/categories/`, { params: { page: 1 } })
    const list = response.data.results || response.data
    categoriesList.value = list.map(c => c.name)
  } catch (error) {
    console.error('Error fetching categories list:', error)
    alert('Failed to fetch category list')
  }
}

// Fetch clubs with pagination, search, and category filter
const fetchClubs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      search: searchQuery.value || undefined,
      category: categoryFilter.value || undefined
    }
    const response = await axios.get(`${baseUrl}/api/clubs/`, { params })

    if (response.data.results) {
      clubs.value = response.data.results
      // Default page_size = itemsPerPage
      totalPages.value = Math.ceil(response.data.count / itemsPerPage)
    } else {
      clubs.value = response.data
      totalPages.value = Math.ceil(clubs.value.length / itemsPerPage)
    }
    // categoriesList is loaded separately from fetchCategoriesList
  } catch (error) {
    console.error('Error fetching clubs:', error)
    alert('Failed to fetch clubs')
  } finally {
    loading.value = false
  }
}

// Load initial data
onMounted(() => {
  fetchCategoriesList()
  fetchClubs()
})

// Watchers to refetch on filter or page change
watch([searchQuery, categoryFilter, currentPage], () => {
  fetchClubs()
})

// Computed: extract current page slice if non-paginated
const filteredClubs = computed(() => {
  const filtered = clubs.value.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          String(c.id).includes(searchQuery.value)
    const matchesCategory = !categoryFilter.value || c.category === categoryFilter.value
    return matchesSearch && matchesCategory
  })
  return filtered
})

const paginatedClubs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredClubs.value.slice(start, start + itemsPerPage)
})

// CRUD Handlers
const handleAddClub = async (formData) => {
  try {
    await axios.post(`${baseUrl}/api/clubs/`, formData)
    showAddModal.value = false
    fetchClubs()
  } catch (error) {
    console.error('Error adding club:', error)
    alert(error.response?.data?.detail || 'Failed to add club')
  }
}

const handleEditClick = (club) => {
  selectedClub.value = { ...club }
  showEditModal.value = true
}

const handleEditSubmit = async (formData) => {
  try {
    await axios.put(`${baseUrl}/api/clubs/${selectedClub.value.id}/`, formData)
    showEditModal.value = false
    selectedClub.value = null
    fetchClubs()
  } catch (error) {
    console.error('Error updating club:', error)
    alert(error.response?.data?.detail || 'Failed to update club')
  }
}

const handleViewClick = (club) => {
  selectedClub.value = club
  showViewModal.value = true
}

const handleDeleteClick = async (club) => {
  if (!confirm(`Are you sure you want to delete club ${club.name}?`)) return
  try {
    await axios.delete(`${baseUrl}/api/clubs/${club.id}/`)
    fetchClubs()
  } catch (error) {
    console.error('Error deleting club:', error)
    alert(error.response?.data?.detail || 'Failed to delete club')
  }
}

const handlePageChange = (delta) => {
  currentPage.value = Math.min(Math.max(1, currentPage.value + delta), totalPages.value)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}
</script>

<style scoped>
/* 复用 StudentManagement 的样式，只需修改类名 */
.club-management {
  min-height: 100vh;
  background: #f3f4f6;
  color: #64748b;
  padding: 2rem;
}

/* 其他样式与 StudentManagement 完全相同，只需将 .student-management 替换为 .club-management */
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
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
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

.search-box input::placeholder {
  color: #64748b;
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

.content {
  background: #2d3748;
  border-radius: 1rem;
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #4a5568;
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

.actions-th {
  text-align: right;
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

.status.pending {
  background: #78350f;
  color: #fcd34d;
}

.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.icon-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn.edit {
  background: #3730a3;
  color: #c7d2fe;
}

.icon-btn.view {
  background: #065f46;
  color: #6ee7b7;
}

.icon-btn.delete {
  background: #991b1b;
  color: #fca5a5;
}

.icon-btn:hover {
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

@media (max-width: 768px) {
  .club-management {
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

.profile-dropdown {
  margin-left: 1rem;
}
</style> 
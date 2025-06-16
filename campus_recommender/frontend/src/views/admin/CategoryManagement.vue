<template>
  <div class="category-management">
    <div class="header">
      <h1>Category Club Management</h1>
      <div class="header-actions">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Search by name or ID..."
          >
        </div>
        <select v-model="statusFilter">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <button class="add-btn" @click="showAddModal = true">
          <i class="bi bi-plus-lg"></i>
          Add Category
        </button>
        <AdminProfileDropdown class="profile-dropdown" />
      </div>
    </div>

    <div class="content">
      <div class="table-wrapper" :class="{ loading }">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th class="actions-th">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in paginatedCategories" :key="category.id">
              <td>{{ category.id }}</td>
              <td>{{ category.name }}</td>
              <td class="actions">
                <button class="icon-btn edit" @click="editCategory(category)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="icon-btn view" @click="viewCategory(category)">
                  <i class="bi bi-eye"></i>
                </button>
                <button class="icon-btn delete" @click="deleteCategory(category.id)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <i class="bi bi-chevron-left"></i>
        </button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button 
          class="page-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <i class="bi bi-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal
      v-if="showAddModal || showEditModal"
      :title="showEditModal ? 'Edit Category' : 'Add New Category'"
      :show="showAddModal || showEditModal"
      @close="closeModal"
    >
      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <label for="name">Name</label>
          <input 
            type="text" 
            id="name" 
            v-model="formData.name" 
            required
          >
        </div>
        <div class="form-group">
          <label for="description">Description</label>
          <textarea 
            id="description" 
            v-model="formData.description" 
            required
          ></textarea>
        </div>
        <div class="form-group">
          <label for="status">Status</label>
          <select id="status" v-model="formData.status" required>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
        <div class="form-actions">
          <button type="submit" class="submit-btn">
            {{ showEditModal ? 'Update' : 'Create' }}
          </button>
          <button type="button" @click="closeModal" class="cancel-btn">Cancel</button>
        </div>
      </form>
    </Modal>

    <!-- View Modal -->
    <Modal
      v-if="showViewModal"
      title="Category Details"
      :show="showViewModal"
      @close="showViewModal = false"
    >
      <div v-if="selectedCategory" class="category-details">
        <div class="detail-section">
          <h3>Basic Information</h3>
          <div class="detail-row">
            <span class="label">ID:</span>
            <span class="value">{{ selectedCategory.id }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Name:</span>
            <span class="value">{{ selectedCategory.name }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Description:</span>
            <span class="value">{{ selectedCategory.description }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Status:</span>
            <span class="value">
              <span class="status" :class="selectedCategory.status">
                {{ selectedCategory.status }}
              </span>
            </span>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AdminProfileDropdown from '@/components/AdminProfileDropdown.vue'
import Modal from '@/components/Modal.vue'
import axios from 'axios'

const categories = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const loading = ref(false)

const showAddModal = ref(false)
const showEditModal = ref(false)
const showViewModal = ref(false)
const selectedCategory = ref(null)
const formData = ref({
  name: '',
  description: '',
  status: 'active'
})

const fetchCategories = async () => {
  try {
    loading.value = true;
    const params = {
      page: currentPage.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value || undefined
    };
    
    // Get API base URL based on environment
    const baseUrl = window.location.hostname === 'localhost' ? 
      `http://${window.location.hostname}:8000` : 
      `${window.location.protocol}//${window.location.host}`;
    const apiUrl = `${baseUrl}/api/categories/`;
    
    console.log('Fetching categories from:', apiUrl);
    
    const response = await axios.get(apiUrl, { params });
    
    if (response.data.results) {
      categories.value = response.data.results.map(category => ({
        ...category,
        memberCount: category.memberCount || 0,
        activityCount: category.activityCount || 0
      }));
      
      // Update pagination from server response
      totalPages.value = response.data.total_pages || 1;
    } else {
      // Handle non-paginated response (fallback)
      categories.value = response.data;
      calculatePagination();
    }
  } catch (error) {
    console.error('Error fetching categories:', error);
    alert('Failed to fetch categories');
  } finally {
    loading.value = false;
  }
};

// Calculate pagination locally if server doesn't provide it
const calculatePagination = () => {
  totalPages.value = Math.ceil(filteredCategories.value.length / itemsPerPage);
};

// Load initial data when component mounts
onMounted(() => {
  fetchCategories();
});

const filteredCategories = computed(() => {
  return categories.value.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                           c.description.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                           String(c.id).includes(searchQuery.value)
    const matchesStatus = !statusFilter.value || c.status === statusFilter.value
    return matchesSearch && matchesStatus
  })
})

const paginatedCategories = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredCategories.value.slice(start, start + itemsPerPage)
})

const totalPages = ref(1)

watch([searchQuery, statusFilter, currentPage], () => {
  fetchCategories();
})

const handleSubmit = async () => {
  try {
    const baseUrl = window.location.hostname === 'localhost' ? 
      `http://${window.location.hostname}:8000` : 
      `${window.location.protocol}//${window.location.host}`;
      
    if (showEditModal.value) {
      await axios.put(`${baseUrl}/api/categories/${selectedCategory.value.id}/`, formData.value);
    } else {
      await axios.post(`${baseUrl}/api/categories/`, formData.value);
    }
    await fetchCategories();
    closeModal();
  } catch (error) {
    console.error('Error saving category:', error);
    alert(error.response?.data?.detail || 'Failed to save category');
  }
};

const editCategory = (category) => {
  selectedCategory.value = category
  formData.value = { ...category }
  showEditModal.value = true
}

const viewCategory = (category) => {
  selectedCategory.value = category
  showViewModal.value = true
}

const deleteCategory = async (id) => {
  if (!confirm('Are you sure you want to delete this category?')) return
  
  try {
    const baseUrl = window.location.hostname === 'localhost' ? 
      `http://${window.location.hostname}:8000` : 
      `${window.location.protocol}//${window.location.host}`;
    
    await axios.delete(`${baseUrl}/api/categories/${id}/`);
    await fetchCategories();
  } catch (error) {
    console.error('Error deleting category:', error);
    alert(error.response?.data?.detail || 'Failed to delete category');
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  showViewModal.value = false
  selectedCategory.value = null
  formData.value = { name: '', description: '', status: 'active' }
}

const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Date(date).toLocaleDateString();
}
</script>

<style scoped>
.category-management {
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
  .category-management {
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

.loading {
  opacity: 0.6;
  pointer-events: none;
}

.category-details {
  padding: 1rem;
}

.detail-row {
  display: flex;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  width: 120px;
  font-weight: 500;
  color: #64748b;
}

.detail-row .value {
  flex: 1;
  color: #1f2937;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #1e293b;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #cbd5e0;
  border-radius: 0.375rem;
  background-color: white;
  color: #1e293b;
}

.form-group textarea {
  height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.submit-btn {
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 0.375rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  background-color: #4338ca;
}

.cancel-btn {
  background-color: #9ca3af;
  color: white;
  border: none;
  border-radius: 0.375rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background-color: #6b7280;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}
</style> 
<template>
  <div class="student-management">
    <div class="header">
      <h1>Student Management</h1>
      <div class="header-actions">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Search by name or ID..."
          >
        </div>
        <select v-model="courseFilter">
          <option value="">All Courses</option>
          <option v-for="course in courses" :key="course" :value="course">
            {{ course }}
          </option>
        </select>
        <button class="add-btn" @click="showAddModal = true">
          <i class="bi bi-plus-lg"></i>
          Add Student
        </button>
        <AdminProfileDropdown class="profile-dropdown" />
      </div>
    </div>

    <div class="content">
      <div class="table-wrapper" :class="{ loading }">
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
          <div>Loading students...</div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Student ID</th>
              <th>Name</th>
              <th>Course</th>
              <th>Joined Date</th>
              <th>Email</th>
              <th>Status</th>
              <th class="actions-th">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.id">
              <td>{{ student.student_id }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.course }}</td>
              <td>{{ student.joinedDate }}</td>
              <td>{{ student.email }}</td>
              <td>
                <span class="status" :class="student.status">
                  {{ student.status }}
                </span>
              </td>
              <td class="actions">
                <button class="icon-btn edit" @click="handleEditClick(student)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="icon-btn view" @click="handleViewClick(student)">
                  <i class="bi bi-eye"></i>
                </button>
                <button class="icon-btn delete" @click="handleDeleteClick(student)">
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

    <!-- Add Student Modal -->
    <Modal
      v-if="showAddModal"
      title="Add New Student"
      :show="showAddModal"
      @close="showAddModal = false"
    >
      <StudentForm
        :courses="courses"
        @submit="handleAddStudent"
        @cancel="showAddModal = false"
      />
    </Modal>

    <!-- Edit Student Modal -->
    <Modal
      v-if="showEditModal"
      title="Edit Student"
      :show="showEditModal"
      @close="showEditModal = false"
    >
      <StudentForm
        v-if="selectedStudent"
        :student="selectedStudent"
        :courses="courses"
        :is-edit="true"
        @submit="handleEditSubmit"
        @cancel="showEditModal = false"
      />
    </Modal>

    <!-- View Student Modal -->
    <Modal
      v-if="showViewModal"
      title="Student Details"
      :show="showViewModal"
      @close="showViewModal = false"
    >
      <div v-if="selectedStudent" class="student-details">
        <div class="detail-section">
          <h3>Basic Information</h3>
          <div class="detail-row">
            <span class="label">Student ID:</span>
            <span class="value">{{ selectedStudent.student_id }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Name:</span>
            <span class="value">{{ selectedStudent.name }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Gender:</span>
            <span class="value">{{ selectedStudent.gender }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Email:</span>
            <span class="value">{{ selectedStudent.email }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Course:</span>
            <span class="value">{{ selectedStudent.course }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Joined Date:</span>
            <span class="value">{{ selectedStudent.joinedDate }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Status:</span>
            <span class="value">
              <span class="status" :class="selectedStudent.status">
                {{ selectedStudent.status }}
              </span>
            </span>
          </div>
        </div>

        <div class="detail-section">
          <h3>Personal Information</h3>
          <div class="detail-row">
            <span class="label">Hobbies:</span>
            <span class="value">
              <div class="tags">
                <span v-for="hobby in selectedStudent.hobbies" :key="hobby" class="tag">
                  {{ hobby }}
                </span>
                <span v-if="!selectedStudent.hobbies?.length" class="no-data">No hobbies listed</span>
              </div>
            </span>
          </div>
          <div class="detail-row">
            <span class="label">Interests:</span>
            <span class="value">
              <div class="tags">
                <span v-for="interest in selectedStudent.interests" :key="interest" class="tag">
                  {{ interest }}
                </span>
                <span v-if="!selectedStudent.interests?.length" class="no-data">No interests listed</span>
              </div>
            </span>
          </div>
          <div class="detail-row">
            <span class="label">Skills:</span>
            <span class="value">
              <div class="tags">
                <span v-for="skill in selectedStudent.skills" :key="skill" class="tag">
                  {{ skill }}
                </span>
                <span v-if="!selectedStudent.skills?.length" class="no-data">No skills listed</span>
              </div>
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
import StudentForm from '@/components/StudentForm.vue'
import axios from 'axios'

const students = ref([])
const courses = ref([])
const searchQuery = ref('')
const courseFilter = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const itemsPerPage = 10
const loading = ref(false)

// Modal states
const showAddModal = ref(false)
const showEditModal = ref(false)
const showViewModal = ref(false)
const selectedStudent = ref(null)

// Fetch students from API
const fetchStudents = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      search: searchQuery.value || undefined,
      course: courseFilter.value || undefined
    }
    
    // Get the API base URL from the current window location
    const baseUrl = window.location.hostname === 'localhost' ? 
      `http://${window.location.hostname}:8000` : 
      `${window.location.protocol}//${window.location.host}`;
    const apiUrl = `${baseUrl}/api/students/`;
    
    console.log('Fetching students from:', apiUrl);
    
    const response = await axios.get(apiUrl, { params })
    if (response.data.results) {
      students.value = response.data.results.map(student => ({
        id: student.id,
        student_id: student.student_id,
        name: student.user.username,
        gender: student.gender || '',
        course: student.course || 'N/A',
        joinedDate: new Date(student.user.date_joined).toLocaleDateString(),
        email: student.user.email,
        status: student.status || 'active',
        hobbies: student.hobbies || [],
        interests: student.interests || [],
        skills: student.skills || []
      }))
      
      // Update pagination
      totalPages.value = Math.ceil(response.data.count / itemsPerPage)
      
      // Update courses list
      if (response.data.courses) {
        courses.value = response.data.courses.filter(Boolean)
      }
    }
  } catch (error) {
    console.error('Error fetching students:', error)
    alert(error.response?.data?.error || 'Failed to fetch students')
  } finally {
    loading.value = false
  }
}

// Add new student
const handleAddStudent = async (formData) => {
  try {
    // Create a proper user object
    const userData = {
      username: formData.username,
      email: formData.email,
      password: formData.password
    }

    // Prepare the student data with user as a separate field
    const studentData = {
      student_id: formData.student_id,
      gender: formData.gender,
      course: formData.course,
      status: formData.status,
      hobbies: formData.hobbies,
      interests: formData.interests,
      skills: formData.skills,
      user: userData  // Ensure user is an object, not an ID
    }
    
    console.log('Sending student data:', JSON.stringify(studentData))
    
    // Get the API base URL from the current window location
    const baseUrl = window.location.hostname === 'localhost' ? 
      `http://${window.location.hostname}:8000` : 
      `${window.location.protocol}//${window.location.host}`;
    const apiUrl = `${baseUrl}/api/students/`;
    
    console.log('API URL:', apiUrl);
    
    // Make the request with the properly structured data
    const response = await axios.post(apiUrl, studentData)
    
    showAddModal.value = false
    await fetchStudents()
  } catch (error) {
    console.error('Error adding student:', error)
    console.error('Response data:', error.response?.data)
    
    if (error.response?.data) {
      const errors = error.response.data
      let errorMessage = 'Failed to add student:\n'
      Object.keys(errors).forEach(key => {
        if (typeof errors[key] === 'object' && errors[key].length) {
          errorMessage += `${key}: ${errors[key][0]}\n`
        } else if (typeof errors[key] === 'object' && errors[key].non_field_errors) {
          errorMessage += `${key}: ${errors[key].non_field_errors[0]}\n`
        } else {
          errorMessage += `${key}: ${JSON.stringify(errors[key])}\n`
        }
      })
      alert(errorMessage)
    } else {
      alert('Failed to add student')
    }
  }
}

// Edit student
const handleEditClick = (student) => {
  selectedStudent.value = student
  showEditModal.value = true
}

const handleEditSubmit = async (formData) => {
  try {
    // Create a proper user object with just the email
    const userData = {
      email: formData.email
    }

    // Prepare the student data with user as a separate field
    const studentData = {
      course: formData.course,
      gender: formData.gender,
      status: formData.status,
      hobbies: formData.hobbies,
      interests: formData.interests,
      skills: formData.skills,
      user: userData  // Ensure user is an object, not an ID
    }
    
    console.log('Updating student data:', JSON.stringify(studentData))
    
    // Get the API base URL from the current window location
    const baseUrl = window.location.hostname === 'localhost' ? 
      `http://${window.location.hostname}:8000` : 
      `${window.location.protocol}//${window.location.host}`;
    const apiUrl = `${baseUrl}/api/students/${selectedStudent.value.id}/`;
    
    console.log('API URL:', apiUrl);
    
    // Make the request with the properly structured data
    await axios.patch(apiUrl, studentData)
    
    showEditModal.value = false
    selectedStudent.value = null
    await fetchStudents()
  } catch (error) {
    console.error('Error updating student:', error)
    console.error('Response data:', error.response?.data)
    
    if (error.response?.data) {
      const errors = error.response.data
      let errorMessage = 'Failed to update student:\n'
      Object.keys(errors).forEach(key => {
        if (typeof errors[key] === 'object' && errors[key].length) {
          errorMessage += `${key}: ${errors[key][0]}\n`
        } else if (typeof errors[key] === 'object' && errors[key].non_field_errors) {
          errorMessage += `${key}: ${errors[key].non_field_errors[0]}\n`
        } else {
          errorMessage += `${key}: ${JSON.stringify(errors[key])}\n`
        }
      })
      alert(errorMessage)
    } else {
      alert('Failed to update student')
    }
  }
}

// Delete student
const handleDeleteClick = async (student) => {
  if (confirm(`Are you sure you want to delete student ${student.name}?`)) {
    try {
      // Get the API base URL from the current window location
      const baseUrl = window.location.hostname === 'localhost' ? 
        `http://${window.location.hostname}:8000` : 
        `${window.location.protocol}//${window.location.host}`;
      const apiUrl = `${baseUrl}/api/students/${student.id}/`;
      
      console.log('Deleting student from:', apiUrl);
      
      await axios.delete(apiUrl)
      await fetchStudents()
    } catch (error) {
      console.error('Error deleting student:', error)
      alert(error.response?.data?.error || 'Failed to delete student')
    }
  }
}

// View student details
const handleViewClick = (student) => {
  selectedStudent.value = student
  showViewModal.value = true
}

// Watch for changes that should trigger a refresh
watch([searchQuery, courseFilter, currentPage], () => {
  fetchStudents()
})

// Load initial data
onMounted(() => {
  fetchStudents()
})
</script>

<style scoped>
.student-management {
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
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(45, 55, 72, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: #e2e8f0;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #4a5568;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
  .student-management {
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

.table-wrapper {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
}

.student-details {
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

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: #e2e8f0;
  color: #475569;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.no-data {
  color: #94a3b8;
  font-style: italic;
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
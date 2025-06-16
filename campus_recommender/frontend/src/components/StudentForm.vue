<template>
  <form @submit.prevent="handleSubmit" class="student-form">
    <div class="form-group">
      <label>Student ID</label>
      <input 
        v-model="formData.student_id"
        type="text"
        required
        :disabled="props.isEdit"
        placeholder="Enter student ID"
        :class="{ 'error': errors.student_id }"
      >
      <span v-if="errors.student_id" class="error-message">{{ errors.student_id }}</span>
    </div>

    <div class="form-group">
      <label>Username</label>
      <input 
        v-model="formData.username"
        type="text"
        required
        :disabled="props.isEdit"
        placeholder="Enter username"
        :class="{ 'error': errors.username }"
      >
      <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
    </div>

    <div class="form-group">
      <label>Email</label>
      <input 
        v-model="formData.email"
        type="email"
        required
        placeholder="Enter email"
        :class="{ 'error': errors.email }"
      >
      <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
    </div>

    <div class="form-group">
      <label>Course</label>
      <select 
        v-model="formData.course" 
        required
        :class="{ 'error': errors.course }"
      >
        <option value="">Select Course</option>
        <option v-for="course in courses" :key="course" :value="course">
          {{ course }}
        </option>
      </select>
      <span v-if="errors.course" class="error-message">{{ errors.course }}</span>
    </div>

    <div class="form-group">
      <label>Gender</label>
      <select v-model="formData.gender" required :class="{ 'error': errors.gender }">
        <option value="">Select Gender</option>
        <option value="Male">Male</option>
        <option value="Female">Female</option>
        <option value="Other">Other</option>
      </select>
      <span v-if="errors.gender" class="error-message">{{ errors.gender }}</span>
    </div>

    <div class="form-group">
      <label>Hobbies</label>
      <div class="tags-input">
        <div class="tags">
          <span v-for="(hobby, index) in formData.hobbies" :key="index" class="tag">
            {{ hobby }}
            <button type="button" @click="removeHobby(index)" class="remove-tag">&times;</button>
          </span>
        </div>
        <div class="input-with-dropdown">
          <input 
            type="text"
            v-model="newHobby"
            @keydown.enter.prevent="addHobby"
            @focus="showHobbyDropdown = true"
            @blur="handleDropdownBlur('hobby')"
            placeholder="Add hobby and press Enter"
          >
          <div v-if="showHobbyDropdown" class="dropdown">
            <div 
              v-for="hobby in filteredHobbyOptions" 
              :key="hobby"
              class="dropdown-item"
              @mousedown="selectHobby(hobby)"
            >
              {{ hobby }}
            </div>
            <div v-if="newHobby && !hobbyOptions.includes(newHobby)" class="dropdown-item custom">
              Add "{{ newHobby }}"
            </div>
          </div>
        </div>
      </div>
      <span v-if="errors.hobbies" class="error-message">{{ errors.hobbies }}</span>
    </div>

    <div class="form-group">
      <label>Interests</label>
      <div class="tags-input">
        <div class="tags">
          <span v-for="(interest, index) in formData.interests" :key="index" class="tag">
            {{ interest }}
            <button type="button" @click="removeInterest(index)" class="remove-tag">&times;</button>
          </span>
        </div>
        <div class="input-with-dropdown">
          <input 
            type="text"
            v-model="newInterest"
            @keydown.enter.prevent="addInterest"
            @focus="showInterestDropdown = true"
            @blur="handleDropdownBlur('interest')"
            placeholder="Add interest and press Enter"
          >
          <div v-if="showInterestDropdown" class="dropdown">
            <div 
              v-for="interest in filteredInterestOptions" 
              :key="interest"
              class="dropdown-item"
              @mousedown="selectInterest(interest)"
            >
              {{ interest }}
            </div>
            <div v-if="newInterest && !interestOptions.includes(newInterest)" class="dropdown-item custom">
              Add "{{ newInterest }}"
            </div>
          </div>
        </div>
      </div>
      <span v-if="errors.interests" class="error-message">{{ errors.interests }}</span>
    </div>

    <div class="form-group">
      <label>Skills</label>
      <div class="tags-input">
        <div class="tags">
          <span v-for="(skill, index) in formData.skills" :key="index" class="tag">
            {{ skill }}
            <button type="button" @click="removeSkill(index)" class="remove-tag">&times;</button>
          </span>
        </div>
        <div class="input-with-dropdown">
          <input 
            type="text"
            v-model="newSkill"
            @keydown.enter.prevent="addSkill"
            @focus="showSkillDropdown = true"
            @blur="handleDropdownBlur('skill')"
            placeholder="Add skill and press Enter"
          >
          <div v-if="showSkillDropdown" class="dropdown">
            <div 
              v-for="skill in filteredSkillOptions" 
              :key="skill"
              class="dropdown-item"
              @mousedown="selectSkill(skill)"
            >
              {{ skill }}
            </div>
            <div v-if="newSkill && !skillOptions.includes(newSkill)" class="dropdown-item custom">
              Add "{{ newSkill }}"
            </div>
          </div>
        </div>
      </div>
      <span v-if="errors.skills" class="error-message">{{ errors.skills }}</span>
    </div>

    <div class="form-group">
      <label>Status</label>
      <select v-model="formData.status" required>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
        <option value="pending">Pending</option>
      </select>
    </div>

    <div v-if="!props.isEdit" class="form-group">
      <label>Password</label>
      <input 
        v-model="formData.password"
        type="password"
        required
        placeholder="Enter password"
        :class="{ 'error': errors.password }"
      >
      <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
    </div>

    <div class="form-actions">
      <button type="button" class="cancel-btn" @click="$emit('cancel')">
        Cancel
      </button>
      <button type="submit" class="submit-btn" :disabled="loading">
        {{ loading ? 'Saving...' : (props.isEdit ? 'Update' : 'Create') }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, defineProps, defineEmits, onMounted, computed } from 'vue'

const props = defineProps({
  student: {
    type: Object,
    default: () => ({})
  },
  courses: {
    type: Array,
    default: () => []
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])
const loading = ref(false)

const formData = ref({
  student_id: '',
  username: '',
  email: '',
  course: '',
  status: 'active',
  password: '',
  gender: '',
  hobbies: [],
  interests: [],
  skills: []
})

const newHobby = ref('')
const newInterest = ref('')
const newSkill = ref('')
const errors = ref({})

const hobbyOptions = [
  'Reading', 'Writing', 'Drawing', 'Painting', 'Photography', 'Music',
  'Dancing', 'Singing', 'Sports', 'Gaming', 'Cooking', 'Gardening',
  'Hiking', 'Swimming', 'Cycling', 'Yoga', 'Meditation', 'Chess',
  'Programming', 'Crafting', 'Fishing', 'Traveling', 'Collecting'
]

const interestOptions = [
  'Technology', 'Science', 'Art', 'History', 'Literature', 'Philosophy',
  'Psychology', 'Economics', 'Politics', 'Environment', 'Health',
  'Education', 'Business', 'Marketing', 'Design', 'Architecture',
  'Engineering', 'Mathematics', 'Languages', 'Culture', 'Fashion'
]

const skillOptions = [
  'Programming', 'Web Development', 'Mobile Development', 'Data Analysis',
  'Machine Learning', 'UI/UX Design', 'Graphic Design', 'Project Management',
  'Public Speaking', 'Writing', 'Research', 'Problem Solving',
  'Team Leadership', 'Communication', 'Time Management', 'Critical Thinking',
  'Creativity', 'Adaptability', 'Collaboration', 'Technical Writing'
]

const showHobbyDropdown = ref(false)
const showInterestDropdown = ref(false)
const showSkillDropdown = ref(false)

const filteredHobbyOptions = computed(() => {
  return hobbyOptions.filter(hobby => 
    hobby.toLowerCase().includes(newHobby.value.toLowerCase()) &&
    !formData.value.hobbies.includes(hobby)
  )
})

const filteredInterestOptions = computed(() => {
  return interestOptions.filter(interest => 
    interest.toLowerCase().includes(newInterest.value.toLowerCase()) &&
    !formData.value.interests.includes(interest)
  )
})

const filteredSkillOptions = computed(() => {
  return skillOptions.filter(skill => 
    skill.toLowerCase().includes(newSkill.value.toLowerCase()) &&
    !formData.value.skills.includes(skill)
  )
})

const selectHobby = (hobby) => {
  formData.value.hobbies.push(hobby)
  newHobby.value = ''
  showHobbyDropdown.value = false
}

const selectInterest = (interest) => {
  formData.value.interests.push(interest)
  newInterest.value = ''
  showInterestDropdown.value = false
}

const selectSkill = (skill) => {
  formData.value.skills.push(skill)
  newSkill.value = ''
  showSkillDropdown.value = false
}

const addHobby = () => {
  if (newHobby.value.trim() && !formData.value.hobbies.includes(newHobby.value.trim())) {
    formData.value.hobbies.push(newHobby.value.trim())
    newHobby.value = ''
  }
}

const addInterest = () => {
  if (newInterest.value.trim() && !formData.value.interests.includes(newInterest.value.trim())) {
    formData.value.interests.push(newInterest.value.trim())
    newInterest.value = ''
  }
}

const addSkill = () => {
  if (newSkill.value.trim() && !formData.value.skills.includes(newSkill.value.trim())) {
    formData.value.skills.push(newSkill.value.trim())
    newSkill.value = ''
  }
}

const removeHobby = (index) => {
  formData.value.hobbies.splice(index, 1)
}

const removeInterest = (index) => {
  formData.value.interests.splice(index, 1)
}

const removeSkill = (index) => {
  formData.value.skills.splice(index, 1)
}

const validateForm = () => {
  errors.value = {}
  
  if (!formData.value.student_id) {
    errors.value.student_id = 'Student ID is required'
  }
  
  if (!formData.value.username) {
    errors.value.username = 'Username is required'
  }
  
  if (!formData.value.email) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.value.email)) {
    errors.value.email = 'Invalid email format'
  }
  
  if (!formData.value.course) {
    errors.value.course = 'Course is required'
  }

  if (!formData.value.gender) {
    errors.value.gender = 'Gender is required'
  }

  if (formData.value.hobbies.length === 0) {
    errors.value.hobbies = 'At least one hobby is required'
  }

  if (formData.value.interests.length === 0) {
    errors.value.interests = 'At least one interest is required'
  }

  if (formData.value.skills.length === 0) {
    errors.value.skills = 'At least one skill is required'
  }
  
  if (!props.isEdit && !formData.value.password) {
    errors.value.password = 'Password is required'
  } else if (!props.isEdit && formData.value.password.length < 8) {
    errors.value.password = 'Password must be at least 8 characters long'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleDropdownBlur = (type) => {
  window.setTimeout(() => {
    switch(type) {
      case 'hobby':
        showHobbyDropdown.value = false
        break
      case 'interest':
        showInterestDropdown.value = false
        break
      case 'skill':
        showSkillDropdown.value = false
        break
    }
  }, 200)
}

onMounted(() => {
  if (props.student) {
    formData.value = {
      ...formData.value,
      ...props.student,
      username: props.student.name,
      hobbies: props.student.hobbies || [],
      interests: props.student.interests || [],
      skills: props.student.skills || []
    }
  }
})

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }
  
  loading.value = true
  try {
    emit('submit', formData.value)
  } catch (error) {
    console.error('Form submission error:', error)
    if (error.response?.data?.error) {
      alert(error.response.data.error)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.student-form {
  padding: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #64748b;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  background: white;
  color: #1f2937;
}

.form-group input:disabled {
  background: #f1f5f9;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.cancel-btn {
  background: #e2e8f0;
  color: #475569;
  border: none;
}

.submit-btn {
  background: #4f46e5;
  color: white;
  border: none;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error {
  border-color: #ef4444 !important;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.tags-input {
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  padding: 0.5rem;
  background: white;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.tag {
  background: #e2e8f0;
  color: #475569;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.remove-tag {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  font-size: 1.25rem;
  line-height: 1;
}

.remove-tag:hover {
  color: #ef4444;
}

.input-with-dropdown {
  position: relative;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  margin-top: 0.25rem;
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.dropdown-item {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f1f5f9;
}

.dropdown-item.custom {
  color: #4f46e5;
  font-style: italic;
}

.tags-input input {
  width: 100%;
  border: none;
  outline: none;
  padding: 0.25rem;
}

.tags-input input::placeholder {
  color: #94a3b8;
}
</style> 
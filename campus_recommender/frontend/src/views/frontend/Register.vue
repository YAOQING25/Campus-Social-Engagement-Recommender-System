<template>
  <div class="register-container">
    <div class="register-box">
      <h2>CSE</h2>
      <form @submit.prevent="handleRegister">
        
        <div class="form-group">
          <label>Name</label>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="Choose a username"
            required
          >
        </div>

        <div class="form-group">
          <label>Student ID</label>
          <input 
            v-model="form.studentId" 
            type="text" 
            placeholder="Enter your student ID"
            required
          >
        </div>

        <div class="form-group">
          <label>E-mail</label>
          <input 
            v-model="form.email" 
            type="text" 
            placeholder="Enter your E-mail"
            required
          >
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Gender</label>
            <select v-model="form.gender" required>
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>

          <div class="form-group">
            <label>Course</label>
            <select v-model="form.course" required>
              <option value="">Select course</option>
              <option value="cs">Computer Science</option>
              <option value="business">Business</option>
              <option value="engineering">Engineering</option>
              <option value="arts">Arts</option>
            </select>
          </div>
        </div>

        <!-- Hobbies -->
        <div class="form-group">
          <label>What are your hobbies?</label>
          <div class="checkbox-group">
            <label v-for="hobby in hobbies" :key="hobby" class="checkbox-option">
              <input type="checkbox" v-model="form.hobbies" :value="hobby">
              <span>{{ hobby }}</span>
            </label>
          </div>
        </div>

        <!-- Academic Interests -->
        <div class="form-group">
          <label>What are your academic interests?</label>
          <div class="checkbox-group">
            <label v-for="interest in academicInterests" :key="interest" class="checkbox-option">
              <input type="checkbox" v-model="form.academicInterests" :value="interest">
              <span>{{ interest }}</span>
            </label>
          </div>
        </div>

        <!-- Extracurricular Activities -->
        <div class="form-group">
          <label>What extracurricular activities are you interested in?</label>
          <div class="checkbox-group">
            <label v-for="activity in extracurricularActivities" :key="activity" class="checkbox-option">
              <input type="checkbox" v-model="form.extracurricularActivities" :value="activity">
              <span>{{ activity }}</span>
            </label>
          </div>
        </div>

        <!-- Clubs or Organizations -->
        <div class="form-group">
          <label>Have you been involved in any clubs or organizations before?</label>
          <div class="radio-group">
            <label class="radio-option">
              <input type="radio" v-model="form.involvedInClubs" value="yes">
              <span>Yes</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="form.involvedInClubs" value="no">
              <span>No</span>
            </label>
          </div>
        </div>

        <!-- If yes, which ones? -->
        <div class="form-group" v-if="form.involvedInClubs === 'yes'">
          <label>If yes, which ones?</label>
          <input 
            v-model="form.clubsList" 
            type="text" 
            placeholder="Enter club names"
          >
        </div>

        <!-- Specific Skills -->
        <div class="form-group">
          <label>Do you have any specific skills?</label>
          <div class="checkbox-group">
            <label v-for="skill in skills" :key="skill" class="checkbox-option">
              <input type="checkbox" v-model="form.skills" :value="skill">
              <span>{{ skill }}</span>
            </label>
          </div>
        </div>

        <!-- Content Preferences -->
        <div class="form-group">
          <label>What type of content do you enjoy?</label>
          <div class="checkbox-group">
            <label v-for="content in contentTypes" :key="content" class="checkbox-option">
              <input type="checkbox" v-model="form.contentTypes" :value="content">
              <span>{{ content }}</span>
            </label>
          </div>
        </div>

        <!-- Activity Participation Frequency -->
        <div class="form-group">
          <label>How often do you like to participate in activities?</label>
          <select v-model="form.activityFrequency" required>
            <option value="">Select frequency</option>
            <option value="weekly">Weekly</option>
            <option value="bi-weekly">Bi-weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>

        <div class="form-group">
          <label>Password</label>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="Enter password"
            required
          >
        </div>

        <div class="form-group">
          <label>Confirm Password</label>
          <input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="Confirm password"
            required
          >
        </div>

        <button type="submit" class="submit-btn">Create Account</button>
        <div class="login-link">
          Already have an account? <router-link to="/login">Sign in</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// Define options for checkboxes and dropdowns
const hobbies = ref(['Sports', 'Technology', 'Arts', 'Science', 'Gaming', 'Music', 'Reading', 'Writing', 'Cooking', 'Travel'])
const academicInterests = ref(['AI', 'Data Science', 'Mathematics', 'Biology', 'Literature', 'History', 'Engineering', 'Physics'])
const extracurricularActivities = ref(['Debate', 'Drama', 'Robotics', 'Music Band', 'Sports Teams', 'Volunteering', 'Photography'])
const skills = ref(['Programming', 'Public Speaking', 'Writing', 'Design', 'Leadership', 'Event Planning'])
const contentTypes = ref(['Articles', 'Videos', 'Events', 'Tutorials', 'Podcasts'])

const form = reactive({

  username: '',
  studentId: '',
  email: '',
  gender: '',
  course: '',
  hobbies: [],
  academicInterests: [],
  extracurricularActivities: [],
  involvedInClubs: '',
  clubsList: '',
  skills: [],
  contentTypes: [],
  activityFrequency: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  if (form.password !== form.confirmPassword) {
    alert('Passwords do not match!')
    return
  }
  
  // Convert gender value to proper case to match backend choices (Male, Female, Other)
  let genderValue = 'Other';
  if (form.gender === 'male') {
    genderValue = 'Male';
  } else if (form.gender === 'female') {
    genderValue = 'Female';
  }
  
  // Split name into first and last name


  
  // Make sure all arrays are initialized as empty arrays
  const formData = {
    user: {
      username: form.username,
      email: form.email,
      password: form.password
    },
    student_id: form.studentId,
    gender: genderValue,
    course: form.course || '',
    hobbies: Array.isArray(form.hobbies) ? form.hobbies : [],
    interests: Array.isArray(form.academicInterests) ? form.academicInterests : [],
    skills: Array.isArray(form.skills) ? form.skills : []
  };
  
  try {
    console.log('Sending registration data:', formData);

    // Clear any existing user data before registration
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('isAdmin')
    localStorage.removeItem('appliedClubs')
    localStorage.removeItem('favoritedClubs')
    localStorage.removeItem('likedClubs')
    delete axios.defaults.headers.common['Authorization']

    // Use the new students registration endpoint
    const response = await axios.post('/api/students/register/', formData);
    console.log('Registration response:', response.data);
    // Save token and user data
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('user', JSON.stringify({
      id: response.data.user_id,
      student_id: response.data.student_id,
      email: response.data.email,
      full_name: response.data.full_name
    }));
    axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`;
    // Redirect to home
    router.push('/home');
  } catch (error) {
    console.error('Registration error:', error);
    
    if (error.response?.data) {
      // Handle validation errors
      const errors = error.response.data;
      let errorMessage = 'Registration failed:\n';
      
      // Format error messages for display
      Object.keys(errors).forEach(key => {
        if (Array.isArray(errors[key])) {
          errorMessage += `${key}: ${errors[key].join(', ')}\n`;
        } else if (typeof errors[key] === 'object') {
          Object.keys(errors[key]).forEach(subKey => {
            errorMessage += `${key}.${subKey}: ${errors[key][subKey].join(', ')}\n`;
          });
        }
      });
      
      alert(errorMessage);
    } else {
      alert('Registration failed. Please try again.');
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  margin: 0;
  position: absolute;
  left: 0;
  top: 0;
}

.register-box {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #1a237e;
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.9rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #667eea;
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.checkbox-group,
.radio-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
}

.checkbox-option,
.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.checkbox-option:hover,
.radio-option:hover {
  background: rgba(102, 126, 234, 0.1);
}

.checkbox-option input[type="checkbox"],
.radio-option input[type="radio"] {
  width: 16px;
  height: 16px;
  accent-color: #667eea;
}

.submit-btn {
  width: 100%;
  padding: 0.875rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 1rem;
}

.submit-btn:hover {
  background: #5468e7;
  transform: translateY(-1px);
}

.login-link {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
  font-size: 0.9rem;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .register-container {
    padding: 1rem;
  }
  
  .register-box {
    padding: 1.5rem;
  }
  
  .form-row,
  .checkbox-group,
  .radio-group {
    grid-template-columns: 1fr;
  }
}
</style>
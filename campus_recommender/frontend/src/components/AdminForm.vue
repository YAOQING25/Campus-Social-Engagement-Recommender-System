<template>
  <form @submit.prevent="handleSubmit" class="admin-form">
    <div class="form-group" v-if="!isEdit">
      <label for="username">Username</label>
      <input id="username" v-model="form.username" required />
    </div>
    <div class="form-group" v-if="!isEdit">
      <label for="password">Password</label>
      <input id="password" type="password" v-model="form.password" required />
    </div>
    <div class="form-group">
      <label for="email">Email</label>
      <input id="email" type="email" v-model="form.email" required />
    </div>
    <div class="form-group">
      <label for="firstName">First Name</label>
      <input id="firstName" v-model="form.first_name" />
    </div>
    <div class="form-group">
      <label for="lastName">Last Name</label>
      <input id="lastName" v-model="form.last_name" />
    </div>
    <div class="form-group">
      <label for="role">Role</label>
      <select id="role" v-model="form.role" required>
        <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
      </select>
    </div>
    <div class="form-group" v-if="isEdit">
      <label for="status">Status</label>
      <select id="status" v-model="form.status" required>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>
    <div class="form-actions">
      <button type="submit" class="submit-btn">{{ isEdit ? 'Update' : 'Create' }}</button>
      <button type="button" class="cancel-btn" @click="$emit('cancel')">Cancel</button>
    </div>
  </form>
</template>

<script setup>
import { reactive, toRefs, watch } from 'vue'

const props = defineProps({
  admin: { type: Object, default: () => ({}) },
  isEdit: { type: Boolean, default: false },
  roles: { type: Array, default: () => ['super', 'manager', 'staff'] }
})

const emits = defineEmits(['submit', 'cancel'])

// Create reactive form data based on props and handle reactivity to admin changes
const { admin, isEdit } = toRefs(props)

const form = reactive({
  username: '',
  password: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'staff',
  status: 'active'
})

// Watch for changes to the admin prop and update form data
watch(admin, (newAdmin) => {
  if (newAdmin) {
    // Only set these values if they exist in the newAdmin object
    if (newAdmin.username) form.username = newAdmin.username
    if (newAdmin.email) form.email = newAdmin.email
    if (newAdmin.first_name) form.first_name = newAdmin.first_name
    if (newAdmin.last_name) form.last_name = newAdmin.last_name
    if (newAdmin.role) form.role = newAdmin.role
    if (newAdmin.status) form.status = newAdmin.status
  }
}, { immediate: true })

function handleSubmit() {
  const payload = { ...form }
  
  // For edit mode, we don't need to send password if it's empty
  if (isEdit.value && !payload.password.trim()) {
    delete payload.password
  }
  
  // Make sure we're not sending empty fields
  Object.keys(payload).forEach(key => {
    if (payload[key] === '' || payload[key] === undefined) {
      delete payload[key]
    }
  })
  
  emits('submit', payload)
}
</script>

<style scoped>
.admin-form {
  padding: 1rem;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}
.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
.submit-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}
.submit-btn {
  background: #4f46e5;
  color: white;
}
.cancel-btn {
  background: #ccc;
  color: #333;
}
</style> 
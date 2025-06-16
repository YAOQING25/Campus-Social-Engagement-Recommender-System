<template>
  <form @submit.prevent="handleSubmit" class="club-form">
    <div class="form-group">
      <label>Name</label>
      <input
        v-model="formData.name"
        type="text"
        required
        placeholder="Enter club name"
      />
    </div>
    <div class="form-group">
      <label>Category</label>
      <select v-model="formData.category" required>
        <option value="">Select Category</option>
        <option v-for="cat in categories" :key="cat" :value="cat">
          {{ cat }}
        </option>
      </select>
    </div>
    <div class="form-group">
      <label>Description</label>
      <textarea
        v-model="formData.description"
        required
        placeholder="Enter description"
      ></textarea>
    </div>
    <div class="form-actions">
      <button type="button" class="cancel-btn" @click="$emit('cancel')">
        Cancel
      </button>
      <button type="submit" class="submit-btn">
        {{ props.isEdit ? 'Update' : 'Create' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, defineProps, defineEmits, onMounted } from 'vue'

const props = defineProps({
  club: {
    type: Object,
    default: () => ({})
  },
  categories: {
    type: Array,
    default: () => []
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formData = ref({
  name: '',
  category: '',
  description: ''
})

onMounted(() => {
  if (props.isEdit && props.club) {
    formData.value = {
      name: props.club.name || '',
      category: props.club.category || '',
      description: props.club.description || ''
    }
  }
})

const handleSubmit = () => {
  emit('submit', formData.value)
}
</script>

<style scoped>
.club-form {
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
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  background: white;
  color: #1f2937;
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
</style> 
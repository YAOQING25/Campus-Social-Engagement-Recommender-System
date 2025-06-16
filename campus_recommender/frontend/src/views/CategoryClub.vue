<template>
  <div class="category-club">
    <h1 class="page-title">Category Club</h1>
    
    <div class="categories-container">
      <div v-for="category in categories" :key="category.id" class="category-card">
        <h2>{{ category.name }}</h2>
        <p>{{ category.description }}</p>
        <div class="category-stats">
          <span>Members: {{ category.memberCount }}</span>
          <span>Activities: {{ category.activityCount }}</span>
        </div>
        <button @click="joinCategory(category.id)" 
                :class="{ 'joined': category.isJoined }"
                class="join-btn">
          {{ category.isJoined ? 'Joined' : 'Join Club' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'CategoryClub',
  setup() {
    const categories = ref([])

    const fetchCategories = async () => {
      try {
        const response = await axios.get('/api/categories/')
        categories.value = response.data
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }

    const joinCategory = async (categoryId) => {
      try {
        const response = await axios.post(`/api/categories/${categoryId}/join/`)
        const updatedCategory = response.data
        const index = categories.value.findIndex(c => c.id === categoryId)
        if (index !== -1) {
          categories.value[index] = updatedCategory
        }
      } catch (error) {
        console.error('Error joining category:', error)
      }
    }

    onMounted(() => {
      fetchCategories()
    })

    return {
      categories,
      joinCategory
    }
  }
}
</script>

<style scoped>
.category-club {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
}

.categories-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.category-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.category-card:hover {
  transform: translateY(-5px);
}

.category-card h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.category-stats {
  display: flex;
  justify-content: space-between;
  margin: 1rem 0;
  color: #666;
}

.join-btn {
  width: 100%;
  padding: 0.8rem;
  border: none;
  border-radius: 4px;
  background-color: #42b983;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.join-btn:hover {
  background-color: #3aa876;
}

.join-btn.joined {
  background-color: #666;
  cursor: default;
}
</style> 
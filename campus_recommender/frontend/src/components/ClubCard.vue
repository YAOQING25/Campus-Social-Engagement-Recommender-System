<template>
  <div class="club-card">
    <img :src="club.image" :alt="club.name" class="club-image">
    
    <div class="club-content">
      <div class="club-header">
        <h3>{{ club.name }}</h3>
        <div class="rating">
          <span class="stars">★★★★★</span>
          <span class="rating-number">{{ club.rating }}</span>
        </div>
      </div>

      <p class="description">{{ club.description }}</p>
      
      <div class="club-info">
        <span class="member-count">
          <i class="fas fa-users"></i> {{ club.memberCount }} 成员
        </span>
        <span class="category">
          {{ getCategoryName(club.category) }}
        </span>
      </div>

      <div class="actions">
        <button 
          class="action-btn like"
          :class="{ active: club.isLiked }"
          @click="$emit('like', club.id)"
        >
          <i class="fas fa-heart"></i>
          {{ club.isLiked ? '已点赞' : '点赞' }}
        </button>

        <button 
          class="action-btn favorite"
          :class="{ active: club.isFavorited }"
          @click="$emit('favorite', club.id)"
        >
          <i class="fas fa-star"></i>
          {{ club.isFavorited ? '已收藏' : '收藏' }}
        </button>

        <button 
          class="action-btn apply"
          @click="$emit('apply', club.id)"
        >
          申请加入
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  club: {
    type: Object,
    required: true
  }
})

const getCategoryName = (category) => {
  const categories = {
    sports: '体育类',
    academic: '学术类',
    art: '艺术类',
    technology: '科技类'
  }
  return categories[category] || category
}
</script>

<style scoped>
.club-card {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.club-card:hover {
  transform: translateY(-5px);
}

.club-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.club-content {
  padding: 1.5rem;
}

.club-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.club-header h3 {
  margin: 0;
  color: #333;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars {
  color: #ffd700;
}

.description {
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.club-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: #666;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background 0.3s;
}

.action-btn i {
  font-size: 0.9rem;
}

.like {
  background: #f8f9fa;
  color: #666;
}

.like.active {
  background: #ff4757;
  color: white;
}

.favorite {
  background: #f8f9fa;
  color: #666;
}

.favorite.active {
  background: #ffd700;
  color: white;
}

.apply {
  background: #667eea;
  color: white;
}

.apply:hover {
  background: #764ba2;
}
</style> 
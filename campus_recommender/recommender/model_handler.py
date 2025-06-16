import tensorflow as tf
import numpy as np
from scipy.sparse import load_npz
import pickle
import os
from django.conf import settings
from .models import Student, Club, Interaction
from django.db.models import Count, Q
import logging
import glob
import sys

# Configure logging
logger = logging.getLogger(__name__)

class ModelHandler:
    """
    Model handler for recommendation system using the trained hybrid model.
    """
    
    def __init__(self):
        """Initialize the model handler by loading the trained model and necessary data."""
        # Set correct paths - try multiple possible paths
        self.base_dirs = []
        
        # 1. Try Django settings
        if hasattr(settings, 'BASE_DIR'):
            self.base_dirs.append(settings.BASE_DIR)
        
        # 2. Try inferring from current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        self.base_dirs.append(parent_dir)
        self.base_dirs.append(os.path.dirname(parent_dir))
        
        # 3. Try using relative paths
        self.base_dirs.append(os.path.join(os.getcwd(), 'campus_recommender'))
        self.base_dirs.append(os.getcwd())
        
        # Log the directories being searched
        logger.info(f"Attempting to find data files in the following paths: {self.base_dirs}")
        
        # Find model files
        self.model_path = self._find_file('hybrid_recommendation_model.keras')
        self.student_vectors_path = self._find_file('student_vectors.npz')
        self.club_vectors_path = self._find_file('club_vectors.npz') or self._find_file('club_vectors .npz')  # Note the space
        self.vectorizer_path = self._find_file('vectorizer.pkl')
        
        logger.info(f"Found file paths:")
        logger.info(f"Model file: {self.model_path}")
        logger.info(f"Student vectors: {self.student_vectors_path}")
        logger.info(f"Club vectors: {self.club_vectors_path}")
        logger.info(f"Vectorizer: {self.vectorizer_path}")
        
        # Create index mappings
        self.student_id_mapping = {}
        self.club_id_mapping = {}
        
        # Load model and data
        self.model = None
        self.student_vectors = None
        self.club_vectors = None
        self.vectorizer = None
        self._load_model_and_data()
        
        # Enable verbose output
        self.verbose = True
    
    def _find_file(self, filename):
        """Search for a file in multiple possible locations"""
        for base_dir in self.base_dirs:
            # Try data directory
            data_path = os.path.join(base_dir, 'data', filename)
            if os.path.exists(data_path):
                return data_path
                
            # Try recommender/data directory
            rec_data_path = os.path.join(base_dir, 'recommender', 'data', filename)
            if os.path.exists(rec_data_path):
                return rec_data_path
                
            # Try project root directory
            root_path = os.path.join(base_dir, filename)
            if os.path.exists(root_path):
                return root_path
        
        # Last attempt: search in all subdirectories
        for base_dir in self.base_dirs:
            for root, dirs, files in os.walk(base_dir):
                if filename in files:
                    return os.path.join(root, filename)
        
        return None
    
    def _load_model_and_data(self):
        """Load model and data files"""
        try:
            # Check if all necessary files are found
            if not all([self.model_path, self.student_vectors_path, self.club_vectors_path, self.vectorizer_path]):
                missing = []
                if not self.model_path:
                    missing.append("Model file")
                if not self.student_vectors_path:
                    missing.append("Student vectors")
                if not self.club_vectors_path:
                    missing.append("Club vectors")
                if not self.vectorizer_path:
                    missing.append("Vectorizer")
                    
                logger.error(f"Could not find necessary data files: {', '.join(missing)}")
                return
            
            # Load model
            logger.info(f"Attempting to load model: {self.model_path}")
            try:
                self.model = tf.keras.models.load_model(self.model_path, compile=False)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {str(e)}", exc_info=True)
                # Try loading with custom objects
                try:
                    logger.info("Attempting to load model with custom objects")
                    self.model = tf.keras.models.load_model(
                        self.model_path, 
                        compile=False,
                        custom_objects={'tf': tf}
                    )
                    logger.info("Model loaded successfully with custom objects")
                except Exception as e2:
                    logger.error(f"Second attempt to load model failed: {str(e2)}", exc_info=True)
                    return
            
            # Load student vectors
            logger.info(f"Attempting to load student vectors: {self.student_vectors_path}")
            try:
                self.student_vectors = load_npz(self.student_vectors_path).toarray()
                logger.info(f"Student vectors loaded successfully, shape: {self.student_vectors.shape}")
            except Exception as e:
                logger.error(f"Error loading student vectors: {str(e)}", exc_info=True)
                return
            
            # Load club vectors
            logger.info(f"Attempting to load club vectors: {self.club_vectors_path}")
            try:
                self.club_vectors = load_npz(self.club_vectors_path).toarray()
                logger.info(f"Club vectors loaded successfully, shape: {self.club_vectors.shape}")
            except Exception as e:
                logger.error(f"Error loading club vectors: {str(e)}", exc_info=True)
                return
            
            # Load vectorizer
            logger.info(f"Attempting to load vectorizer: {self.vectorizer_path}")
            try:
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                logger.info("Vectorizer loaded successfully")
            except Exception as e:
                logger.error(f"Error loading vectorizer: {str(e)}", exc_info=True)
                return
            
            # Initialize ID mappings
            self._initialize_id_mappings()
            logger.info("All data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model or data: {str(e)}", exc_info=True)
    
    def _initialize_id_mappings(self):
        """Initialize ID mappings to resolve index alignment issues"""
        try:
            # Create student ID to vector index mapping
            students = Student.objects.all()
            for i, student in enumerate(students):
                if i < len(self.student_vectors):
                    self.student_id_mapping[student.id] = i
            
            # Create club ID to vector index mapping
            clubs = Club.objects.all()
            for i, club in enumerate(clubs):
                if i < len(self.club_vectors):
                    self.club_id_mapping[club.id] = i
            
            logger.info(f"ID mappings initialized: {len(self.student_id_mapping)} students, {len(self.club_id_mapping)} clubs")
        except Exception as e:
            logger.error(f"Error initializing ID mappings: {str(e)}", exc_info=True)
    
    def _print_terminal(self, message):
        """Print to terminal and log the message"""
        if self.verbose:
            print(message, flush=True)
        logger.info(message)
    
    def get_hybrid_recommendations(self, student, top_n=5, cbf_weight=0.4):
        """
        Improved hybrid recommendation method that better integrates content and collaborative filtering results.
        
        Args:
            student: Student object
            top_n: Number of recommendations to return
            cbf_weight: Weight for content-based filtering (0-1)
            
        Returns:
            List of dictionaries with club_id and score
        """
        self._print_terminal(f"Getting hybrid recommendations for student {student.id}")
        self._print_terminal(f"Hybrid: Starting hybrid recommendations for student PK {student.id}, Student ID {student.student_id}")
        
        if self.model is None:
            self._print_terminal("Model not loaded, unable to provide hybrid model recommendations")
            # Attempt to reload model
            self._load_model_and_data()
            
            # If model still not loaded, use simplified hybrid recommendations
            if self.model is None:
                self._print_terminal("Model reload failed, using simplified hybrid recommendation method")
                return self._get_simplified_hybrid_recommendations(student, top_n, cbf_weight)
        
        try:
            # Get student index using mapping
            student_id = self.student_id_mapping.get(student.id)
            if student_id is None:
                self._print_terminal(f"WARNING:recommender.model_handler:Student ID {student.student_id} (PK {student.id}) not found in student_id_map. Falling back to attribute-based matching.")
                # Fallback to simple indexing
                student_id = min(int(student.id) - 1, len(self.student_vectors) - 1)
                if student_id < 0:
                    student_id = 0
            
            # Get content-based recommendations
            cbf_recommendations = self.get_content_based_recommendations(student, top_n)
            self._print_terminal(f"Hybrid: Got {len(cbf_recommendations)} content-based recommendations: {cbf_recommendations}")
            
            # Get collaborative filtering recommendations
            cf_recommendations = self.get_collaborative_recommendations(student, top_n)
            self._print_terminal(f"Hybrid: Got {len(cf_recommendations)} collaborative filtering recommendations: {cf_recommendations}")
            
            # Get all clubs
            clubs = list(Club.objects.all())
            num_clubs = len(clubs)
            if num_clubs == 0:
                self._print_terminal("No clubs found in database, unable to provide recommendations")
                return []
            
            # Ensure data dimensions match
            num_clubs_to_use = min(num_clubs, len(self.club_vectors)) if self.club_vectors is not None else num_clubs
            
            # Prepare hybrid recommendation results
            # Identify all unique club IDs from recommendations
            unique_club_ids = set()
            for rec in cbf_recommendations:
                unique_club_ids.add(rec['club_id'])
            for rec in cf_recommendations:
                unique_club_ids.add(rec['club_id'])
            
            self._print_terminal(f"Hybrid: Found {len(unique_club_ids)} unique clubs to evaluate for hybrid scoring.")
            
            # Calculate hybrid scores for each recommended club
            cbf_scores = {rec['club_id']: rec['score'] for rec in cbf_recommendations}
            cf_scores = {rec['club_id']: rec['score'] for rec in cf_recommendations}
            
            # Normalize scores
            if cbf_scores:
                cbf_max = max(cbf_scores.values())
                if cbf_max > 0:
                    for club_id in cbf_scores:
                        cbf_scores[club_id] /= cbf_max  # Normalize CBF scores
            
            if cf_scores:
                cf_max = max(cf_scores.values()) 
                if cf_max > 0:
                    for club_id in cf_scores:
                        cf_scores[club_id] /= cf_max  # Normalize CF scores
            
            # Log normalized scores
            self._print_terminal(f"Hybrid: Normalized CBF scores: {cbf_scores}")
            self._print_terminal(f"Hybrid: Normalized CF scores: {cf_scores}")
            
            # Dynamically adjust weights - increase CBF weight if CF recommendations are few; favor CF if sufficient
            adjusted_cbf_weight = cbf_weight
            if len(cf_recommendations) < 2:
                adjusted_cbf_weight = min(0.8, cbf_weight + 0.3)
                self._print_terminal(f"Hybrid: Adjusting CBF weight from {cbf_weight} to {adjusted_cbf_weight} due to few CF recommendations")
            elif len(cf_recommendations) >= top_n:
                adjusted_cbf_weight = max(0.2, cbf_weight - 0.1)
                self._print_terminal(f"Hybrid: Adjusting CBF weight from {cbf_weight} to {adjusted_cbf_weight} to favor CF recommendations")
            
            # Calculate final hybrid scores
            hybrid_scores = {}
            for club_id in unique_club_ids:
                norm_cbf = cbf_scores.get(club_id, 0.0)
                norm_cf = cf_scores.get(club_id, 0.0)
                
                # Adjust with model prediction if available
                model_score = 0.0
                if self.model is not None and student_id is not None and club_id in self.club_id_mapping:
                    club_idx = self.club_id_mapping.get(club_id)
                    if club_idx is not None and self.student_vectors is not None and self.club_vectors is not None:
                        try:
                            # Prepare input data for single prediction
                            student_vec = np.tile(self.student_vectors[student_id], (1, 1))
                            club_vec = self.club_vectors[club_idx].reshape(1, -1)
                            student_idx = np.array([[student_id]])
                            club_idx_arr = np.array([[club_idx]])
                            
                            single_input = {
                                "student_vector": student_vec,
                                "club_vector": club_vec,
                                "student_idx": student_idx,
                                "club_idx": club_idx_arr
                            }
                            
                            # Get model prediction
                            pred_score = self.model.predict(single_input, verbose=0)[0][0]
                            model_score = float(pred_score)
                        except Exception as e:
                            logger.error(f"Error predicting score for single club: {str(e)}", exc_info=True)
                
                # Calculate weighted average score
                if model_score > 0:
                    # Use model score to adjust final score
                    final_score = (adjusted_cbf_weight * norm_cbf + 
                                  (1 - adjusted_cbf_weight) * norm_cf + 
                                  model_score) / 2
                else:
                    # Use only CBF and CF scores
                    final_score = adjusted_cbf_weight * norm_cbf + (1 - adjusted_cbf_weight) * norm_cf
                
                hybrid_scores[club_id] = final_score
                
                club_name = next((club.name for club in clubs if club.id == club_id), f"Club {club_id}")
                self._print_terminal(f"Hybrid: Club {club_id} - NormCBF: {norm_cbf:.2f}, NormCF: {norm_cf:.2f}, ModelScore: {model_score:.2f}, WeightCBF: {adjusted_cbf_weight:.1f}, FinalHybrid: {final_score:.2f}")
            
            # Sort and select top_n recommendations
            sorted_clubs = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            
            # Create recommendation list
            recommendations = []
            for club_id, score in sorted_clubs:
                club = next((c for c in clubs if c.id == club_id), None)
                if club:
                    recommendations.append({
                        'club_id': club_id,
                        'score': score,
                        'type': 'hybrid',
                        'club_name': club.name,
                        'club_category': club.category
                    })
            
            self._print_terminal(f"Final recommendations for student {student.id}: {recommendations}")
            return recommendations
        except Exception as e:
            logger.error(f"Error generating hybrid recommendations: {str(e)}", exc_info=True)
            self._print_terminal(f"Hybrid: Error in model-based hybrid recommendations. Falling back to simplified hybrid method.")
            return self._get_simplified_hybrid_recommendations(student, top_n, cbf_weight)
    
    def _get_simplified_hybrid_recommendations(self, student, top_n=5, cbf_weight=0.5):
        """
        Simplified hybrid recommendation method used when the primary hybrid method fails
        """
        try:
            # Get recommendations
            cbf_recommendations = self.get_content_based_recommendations(student, top_n * 2)  # Get more recommendations for diversity
            cf_recommendations = self.get_collaborative_recommendations(student, top_n * 2)
            
            # Merge recommendations
            all_recommendations = {}
            
            # Process CBF recommendations
            for rec in cbf_recommendations:
                all_recommendations[rec['club_id']] = {
                    'cbf_score': rec['score'],
                    'cf_score': 0,
                    'club_name': rec['club_name'],
                    'club_category': rec['club_category']
                }
            
            # Process CF recommendations
            for rec in cf_recommendations:
                if rec['club_id'] in all_recommendations:
                    all_recommendations[rec['club_id']]['cf_score'] = rec['score']
                else:
                    all_recommendations[rec['club_id']] = {
                        'cbf_score': 0,
                        'cf_score': rec['score'],
                        'club_name': rec['club_name'],
                        'club_category': rec['club_category']
                    }
            
            # Normalize scores
            cbf_max = max([r['cbf_score'] for r in all_recommendations.values()]) if all_recommendations else 1.0
            cf_max = max([r['cf_score'] for r in all_recommendations.values()]) if all_recommendations else 1.0
            
            if cbf_max == 0: cbf_max = 1.0
            if cf_max == 0: cf_max = 1.0
            
            # Calculate hybrid scores
            hybrid_scores = []
            for club_id, rec in all_recommendations.items():
                norm_cbf = rec['cbf_score'] / cbf_max
                norm_cf = rec['cf_score'] / cf_max
                hybrid_score = cbf_weight * norm_cbf + (1 - cbf_weight) * norm_cf
                
                hybrid_scores.append({
                    'club_id': club_id,
                    'score': hybrid_score,
                    'type': 'hybrid-simplified',
                    'club_name': rec['club_name'],
                    'club_category': rec['club_category']
                })
            
            # Sort and return top_n recommendations
            sorted_recommendations = sorted(hybrid_scores, key=lambda x: x['score'], reverse=True)[:top_n]
            self._print_terminal(f"Simplified hybrid recommendations for student {student.id}: {sorted_recommendations}")
            return sorted_recommendations
            
        except Exception as e:
            logger.error(f"Error in simplified hybrid recommendations: {str(e)}", exc_info=True)
            self._print_terminal("Simplified hybrid recommendations failed, returning content-based recommendations only")
            return self.get_content_based_recommendations(student, top_n)
    
    def get_content_based_recommendations(self, student, top_n=5):
        """
        Improved content-based recommendation algorithm using more precise matching of student attributes with clubs.
        
        Args:
            student: Student object
            top_n: Number of recommendations to return
            
        Returns:
            List of dictionaries with club_id and score
        """
        self._print_terminal(f"Hybrid: Getting content-based recommendations")
        self._print_terminal(f"CBF: Starting content-based filtering for student PK {student.id}, Student ID {student.student_id}")
        
        try:
            # Get all clubs
            clubs = list(Club.objects.all())
            if not clubs:
                self._print_terminal("No clubs found in database, unable to provide recommendations")
                return []
            
            self._print_terminal(f"CBF: Found {len(clubs)} clubs to evaluate")
            
            # Get student attributes
            hobbies = student.hobbies if hasattr(student, 'hobbies') and student.hobbies else []
            interests = student.interests if hasattr(student, 'interests') and student.interests else []
            skills = student.skills if hasattr(student, 'skills') and student.skills else []
            course = student.course if hasattr(student, 'course') else ''
            
            self._print_terminal(f"CBF: Student attributes - hobbies: {hobbies}, interests: {interests}, skills: {skills}, course: {course}")
            
            # Set weights for attributes
            weights = {
                'category_match': 3.0,    # Highest weight for category matching
                'description_match': 2.0, # Description matching
                'name_match': 1.5,        # Name matching
                'course_match': 1.0       # Course matching
            }
            
            # Define category mapping - map student interests to club categories
            category_mapping = {
                # Arts-related mapping
                'arts': ['arts', 'creative', 'design', 'music', 'photography', 'film', 'drama', 'drawing', 'painting'],
                'literature': ['literature', 'reading', 'writing', 'poetry', 'book', 'arts'],
                'music': ['music', 'singing', 'choir', 'band', 'orchestra', 'arts'],
                'photography': ['photography', 'camera', 'arts', 'visual'],
                'design': ['design', 'graphic', 'arts', 'creative', 'visual'],
                'drawing': ['drawing', 'sketch', 'arts', 'creative', 'visual'],
                'painting': ['painting', 'arts', 'creative', 'visual'],
                
                # Academic-related mapping
                'academics': ['academics', 'study', 'learning', 'education', 'research', 'science'],
                'mathematics': ['mathematics', 'math', 'algebra', 'calculus', 'academics', 'science'],
                'science': ['science', 'physics', 'chemistry', 'biology', 'academics', 'research'],
                'technology': ['technology', 'computer', 'programming', 'coding', 'tech', 'it'],
                'engineering': ['engineering', 'mechanics', 'electronics', 'design', 'technology'],
                'programming': ['programming', 'coding', 'software', 'development', 'technology', 'computer', 'tech'],
                
                # Sports-related mapping
                'sports': ['sports', 'athletic', 'fitness', 'exercise', 'team'],
                'basketball': ['basketball', 'sports', 'team', 'athletic'],
                'football': ['football', 'sports', 'team', 'athletic'],
                'soccer': ['soccer', 'sports', 'team', 'athletic'],
                'swimming': ['swimming', 'sports', 'athletic'],
                'tennis': ['tennis', 'sports', 'athletic'],
                'fitness': ['fitness', 'gym', 'health', 'exercise', 'sports'],
                
                # Community service-related mapping
                'volunteer': ['volunteer', 'service', 'community', 'charity', 'helping'],
                'environment': ['environment', 'nature', 'climate', 'sustainability', 'green'],
                'social': ['social', 'community', 'networking', 'cultural', 'diversity'],
                'leadership': ['leadership', 'management', 'organization', 'entrepreneurship'],
                'business': ['business', 'entrepreneurship', 'finance', 'marketing', 'economics'],
                
                # Other categories
                'gaming': ['gaming', 'games', 'video games', 'esports', 'entertainment'],
                'food': ['food', 'cooking', 'culinary', 'baking', 'nutrition'],
                'travel': ['travel', 'adventure', 'exploration', 'culture']
            }
            
            # Flatten student interests and hobbies for easier matching
            student_interests = []
            for item in hobbies + interests + skills:
                student_interests.append(item.lower())
                
            if course:
                student_interests.append(course.lower())
            
            # Calculate relevance score for each club
            club_scores = []
            for club in clubs:
                score = 0.0
                
                # 1. Category matching - match club category with student interests
                if club.category:
                    category_lower = club.category.lower()
                    
                    # Direct category matching
                    for interest in student_interests:
                        if interest == category_lower:
                            score += weights['category_match']
                            self._print_terminal(f"CBF: Direct category match for {club.name} with {interest} (+{weights['category_match']})")
                            break
                    
                    # Indirect matching using category mapping
                    for interest in student_interests:
                        for category, related_terms in category_mapping.items():
                            if interest in related_terms and category_lower in related_terms:
                                score += weights['category_match'] * 0.8  # 80% of direct match weight
                                self._print_terminal(f"CBF: Indirect category match for {club.name} via {interest} and {category} (+{weights['category_match'] * 0.8})")
                                break
                
                # 2. Name matching - check if club name contains student interests
                if club.name:
                    name_lower = club.name.lower()
                    for interest in student_interests:
                        if interest in name_lower or name_lower in interest:
                            score += weights['name_match']
                            self._print_terminal(f"CBF: Name match for {club.name} with {interest} (+{weights['name_match']})")
                            break
                
                # 3. Description matching - if description exists, check for student interests
                if hasattr(club, 'description') and club.description:
                    desc_lower = club.description.lower()
                    for interest in student_interests:
                        if interest in desc_lower:
                            score += weights['description_match']
                            self._print_terminal(f"CBF: Description match for {club.name} with {interest} (+{weights['description_match']})")
                            break
                
                # 4. Course relevance - if club is related to student’s course
                if course and hasattr(club, 'target_courses') and club.target_courses:
                    if isinstance(club.target_courses, list):
                        for target_course in club.target_courses:
                            if course.lower() in target_course.lower():
                                score += weights['course_match']
                                self._print_terminal(f"CBF: Course match for {club.name} with {course} (+{weights['course_match']})")
                                break
                    elif isinstance(club.target_courses, str):
                        if course.lower() in club.target_courses.lower():
                            score += weights['course_match']
                            self._print_terminal(f"CBF: Course match for {club.name} with {course} (+{weights['course_match']})")
                
                # Add base score to avoid zero scores
                score = max(score, 0.01)
                
                # Save score
                club_scores.append((club, score))
                self._print_terminal(f"CBF: Club {club.name} (ID: {club.id}) final score: {score:.2f}")
            
            # Sort and get top_n recommendations
            sorted_clubs = sorted(club_scores, key=lambda x: x[1], reverse=True)[:top_n]
            
            # Create recommendation list
            recommendations = []
            for club, score in sorted_clubs:
                recommendations.append({
                    'club_id': club.id,
                    'score': float(score),
                    'type': 'content-based-attributes',
                    'club_name': club.name,
                    'club_category': club.category
                })
            
            self._print_terminal(f"CBF: Found {len(recommendations)} clubs with matching scores")
            self._print_terminal(f"CBF: Returning {len(recommendations)} recommendations")
            return recommendations
        
        except Exception as e:
            logger.error(f"Error generating content-based recommendations: {str(e)}", exc_info=True)
            
            # Fallback to vector similarity (if available)
            if self.student_vectors is not None and self.club_vectors is not None:
                try:
                    self._print_terminal("CBF: Error in attribute-based matching. Trying vector similarity as fallback.")
                    return self._get_vector_based_recommendations(student, top_n)
                except Exception as e2:
                    logger.error(f"Vector similarity fallback failed: {str(e2)}", exc_info=True)
            
        return [] 
    
    def _get_vector_based_recommendations(self, student, top_n=5):
        """
        Helper method for recommendations using vector similarity
        """
        # Get student index using mapping
        student_id = self.student_id_mapping.get(student.id)
        if student_id is None:
            # Fallback to simple indexing
            student_id = min(int(student.id) - 1, len(self.student_vectors) - 1)
            if student_id < 0:
                student_id = 0
        
        # Calculate cosine similarity
        student_vec = self.student_vectors[student_id].reshape(1, -1)
        similarities = np.dot(student_vec, self.club_vectors.T)[0]
        
        # Get all clubs
        clubs = list(Club.objects.all())
        
        # Get recommended clubs
        num_clubs = min(len(clubs), len(similarities))
        top_indices = np.argsort(similarities[:num_clubs])[::-1][:top_n]
        top_scores = similarities[top_indices]
        
        # Create recommendation list
        recommendations = []
        for idx, score in zip(top_indices, top_scores):
            if idx < len(clubs):  # Ensure index is valid
                club = clubs[idx]
                self._print_terminal(f"CBF Vector: Club {club.name} (ID: {club.id}) scored {score:.2f}")
                recommendations.append({
                    'club_id': int(club.id),
                    'score': float(score),
                    'type': 'content-based-vectors',
                    'club_name': club.name,
                    'club_category': club.category
                })
        
        return recommendations
    
    def get_collaborative_recommendations(self, student, top_n=5, top_k_users=20):
        """
        Improved collaborative filtering recommendation implementation.
        Generates collaborative filtering recommendations based on student interaction data.
        
        Args:
            student: Student object
            top_n: Number of recommendations to return
            top_k_users: Number of similar users to consider
            
        Returns:
            List of dictionaries with club_id and score
        """
        self._print_terminal(f"Hybrid: Getting collaborative filtering recommendations")
        self._print_terminal(f"CF: Starting collaborative filtering for student PK {student.id}, Student ID {student.student_id}")
        
        try:
            # Get current student’s interactions (as a set for efficient lookup)
            student_interacted_club_ids = set(Interaction.objects.filter(
                student=student
            ).values_list('club_id', flat=True))
            
            if not student_interacted_club_ids:
                self._print_terminal(f"CF: Student {student.id} has no interactions. Using content-based as fallback.")
                recommendations = self.get_content_based_recommendations(student, top_n)
                for rec in recommendations:
                    rec['type'] = 'collaborative-fallback'
                return recommendations
            
            interacted_clubs_details = Club.objects.filter(id__in=student_interacted_club_ids)
            student_interactions_log = [
                {'club_id': c.id, 'club_name': c.name} for c in interacted_clubs_details
            ]
            self._print_terminal(f"CF: Student PK {student.id} has interacted with (IDs: {student_interacted_club_ids}): {student_interactions_log}")
            
            # Lower similarity requirement: consider users with at least one common interaction
            similar_students_qs = Student.objects.filter(
                interaction__club_id__in=student_interacted_club_ids
            ).exclude(
                id=student.id
            ).annotate(
                overlap_count=Count('interaction__club_id', filter=Q(interaction__club_id__in=student_interacted_club_ids), distinct=True)
            ).filter(
                overlap_count__gte=1  # At least one common interaction
            ).order_by('-overlap_count')[:top_k_users]
            
            similar_student_pks = [s.id for s in similar_students_qs]
            
            if not similar_student_pks:
                self._print_terminal(f"CF: No similar students found for student PK {student.id} (based on current interactions). Using content-based as fallback.")
                recommendations = self.get_content_based_recommendations(student, top_n)
                for rec in recommendations:
                    rec['type'] = 'collaborative-fallback'
                return recommendations
            
            self._print_terminal(f"CF: Found {len(similar_student_pks)} similar students (PKs: {similar_student_pks}). Overlap counts: {[s.overlap_count for s in similar_students_qs]}")

            all_similar_student_interactions = Interaction.objects.filter(student_id__in=similar_student_pks)
            all_similar_interactions_log = []
            clubs_for_log_dict = {c.id: c.name for c in Club.objects.filter(id__in=all_similar_student_interactions.values_list('club_id', flat=True).distinct())}
            for interaction_obj in all_similar_student_interactions:
                all_similar_interactions_log.append({
                    'student_pk': interaction_obj.student_id,
                    'club_pk': interaction_obj.club_id,
                    'club_name': clubs_for_log_dict.get(interaction_obj.club_id, f"Club PK {interaction_obj.club_id}")
                })
            self._print_terminal(f"CF DIAGNOSTIC: All clubs interacted with by similar students (before filtering known clubs): {all_similar_interactions_log}")

            # Get all clubs interacted with by similar users, including those already interacted by the current student
            all_club_interaction_counts = Interaction.objects.filter(
                student_id__in=similar_student_pks
            ).values(
                'club_id'
            ).annotate(
                interaction_count=Count('student_id', distinct=True)
            ).order_by('-interaction_count')
            
            # Separate new and known clubs
            new_club_interactions = []
            known_club_interactions = []
            
            for item in all_club_interaction_counts:
                if item['club_id'] in student_interacted_club_ids:
                    known_club_interactions.append(item)
                else:
                    new_club_interactions.append(item)
            
            # Ensure enough recommendations
            # If new clubs are insufficient, add some popular known clubs
            candidate_interactions = new_club_interactions
            if len(new_club_interactions) < top_n:
                self._print_terminal(f"CF: Only {len(new_club_interactions)} new clubs found. Adding some popular known clubs.")
                # Add some popular known clubs, up to half of top_n
                num_known_to_add = min(top_n - len(new_club_interactions), top_n // 2)
                candidate_interactions.extend(known_club_interactions[:num_known_to_add])
            
            # Get top_n candidate clubs
            top_candidate_interactions = candidate_interactions[:top_n]
            
            # Get details for all candidate clubs
            candidate_club_ids = [item['club_id'] for item in top_candidate_interactions]
            candidate_clubs_dict = {club.id: club for club in Club.objects.filter(id__in=candidate_club_ids)}
            
            self._print_terminal(f"CF: Candidate clubs (including some known clubs): {[{'club_id': item['club_id'], 'club_name': candidate_clubs_dict.get(item['club_id'], {}).name, 'similar_user_interactions': item['interaction_count'], 'is_new': item['club_id'] not in student_interacted_club_ids} for item in top_candidate_interactions]}")
            
            recommendations = []
            for club_data in top_candidate_interactions:
                club_id = club_data['club_id']
                club_obj = candidate_clubs_dict.get(club_id)
                if club_obj:
                    score = float(club_data['interaction_count']) / len(similar_student_pks)
                    is_known = club_id in student_interacted_club_ids
                    recommendations.append({
                        'club_id': club_id,
                        'score': score,
                        'type': 'collaborative-known-club' if is_known else 'collaborative-similar-users',
                        'club_name': club_obj.name,
                        'club_category': club_obj.category
                    })
            
            self._print_terminal(f"CF: Returning {len(recommendations)} recommendations from similar users: {recommendations}")
            return recommendations
        except Exception as e:
            logger.error(f"Error generating collaborative filtering recommendations: {str(e)}", exc_info=True)
            self._print_terminal(f"CF: Error in collaborative filtering ({str(e)}). Falling back to content-based.")
            recommendations = self.get_content_based_recommendations(student, top_n)
            for rec in recommendations:
                rec['type'] = 'collaborative-fallback'
            return recommendations
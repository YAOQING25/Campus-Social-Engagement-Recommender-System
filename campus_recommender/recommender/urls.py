from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import admin_login, student_login, student_register, CategoryListView, CategoryJoinView, DashboardStatsView

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'clubs', views.ClubViewSet)
router.register(r'interactions', views.InteractionViewSet)
router.register(r'saved-clubs', views.SavedClubViewSet)
router.register(r'applications', views.ApplicationViewSet)
router.register(r'recommender', views.RecommenderViewSet, basename='recommender')
router.register(r'admins', views.AdminViewSet, basename='admin')

urlpatterns = [
    # Explicit login endpoints for admin login (singular and plural)
    path('admin/login/', admin_login, name='admin-login'),
    path('students/login/', student_login, name='student-login'),
    path('students/register/', student_register, name='student-register'),
    path('admins/login/', admin_login, name='admin-login-alias'),

    # Category management endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/', views.CategoryListView.as_view(), name='category-detail'),
    path('categories/<int:category_id>/join/', views.CategoryJoinView.as_view(), name='category-join'),

    # Dashboard statistics endpoint
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),

    # Custom interaction endpoints
    path('interactions/record-view/', views.InteractionViewSet.as_view({'post': 'record_view'}), name='record-view'),

    # Include all other router URLs (includes the reset_password action)
    path('', include(router.urls)),
]
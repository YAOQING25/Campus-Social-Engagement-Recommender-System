from django.contrib import admin
from .models import Student, Club, Category, Interaction, SavedClub, Admin

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_name', 'course', 'status')
    search_fields = ('student_id', 'user__username', 'course')
    list_filter = ('status', 'course')
    
    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_name.short_description = 'Name'

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    search_fields = ('name', 'category', 'description')
    list_filter = ('category',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'member_count', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('status',)
    filter_horizontal = ('members',)

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('student', 'club', 'interaction_type', 'timestamp')
    search_fields = ('student__student_id', 'club__name')
    list_filter = ('interaction_type', 'timestamp')

@admin.register(SavedClub)
class SavedClubAdmin(admin.ModelAdmin):
    list_display = ('student', 'club', 'saved_at')
    search_fields = ('student__student_id', 'club__name')
    list_filter = ('saved_at',)

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status', 'last_login')
    list_filter = ('role', 'status') 
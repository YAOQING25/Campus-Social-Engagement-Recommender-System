from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=8, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    course = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    hobbies = models.JSONField(default=list)
    interests = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure JSON fields are lists
        if self.hobbies is None:
            self.hobbies = []
        if self.interests is None:
            self.interests = []
        if self.skills is None:
            self.skills = []
        
        # Convert to list if string was provided
        if isinstance(self.hobbies, str):
            self.hobbies = [x.strip() for x in self.hobbies.split(',') if x.strip()]
        if isinstance(self.interests, str):
            self.interests = [x.strip() for x in self.interests.split(',') if x.strip()]
        if isinstance(self.skills, str):
            self.skills = [x.strip() for x in self.skills.split(',') if x.strip()]
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

class Club(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Interaction(models.Model):
    INTERACTION_TYPES = [
        ('join', 'Join'),
        ('like', 'Like'),
        ('view', 'View'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'club', 'interaction_type')

    def __str__(self):
        return f"{self.student} - {self.club} ({self.interaction_type})"

class SavedClub(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'club')

    def __str__(self):
        return f"{self.student} - {self.club}"

class Admin(models.Model):
    ROLE_CHOICES = [
        ('super', 'Super Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()

class Category(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField('Student', related_name='categories')

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()

    @property
    def activity_count(self):
        # Return 0 since we don't have activities
        return 0 

class Application(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    apply_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    # other fields as needed 
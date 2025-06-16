from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Club, Interaction, SavedClub, Admin, Category, Application

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Student
        fields = ('id', 'student_id', 'user', 'course', 'status', 'gender', 'hobbies', 'interests', 'skills')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                if attr == 'password':
                    instance.user.set_password(value)
                else:
                    setattr(instance.user, attr, value)
            instance.user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = '__all__'

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'
        read_only_fields = ('student',)

class SavedClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedClub
        fields = '__all__'
        read_only_fields = ('student',)

class AdminSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    name = serializers.SerializerMethodField()
    lastLogin = serializers.DateTimeField(source='last_login', format='%Y-%m-%d %H:%M')

    class Meta:
        model = Admin
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'name', 'role', 'status', 'lastLogin']

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def update(self, instance, validated_data):
        user_data = self.initial_data
        
        # Update user fields if provided
        if 'email' in user_data:
            instance.user.email = user_data.get('email')
        if 'first_name' in user_data:
            instance.user.first_name = user_data.get('first_name')
        if 'last_name' in user_data:
            instance.user.last_name = user_data.get('last_name')
        
        instance.user.save()
            
        # Update admin fields
        if 'role' in validated_data:
            instance.role = validated_data.get('role')
        if 'status' in validated_data:
            instance.status = validated_data.get('status')
            
        instance.save()
        return instance

class AdminCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=Admin.ROLE_CHOICES)

    class Meta:
        model = Admin
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
        }
        
        user = User.objects.create_user(**user_data)
        user.is_staff = True
        user.save()
        
        admin = Admin.objects.create(user=user, **validated_data)
        return admin 

class CategorySerializer(serializers.ModelSerializer):
    memberCount = serializers.IntegerField(source='member_count', read_only=True)
    activityCount = serializers.IntegerField(source='activity_count', read_only=True)
    isJoined = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status', 'memberCount', 'activityCount', 'isJoined']

    def get_isJoined(self, obj):
        request = self.context.get('request')
        # Only authenticated students can join categories
        if request and request.user.is_authenticated and hasattr(request.user, 'student'):
            try:
                student = request.user.student
                return obj.members.filter(id=student.id).exists()
            except Exception:
                return False
        return False 

class ApplicationSerializer(serializers.ModelSerializer):
    studentName = serializers.CharField(source='student.user.get_full_name', read_only=True)
    studentId = serializers.CharField(source='student.student_id', read_only=True)
    clubName = serializers.CharField(source='club.name', read_only=True)
    applyDate = serializers.DateField(source='apply_date', read_only=True)
    
    class Meta:
        model = Application
        fields = ['id', 'student', 'club', 'studentName', 'studentId', 'clubName', 'status', 'applyDate']
        read_only_fields = ['apply_date']
        extra_kwargs = {
            'student': {'required': False},  # Make student optional for testing
            'club': {'required': False}      # Make club optional for testing
        } 
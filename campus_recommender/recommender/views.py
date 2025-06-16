from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from .models import Student, Club, Interaction, SavedClub, Admin, Category, Application
from .serializers import (
    StudentSerializer, ClubSerializer, InteractionSerializer,
    SavedClubSerializer, UserSerializer, AdminSerializer, AdminCreateSerializer,
    CategorySerializer, ApplicationSerializer
)
from .model_handler import ModelHandler
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone

class StudentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StudentPagination

    def get_permissions(self):
        """
        Admin required for management operations
        """
        if self.action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Admins can see all students, regular users only see themselves
        """
        try:
            queryset = Student.objects.select_related('user').all().order_by('-user__date_joined')
            
            # Search functionality
            search = self.request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(
                    Q(user__username__icontains=search) |
                    Q(student_id__icontains=search) |
                    Q(user__email__icontains=search)
                )
                
            # Course filter
            course = self.request.query_params.get('course', None)
            if course:
                queryset = queryset.filter(course=course)
                
            return queryset
        except Exception as e:
            print(f"Error in get_queryset: {str(e)}")
            return Student.objects.none()

    def list(self, request, *args, **kwargs):
        """
        List students with additional metadata
        """
        try:
            response = super().list(request, *args, **kwargs)
            
            # Add available courses to response
            courses = Student.objects.values_list('course', flat=True).distinct()
            response.data['courses'] = list(filter(None, courses))
            
            return response
        except Exception as e:
            print(f"Error in list: {str(e)}")
            return Response({
                'error': 'Failed to fetch students',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        # DEBUG: Log incoming request for nested user field issue
        try:
            raw_body = request.body.decode('utf-8')
        except Exception:
            raw_body = request.body
        print("DEBUG create RAW_BODY:", raw_body)
        print("DEBUG create request.data:", request.data)
        print("DEBUG create user field type and value:", type(request.data.get('user')), request.data.get('user'))
        # Proceed with default nested creation
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update student and associated user
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # Update user if user data provided
            user_data = request.data.pop('user', None)
            if user_data:
                user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
                user_serializer.is_valid(raise_exception=True)
                user_serializer.save()
            
            # Update student
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(serializer.data)
        except Exception as e:
            print(f"Error in update: {str(e)}")
            return Response({
                'error': 'Failed to update student',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete student and associated user
        """
        try:
            instance = self.get_object()
            user = instance.user
            self.perform_destroy(instance)
            user.delete()  # Delete associated user
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error in destroy: {str(e)}")
            return Response({
                'error': 'Failed to delete student',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Returns the student profile of the currently authenticated user
        """
        try:
            student = Student.objects.get(user=request.user)
            serializer = self.get_serializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []
        return [IsAdminUser()]

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Interaction.objects.all()
        return Interaction.objects.filter(student__user=self.request.user)

    def perform_create(self, serializer):
        student = get_object_or_404(Student, user=self.request.user)
        serializer.save(student=student)
        
    @action(detail=False, methods=['post'])
    def record_view(self, request):
        """
        Record a view interaction, updating if it already exists.
        This avoids the UNIQUE constraint error.
        """
        try:
            # 确保用户已认证
            if request.user.is_anonymous:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            student = get_object_or_404(Student, user=request.user)
            club_id = request.data.get('club')
            
            if not club_id:
                return Response(
                    {'error': 'Club ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 尝试将club_id转换为整数
            try:
                club_id = int(club_id)
            except (ValueError, TypeError):
                return Response(
                    {'error': f'Invalid club ID: {club_id}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            club = get_object_or_404(Club, id=club_id)
            
            # 使用update_or_create避免唯一约束违规
            interaction, created = Interaction.objects.update_or_create(
                student=student,
                club=club,
                interaction_type='view',
                defaults={'timestamp': timezone.now()}
            )
            
            print(f"View interaction {'created' if created else 'updated'} for student {student.id} and club {club.id}")
            
            return Response(
                {
                    'success': True, 
                    'created': created,
                    'student_id': student.id,
                    'club_id': club.id,
                    'interaction_id': interaction.id,
                    'timestamp': interaction.timestamp
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        except Exception as e:
            print(f"Error in record_view: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SavedClubViewSet(viewsets.ModelViewSet):
    queryset = SavedClub.objects.all()
    serializer_class = SavedClubSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedClub.objects.filter(student__user=self.request.user)

    def perform_create(self, serializer):
        student = get_object_or_404(Student, user=self.request.user)
        serializer.save(student=student)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        # Allow any access for testing
        return [AllowAny()]
        
        # Original permission logic (commented out for now)
        # if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
        #     return [IsAdminUser()]
        # return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:  # Handle anonymous users
            return Application.objects.all().order_by('-apply_date')
        if user.is_staff:
            return Application.objects.all().order_by('-apply_date')
        
        # Regular users can only see their own applications
        try:
            student = Student.objects.get(user=user)
            return Application.objects.filter(student=student).order_by('-apply_date')
        except Student.DoesNotExist:
            return Application.objects.none()

    def perform_create(self, serializer):
        # For testing, allow applications without auth
        if self.request.user.is_anonymous:
            # Find a student to use (first one in the database)
            student = Student.objects.first()
            if student:
                serializer.save(student=student)
            else:
                # Can't create an application without a student
                raise serializers.ValidationError("No student available and user is not authenticated")
        else:
            # Get student object for the authenticated user
            student = get_object_or_404(Student, user=self.request.user)
            serializer.save(student=student)

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        application = self.get_object()
        application.status = 'approved'
        application.save()
        return Response({'status': 'application approved'})

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        application = self.get_object()
        application.status = 'rejected'
        application.save()
        return Response({'status': 'application rejected'})

class RecommenderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    model_handler = ModelHandler()

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        student = get_object_or_404(Student, user=request.user)
        n_recommendations = int(request.query_params.get('n', 5))
        
        recommendations = self.model_handler.get_hybrid_recommendations(
            student, top_n=n_recommendations
        )
        
        # Get full club details for recommendations
        club_details = []
        for rec in recommendations:
            club = get_object_or_404(Club, id=rec['club_id'])
            club_data = ClubSerializer(club).data
            club_data.update({
                'score': rec['score'],
                'recommendation_type': rec['type']
            })
            club_details.append(club_data)
        
        return Response(club_details)

    @action(detail=False, methods=['get'])
    def content_based(self, request):
        student = get_object_or_404(Student, user=request.user)
        n_recommendations = int(request.query_params.get('n', 5))
        
        recommendations = self.model_handler.get_content_based_recommendations(
            student, top_n=n_recommendations
        )
        
        # Get full club details for recommendations
        club_details = []
        for rec in recommendations:
            club = get_object_or_404(Club, id=rec['club_id'])
            club_data = ClubSerializer(club).data
            club_data.update({
                'score': rec['score'],
                'recommendation_type': rec['type']
            })
            club_details.append(club_data)
        
        return Response(club_details)

    @action(detail=False, methods=['get'])
    def collaborative(self, request):
        student = get_object_or_404(Student, user=request.user)
        n_recommendations = int(request.query_params.get('n', 5))
        
        recommendations = self.model_handler.get_collaborative_recommendations(
            student, top_n=n_recommendations
        )
        
        # Get full club details for recommendations
        club_details = []
        for rec in recommendations:
            club = get_object_or_404(Club, id=rec['club_id'])
            club_data = ClubSerializer(club).data
            club_data.update({
                'score': rec['score'],
                'recommendation_type': rec['type']
            })
            club_details.append(club_data)
        
        return Response(club_details)

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Filter admins based on role and search query
        """
        queryset = Admin.objects.all().order_by('id')
        
        # Filter by role if provided
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
            
        # Search by name or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
            
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminCreateSerializer
        return AdminSerializer
        
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Returns or updates the admin profile of the currently authenticated user
        """
        try:
            admin = Admin.objects.get(user=request.user)
            
            # Update admin profile
            if request.method in ['PUT', 'PATCH']:
                serializer = self.get_serializer(admin, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Return admin profile
            serializer = self.get_serializer(admin)
            return Response(serializer.data)
        except Admin.DoesNotExist:
            return Response(
                {'error': 'Admin profile not found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Reset the password for a specific admin user by ID
        """
        try:
            admin = self.get_object()
            user = admin.user
            
            # Get password data from request
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            
            # For API backward compatibility
            if not new_password:
                new_password = request.data.get('password')
                
            if not new_password:
                return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Current password verification is optional
            if current_password:
                # Only verify if provided
                if not user.check_password(current_password):
                    return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Update last login time
            admin.update_last_login()
            
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='me/reset_password')
    def me_reset_password(self, request):
        """
        Reset the password for the currently authenticated admin user
        """
        try:
            admin = Admin.objects.get(user=request.user)
            user = admin.user
            
            # Get password data from request
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            
            # For API backward compatibility
            if not new_password:
                new_password = request.data.get('password')
            
            if not new_password:
                return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Current password verification is optional
            if current_password:
                # Only verify if provided
                if not user.check_password(current_password):
                    return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Update last login time
            admin.update_last_login()
            
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        except Admin.DoesNotExist:
            return Response(
                {'error': 'Admin profile not found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def student_login(request):
    """Function-based view for student login."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    student_id = data.get('student_id')
    password = data.get('password')
    if not student_id or not password:
        return JsonResponse({'error': 'Provide student_id and password'}, status=400)
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    user = authenticate(username=student.user.username, password=password)
    if user is None:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    token, _ = Token.objects.get_or_create(user=user)
    return JsonResponse({
        'token': token.key,
        'user_id': user.pk,
        'student_id': student.student_id,
        'id': student.id,
        'email': user.email,
        'full_name': user.get_full_name(),
    })

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def student_register(request):
    """Function-based view for student registration."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    serializer = StudentSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    student = serializer.save()
    token, _ = Token.objects.get_or_create(user=student.user)
    return JsonResponse({
        'token': token.key,
        'user_id': student.user.pk,
        'student_id': student.student_id,
        'id': student.id,
        'email': student.user.email,
        'full_name': student.user.get_full_name(),
        'message': 'Student registered successfully'
    }, status=201)

@csrf_exempt
def admin_login(request):
    """Plain Django view for admin login, bypassing DRF auth/permission."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    if not user.is_staff:
        return JsonResponse({'error': 'Not an admin user'}, status=403)
    try:
        admin = Admin.objects.get(user=user)
        admin.update_last_login()
    except Admin.DoesNotExist:
        return JsonResponse({'error': 'Admin profile not found'}, status=404)
    token, _ = Token.objects.get_or_create(user=user)
    
    # Serialize admin data
    admin_data = AdminSerializer(admin).data
    
    # Include user ID for easier reference
    user_data = {
        'id': admin_data['id'],
        'username': admin_data['username'],
        'email': admin_data['email'],
        'first_name': admin_data['first_name'],
        'last_name': admin_data['last_name'],
        'name': admin_data['name'],
        'role': admin_data['role'],
        'status': admin_data['status'],
        'lastLogin': admin_data['lastLogin']
    }
    
    return JsonResponse({
        'token': token.key,
        'user': user_data
    })

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def student_logout(request):
    """Plain Django view for student logout, deleting the token"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Token '):
        return JsonResponse({'message': 'No token provided'}, status=400)
    token_key = auth_header.split(' ', 1)[1]
    try:
        token = Token.objects.get(key=token_key)
        token.delete()
        return JsonResponse({'message': 'Successfully logged out'})
    except Token.DoesNotExist:
        return JsonResponse({'message': 'Token not found or already logged out'}, status=200)

class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_id=None):
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                serializer = CategorySerializer(category, context={'request': request})
                return Response(serializer.data)
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Get query parameters
            search = request.query_params.get('search', '')
            status_filter = request.query_params.get('status', '')
            
            # Filter categories
            categories = Category.objects.all()
            if search:
                categories = categories.filter(name__icontains=search)
            if status_filter:
                categories = categories.filter(status=status_filter)
                
            # Pagination
            page = request.query_params.get('page', 1)
            try:
                page = int(page)
            except ValueError:
                page = 1
                
            page_size = 10
            start = (page - 1) * page_size
            end = start + page_size
            
            # Total pages calculation
            total_categories = categories.count()
            total_pages = (total_categories + page_size - 1) // page_size
            
            # Slice for pagination
            categories = categories[start:end]
            
            serializer = CategorySerializer(categories, many=True, context={'request': request})
            
            return Response({
                'results': serializer.data,
                'count': total_categories,
                'total_pages': total_pages,
                'current_page': page
            })

    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            serializer = CategorySerializer(category, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

class CategoryJoinView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            student = request.user.student
            
            if category.members.filter(id=student.id).exists():
                category.members.remove(student)
                message = 'Left category successfully'
            else:
                category.members.add(student)
                message = 'Joined category successfully'
            
            serializer = CategorySerializer(category, context={'request': request})
            return Response({
                'message': message,
                'category': serializer.data
            })
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=404) 
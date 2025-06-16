from django.core.management.base import BaseCommand
from recommender.models import Student, SavedClub, Club
from django.db import transaction
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check and diagnose saved clubs functionality'

    def handle(self, *args, **options):
        self.stdout.write('Checking saved clubs...')
        
        # Check if SavedClub model exists and has records
        saved_clubs_count = SavedClub.objects.count()
        self.stdout.write(f'Total saved clubs in database: {saved_clubs_count}')
        
        # Check all students and their saved clubs
        students = Student.objects.all()
        self.stdout.write(f'Total students: {students.count()}')
        
        for student in students:
            saved_clubs = SavedClub.objects.filter(student=student)
            self.stdout.write(f'Student ID: {student.student_id} (PK: {student.id}) has {saved_clubs.count()} saved clubs')
            
            for saved in saved_clubs:
                self.stdout.write(f'  - {saved.club.name} (ID: {saved.club.id}), Saved at: {saved.saved_at}')
        
        # Test creating a saved club
        try:
            with transaction.atomic():
                # Get a student and club
                student = Student.objects.first()
                club = Club.objects.first()
                
                if student and club:
                    self.stdout.write(f'Testing saving club {club.name} for student {student.student_id}...')
                    
                    # Check if it already exists
                    existing = SavedClub.objects.filter(student=student, club=club).first()
                    if existing:
                        self.stdout.write(f'Club already saved (ID: {existing.id})')
                    else:
                        # Try to create a new saved club
                        new_saved = SavedClub.objects.create(student=student, club=club)
                        self.stdout.write(f'Successfully created saved club with ID: {new_saved.id}')
                        
                        # Clean up the test data
                        new_saved.delete()
                        self.stdout.write('Test saved club deleted')
                else:
                    self.stdout.write('No student or club available for testing')
                    
                # Always rollback the transaction
                raise Exception("Rolling back transaction")
        except Exception as e:
            if str(e) != "Rolling back transaction":
                self.stdout.write(self.style.ERROR(f'Error testing saved clubs: {str(e)}'))
        
        # Check API endpoints
        self.stdout.write('\nAPI Endpoints for saved clubs:')
        self.stdout.write('- GET /api/saved-clubs/ - List saved clubs for current user')
        self.stdout.write('- POST /api/saved-clubs/ - Save a club (requires club ID)')
        self.stdout.write('- DELETE /api/saved-clubs/{id}/ - Remove a saved club') 
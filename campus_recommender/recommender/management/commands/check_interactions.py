from django.core.management.base import BaseCommand
from recommender.models import Student, Interaction, Club

class Command(BaseCommand):
    help = 'Check student interactions with clubs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking student interactions...'))
        
        # 查找ID为test13的学生
        student_13 = Student.objects.filter(student_id='test13').first()
        if student_13:
            self.stdout.write(f"Student test13 found: ID={student_13.id}, Name={student_13.user.username}")
            interactions = Interaction.objects.filter(student=student_13)
            if interactions:
                self.stdout.write(self.style.SUCCESS(f"Student test13 has {interactions.count()} interactions:"))
                for interaction in interactions:
                    self.stdout.write(f"- Club: {interaction.club.name} (ID: {interaction.club.id})")
            else:
                self.stdout.write(self.style.WARNING("Student test13 has no interactions"))
        else:
            self.stdout.write(self.style.ERROR("Student with ID 'test13' not found"))
            
        # 列出所有学生及其交互数
        self.stdout.write("\nAll students and their interaction counts:")
        for student in Student.objects.all():
            interaction_count = Interaction.objects.filter(student=student).count()
            self.stdout.write(f"Student ID: {student.student_id} (PK: {student.id}), Name: {student.user.username}, Interactions: {interaction_count}")
        
        # 列出所有交互
        self.stdout.write("\nAll interactions:")
        for interaction in Interaction.objects.all():
            self.stdout.write(f"Student: {interaction.student.student_id} (PK: {interaction.student.id}), Club: {interaction.club.name} (ID: {interaction.club.id})") 
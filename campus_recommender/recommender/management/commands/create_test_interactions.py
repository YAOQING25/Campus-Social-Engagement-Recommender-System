from django.core.management.base import BaseCommand
from recommender.models import Student, Club, Interaction, SavedClub
from django.utils import timezone

class Command(BaseCommand):
    help = '创建测试交互数据，包括浏览、点赞和收藏等'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除所有现有交互记录后再创建新数据',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('正在清除所有现有交互记录...')
            Interaction.objects.all().delete()
            SavedClub.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('已清除所有交互记录'))
        
        # 获取所有学生和俱乐部
        students = Student.objects.all()
        clubs = Club.objects.all()
        
        if not students:
            self.stdout.write(self.style.ERROR('没有学生记录，请先创建学生'))
            return
        
        if not clubs:
            self.stdout.write(self.style.ERROR('没有俱乐部记录，请先创建俱乐部'))
            return
        
        self.stdout.write(f'找到 {students.count()} 个学生和 {clubs.count()} 个俱乐部')
        
        # 为每个学生创建一些随机交互
        interaction_count = 0
        saved_club_count = 0
        
        for student in students:
            # 为每个学生生成一些交互记录
            # 学生浏览前3个社团
            for club in clubs[:3]:
                interaction, created = Interaction.objects.get_or_create(
                    student=student,
                    club=club,
                    interaction_type='view'
                )
                if created:
                    interaction_count += 1
                    self.stdout.write(f'学生 {student.user.username} 浏览了社团 {club.name}')
            
            # 学生点赞前2个社团
            if clubs.count() >= 2:
                for club in clubs[:2]:
                    interaction, created = Interaction.objects.get_or_create(
                        student=student,
                        club=club,
                        interaction_type='like'
                    )
                    if created:
                        interaction_count += 1
                        self.stdout.write(f'学生 {student.user.username} 点赞了社团 {club.name}')
            
            # 学生加入第1个社团
            if clubs.count() >= 1:
                interaction, created = Interaction.objects.get_or_create(
                    student=student,
                    club=clubs[0],
                    interaction_type='join'
                )
                if created:
                    interaction_count += 1
                    self.stdout.write(f'学生 {student.user.username} 加入了社团 {clubs[0].name}')
            
            # 学生收藏前2个社团
            if clubs.count() >= 2:
                for club in clubs[:2]:
                    saved_club, created = SavedClub.objects.get_or_create(
                        student=student,
                        club=club
                    )
                    if created:
                        saved_club_count += 1
                        self.stdout.write(f'学生 {student.user.username} 收藏了社团 {club.name}')
        
        self.stdout.write(self.style.SUCCESS(f'成功创建 {interaction_count} 条交互记录和 {saved_club_count} 条收藏记录')) 
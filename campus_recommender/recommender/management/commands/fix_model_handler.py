from django.core.management.base import BaseCommand
import os
import re

class Command(BaseCommand):
    help = 'Fix syntax error in model_handler.py'

    def handle(self, *args, **options):
        self.stdout.write('Fixing model_handler.py...')
        
        file_path = os.path.join('recommender', 'model_handler.py')
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the syntax error - look for the problematic line
        pattern = r'(\s+)self\._print_terminal\("数据库中没有俱乐部，无法提供推荐"\)(\s+)return \[\]'
        replacement = r'\1self._print_terminal("数据库中没有俱乐部，无法提供推荐")\1return []'
        
        # Apply the fix
        fixed_content = re.sub(pattern, replacement, content)
        
        # Write the fixed content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        self.stdout.write(self.style.SUCCESS('Successfully fixed model_handler.py')) 
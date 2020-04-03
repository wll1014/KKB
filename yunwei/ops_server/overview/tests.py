from django.test import TestCase

# Create your tests here.
# from .models import Map
import json

with open('./BoroughInfo.json', 'r', encoding='utf8')as f:
    x = f.read()

print(json.loads(x))
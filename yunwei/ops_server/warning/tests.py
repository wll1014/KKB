from django.test import TestCase

# Create your tests here.
import uuid
import time

start = time.time()
l = []
for i in range(100):
    u = uuid.uuid1()
    l.append(u)
print(l , time.time()-start)
import random
key = [0] * 32
for i in range(0,32):
    num = random.randint(0, 255)
    key[i] = num
p = 53
q = 59
n = p * q
e = 3
eKey = [0] * 32

t = (p-1)*(q-1)
k = 2
d = (k * t + 1) // e
for i in range(0,32):
    eKey[i] = (key[i] ** e) % n

dKey = [0] * 32

for i in range(0,32):
    dKey[i] = (eKey[i] ** d) % n

print("{}".format(key))
print("{}".format(eKey))
print("{}".format(dKey))
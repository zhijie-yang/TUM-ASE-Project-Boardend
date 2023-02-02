import sys
from mfrc522 import SimpleMFRC522


print(sys.argv)

text = sys.argv[1]

reader = SimpleMFRC522()
print(reader.read())
reader.write(text)
print("token changed to {}".format(text))

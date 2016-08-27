import sys
import os

path1 = sys.path[0]
path2 = os.path.normpath(os.path.join(path1, '../'))
path3 = os.path.realpath('../')

print(path3)
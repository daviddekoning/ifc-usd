import numpy as np
from pxr import Gf

matrix = np.array([
    [ 2.52575738e-14,  1.00000000e+00,  3.74708930e-30,  7.10000000e+03],
    [-1.00000000e+00,  2.52575738e-14,  3.28369430e-15,  4.80000000e+03],
    [ 3.28369430e-15, -8.66852406e-29,  1.00000000e+00, -8.13571432e-12],
    [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  1.00000000e+00]
])

# scale translation
matrix[0:3, 3] *= 0.001

# numpy matrix to Gf.Matrix4d: Gf.Matrix4d expects row-major (which means passing the python lists of rows)
gf_mat = Gf.Matrix4d([
    list(matrix[0]),
    list(matrix[1]),
    list(matrix[2]),
    list(matrix[3])
])
# Is it row major or transposed? In USD, transforms are v * M. 
# Typical math is M * v.
# If numpy represents M * v where translation is in the last column,
# then Gf.Matrix4d( ... ) expects translation in the last row!
# So we must transpose it for USD!
# Let's test.
gf_mat_transposed = Gf.Matrix4d([list(row) for row in matrix.transpose()])
print(gf_mat_transposed)


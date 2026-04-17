"""
Comprehensive NumPy Operations Program
Demonstrates various NumPy array operations and mathematical functions
"""

import numpy as np

print("=" * 60)
print("NUMPY OPERATIONS DEMONSTRATION")
print("=" * 60)

# 1. Creating Arrays
print("\n1. CREATING ARRAYS")
print("-" * 40)

# 1D Array
arr1d = np.array([1, 2, 3, 4, 5])
print(f"1D Array: {arr1d}")
print(f"Shape: {arr1d.shape}, Dtype: {arr1d.dtype}")

# 2D Array
arr2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(f"\n2D Array:\n{arr2d}")
print(f"Shape: {arr2d.shape}, Dtype: {arr2d.dtype}")

# Using arange, linspace, zeros, ones
zeros_arr = np.zeros((2, 3))
ones_arr = np.ones((2, 3))
range_arr = np.arange(0, 10, 2)
linspace_arr = np.linspace(0, 1, 5)

print(f"\nZeros array:\n{zeros_arr}")
print(f"\nOnes array:\n{ones_arr}")
print(f"\nRange array (0 to 10, step 2): {range_arr}")
print(f"Linspace array (0 to 1, 5 points): {linspace_arr}")

# 2. Array Operations
print("\n\n2. ARRAY OPERATIONS")
print("-" * 40)

a = np.array([10, 20, 30, 40, 50])
b = np.array([1, 2, 3, 4, 5])

print(f"Array A: {a}")
print(f"Array B: {b}")
print(f"A + B: {a + b}")
print(f"A - B: {a - b}")
print(f"A * B: {a * b}")
print(f"A / B: {a / b}")
print(f"A ** 2: {a ** 2}")
print(f"A % 3: {a % 3}")

# 3. Mathematical Functions
print("\n\n3. MATHEMATICAL FUNCTIONS")
print("-" * 40)

arr = np.array([1, 4, 9, 16, 25])
print(f"Array: {arr}")
print(f"Square root: {np.sqrt(arr)}")
print(f"Exponential: {np.exp(arr / 10)}")
print(f"Logarithm: {np.log(arr)}")
print(f"Sin values: {np.sin(arr / 10)}")
print(f"Cos values: {np.cos(arr / 10)}")

# 4. Aggregation Functions
print("\n\n4. AGGREGATION FUNCTIONS")
print("-" * 40)

data = np.array([5, 3, 8, 1, 9, 2, 7, 4])
print(f"Data: {data}")
print(f"Sum: {np.sum(data)}")
print(f"Mean: {np.mean(data)}")
print(f"Median: {np.median(data)}")
print(f"Standard Deviation: {np.std(data)}")
print(f"Variance: {np.var(data)}")
print(f"Min: {np.min(data)}, Max: {np.max(data)}")
print(f"Product: {np.prod(data)}")

# 5. Array Indexing and Slicing
print("\n\n5. ARRAY INDEXING AND SLICING")
print("-" * 40)

arr = np.arange(20).reshape(4, 5)
print(f"Original Array:\n{arr}")
print(f"Element at [0, 0]: {arr[0, 0]}")
print(f"Element at [2, 3]: {arr[2, 3]}")
print(f"First row: {arr[0, :]}")
print(f"First column: {arr[:, 0]}")
print(f"Subarray [1:3, 2:4]:\n{arr[1:3, 2:4]}")
print(f"Every other element in first row: {arr[0, ::2]}")

# 6. Boolean Indexing
print("\n\n6. BOOLEAN INDEXING")
print("-" * 40)

arr = np.array([1, 5, 3, 8, 2, 9, 4, 6])
print(f"Array: {arr}")
print(f"Elements > 5: {arr[arr > 5]}")
print(f"Even elements: {arr[arr % 2 == 0]}")
print(f"Multiple condition (3 < arr < 8): {arr[(arr > 3) & (arr < 8)]}")

# 7. Matrix Operations
print("\n\n7. MATRIX OPERATIONS")
print("-" * 40)

mat1 = np.array([[1, 2], [3, 4]])
mat2 = np.array([[5, 6], [7, 8]])

print(f"Matrix 1:\n{mat1}")
print(f"Matrix 2:\n{mat2}")
print(f"Matrix multiplication (dot product):\n{np.dot(mat1, mat2)}")
print(f"Element-wise multiplication:\n{mat1 * mat2}")
print(f"Transpose of Matrix 1:\n{mat1.T}")

# 8. Reshaping Arrays
print("\n\n8. RESHAPING ARRAYS")
print("-" * 40)

arr = np.arange(12)
print(f"Original array (shape {arr.shape}): {arr}")
print(f"Reshaped to (3, 4):\n{arr.reshape(3, 4)}")
print(f"Reshaped to (2, 2, 3):\n{arr.reshape(2, 2, 3)}")
print(f"Flattened: {arr.reshape(3, 4).flatten()}")
print(f"Ravel: {arr.reshape(3, 4).ravel()}")

# 9. Concatenation and Splitting
print("\n\n9. CONCATENATION AND SPLITTING")
print("-" * 40)

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
concatenated = np.concatenate([a, b])
print(f"Array A: {a}")
print(f"Array B: {b}")
print(f"Concatenated: {concatenated}")

arr = np.arange(10)
split_result = np.split(arr, 5)
print(f"Original array: {arr}")
print(f"Split into 5 parts: {split_result}")

# 10. Random Numbers
print("\n\n10. RANDOM NUMBER GENERATION")
print("-" * 40)

np.random.seed(42)  # For reproducibility
print(f"Random integers (0-10, 5 values): {np.random.randint(0, 11, 5)}")
print(f"Random floats (0-1, shape 3x3):\n{np.random.rand(3, 3)}")
print(f"Random normal distribution (mean=0, std=1, 5 values): {np.random.randn(5)}")
print(f"Random choice from array: {np.random.choice([1, 2, 3, 4, 5], 5)}")

# 11. Statistical Functions
print("\n\n11. STATISTICAL FUNCTIONS")
print("-" * 40)

data = np.random.randn(1000)
print(f"Data shape: {data.shape}")
print(f"Mean: {np.mean(data):.4f}")
print(f"Median: {np.median(data):.4f}")
print(f"Percentile 25%: {np.percentile(data, 25):.4f}")
print(f"Percentile 75%: {np.percentile(data, 75):.4f}")
print(f"Standard Deviation: {np.std(data):.4f}")
print(f"Skewness: {np.mean((data - np.mean(data))**3) / (np.std(data)**3):.4f}")

# 12. Sorting and Searching
print("\n\n12. SORTING AND SEARCHING")
print("-" * 40)

arr = np.array([3, 1, 5, 2, 8, 4, 7])
print(f"Original array: {arr}")
print(f"Sorted array: {np.sort(arr)}")
print(f"Sorted indices: {np.argsort(arr)}")
print(f"Index of maximum: {np.argmax(arr)}")
print(f"Index of minimum: {np.argmin(arr)}")
print(f"Where arr > 4: {np.where(arr > 4)}")

# 13. Unique and Count
print("\n\n13. UNIQUE VALUES AND COUNTING")
print("-" * 40)

arr = np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4])
print(f"Original array: {arr}")
print(f"Unique values: {np.unique(arr)}")
unique_vals, counts = np.unique(arr, return_counts=True)
print(f"Unique values with counts:")
for val, count in zip(unique_vals, counts):
    print(f"  {val}: {count} times")

print("\n" + "=" * 60)
print("END OF NUMPY OPERATIONS DEMONSTRATION")
print("=" * 60)

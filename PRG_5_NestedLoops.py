"""
Program 5: Nested Loops in Python
Demonstrates nested for and while loops
"""

print("=" * 50)
print("NESTED LOOPS")
print("=" * 50)

# 1. Nested for loops - simple pattern
print("\n1. Nested for loops - multiplication table:")
print("\nMultiplication Table (5x5):")
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i}x{j}={i*j:2d}", end="  ")
    print()

# 2. Nested for loops - pyramid pattern
print("\n2. Nested for loops - pyramid pattern:")
for i in range(1, 6):
    for j in range(i):
        print("*", end=" ")
    print()

# 3. Nested for loops - diamond pattern
print("\n3. Nested for loops - diamond pattern:")
n = 5
for i in range(n):
    for j in range(n - i - 1):
        print(" ", end="")
    for j in range(2 * i + 1):
        print("*", end="")
    print()

for i in range(n - 1, 0, -1):
    for j in range(n - i):
        print(" ", end="")
    for j in range(2 * i - 1):
        print("*", end="")
    print()

# 4. Nested for loops - list of lists
print("\n4. Nested for loops - processing 2D list:")
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
print("Matrix:")
for row in matrix:
    for element in row:
        print(element, end=" ")
    print()

# 5. Nested for loops - finding pairs
print("\n5. Nested for loops - finding pairs in list:")
numbers = [1, 2, 3, 4]
print("All pairs:")
for i in range(len(numbers)):
    for j in range(i + 1, len(numbers)):
        print(f"({numbers[i]}, {numbers[j]})", end="  ")
print()

# 6. Nested for loops with break
print("\n6. Nested for loops with break:")
print("Searching for number 5 in matrix:")
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
found = False
for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        print(f"Checking position [{i}][{j}] = {matrix[i][j]}")
        if matrix[i][j] == 5:
            print(f"Found 5 at position [{i}][{j}]")
            found = True
            break
    if found:
        break

# 7. Nested loops - dictionary in list
print("\n7. Nested loops - iterating dictionary in list:")
students = [
    {"name": "Alice", "scores": [85, 90, 88]},
    {"name": "Bob", "scores": [75, 80, 82]},
    {"name": "Charlie", "scores": [92, 95, 89]}
]

for student in students:
    print(f"\n{student['name']}'s scores:")
    for score in student['scores']:
        print(f"  {score}", end=" ")
print()

# 8. Triple nested loop
print("\n\n8. Triple nested loop - 3D structure:")
print("3D coordinates:")
for x in range(1, 3):
    for y in range(1, 3):
        for z in range(1, 3):
            print(f"({x},{y},{z})", end=" ")
print()

# 9. Nested while loops
print("\n9. Nested while loops:")
i = 1
while i <= 3:
    j = 1
    while j <= 3:
        print(f"({i},{j})", end=" ")
        j += 1
    print()
    i += 1

# 10. Mixed nested loops (for in while)
print("\n10. Mixed nested loops (for inside while):")
row = 1
while row <= 3:
    for col in range(1, 4):
        print(f"R{row}C{col}", end="  ")
    print()
    row += 1

# 11. Nested loops with continue
print("\n11. Nested loops with continue (skip when sum is even):")
for i in range(1, 4):
    for j in range(1, 4):
        if (i + j) % 2 == 0:
            continue
        print(f"({i},{j})", end=" ")
print()

# 12. Loop label simulation (breaking outer loop)
print("\n12. Breaking out of nested loop with flag:")
found = False
for i in range(5):
    for j in range(5):
        if i * j == 12:
            print(f"Found: {i} * {j} = 12")
            found = True
            break
    if found:
        break

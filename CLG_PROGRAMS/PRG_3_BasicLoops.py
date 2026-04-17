"""
Program 3: Basic For Loops in Python
Demonstrates different ways to use for loops
"""

print("=" * 50)
print("BASIC FOR LOOPS")
print("=" * 50)

# 1. For loop with range
print("\n1. For loop with range:")
print("Numbers from 0 to 4:")
for i in range(5):
    print(i, end=" ")
print()

# 2. For loop with start, stop, step
print("\n2. For loop with start, stop, step:")
print("Numbers from 2 to 10 with step 2:")
for i in range(2, 11, 2):
    print(i, end=" ")
print()

# 3. For loop iterating over a list
print("\n3. For loop iterating over a list:")
fruits = ["apple", "banana", "cherry", "date"]
for fruit in fruits:
    print(fruit, end=" | ")
print()

# 4. For loop with enumerate
print("\n4. For loop with enumerate (index and value):")
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# 5. For loop iterating over a string
print("\n5. For loop iterating over a string:")
word = "PYTHON"
for char in word:
    print(char, end=" ")
print()

# 6. For loop iterating over a dictionary
print("\n6. For loop iterating over a dictionary:")
student = {"name": "John", "age": 20, "grade": "A"}
for key, value in student.items():
    print(f"{key}: {value}")

# 7. For loop iterating over a tuple
print("\n7. For loop iterating over a tuple:")
coordinates = (10, 20, 30)
for coord in coordinates:
    print(f"Coordinate: {coord}")

# 8. For loop with reversed
print("\n8. For loop with reversed:")
numbers = [1, 2, 3, 4, 5]
for num in reversed(numbers):
    print(num, end=" ")
print()

# 9. For loop with zip (iterate over multiple sequences)
print("\n9. For loop with zip (multiple lists):")
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")

# 10. For loop using list comprehension style (not a loop but related)
print("\n10. Squares of numbers (using for loop):")
squares = []
for num in range(1, 6):
    squares.append(num ** 2)
print(squares)

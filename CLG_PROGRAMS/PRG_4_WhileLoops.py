"""
Program 4: While Loops in Python
Demonstrates different ways to use while loops
"""

print("=" * 50)
print("WHILE LOOPS")
print("=" * 50)

# 1. Simple while loop
print("\n1. Simple while loop - counting from 1 to 5:")
count = 1
while count <= 5:
    print(count, end=" ")
    count += 1
print()

# 2. While loop with user input simulation
print("\n2. While loop - decreasing counter:")
num = 5
while num > 0:
    print(f"Count: {num}")
    num -= 1

# 3. While loop with condition on list
print("\n3. While loop - removing items from list:")
items = ["pen", "pencil", "eraser", "notebook"]
print(f"Initial list: {items}")
while items:
    item = items.pop(0)
    print(f"Removed: {item}, Remaining: {items}")

# 4. While loop with multiple conditions
print("\n4. While loop with multiple conditions:")
x = 0
y = 10
while x < 5 and y > 5:
    print(f"x={x}, y={y}")
    x += 1
    y -= 1

# 5. While loop using flag
print("\n5. While loop using a flag:")
password = ""
correct_password = "python123"
attempts = 0
while password != correct_password and attempts < 3:
    password = input(f"Attempt {attempts + 1}: Enter password (or type 'python123'): ") if attempts == 999 else correct_password  # For demo, auto-enter
    attempts += 1
    if password == correct_password:
        print("Access granted!")
    elif attempts < 3:
        print("Wrong password. Try again.")
if attempts >= 3:
    print("Access denied - too many attempts")

# 6. While loop with break
print("\n6. While loop with break statement:")
count = 0
while count < 10:
    if count == 5:
        print(f"Breaking at {count}")
        break
    print(count, end=" ")
    count += 1
print()

# 7. While loop with continue
print("\n7. While loop with continue statement (skip even numbers):")
count = 0
while count < 10:
    count += 1
    if count % 2 == 0:
        continue
    print(count, end=" ")
print()

# 8. While True (infinite loop with break)
print("\n8. While True with break:")
counter = 0
while True:
    counter += 1
    print(f"Iteration {counter}")
    if counter >= 3:
        print("Exiting infinite loop")
        break

# 9. Nested while loops
print("\n9. Nested while loops - multiplication table (5x3):")
row = 1
while row <= 3:
    col = 1
    while col <= 5:
        print(f"{row}x{col}={row*col}", end="  ")
        col += 1
    print()
    row += 1

# 10. While loop with else
print("\n10. While loop with else (no break):")
n = 1
while n <= 3:
    print(f"n = {n}")
    n += 1
else:
    print("Loop completed normally (no break)")

print("\n11. While loop with else (with break):")
n = 1
while n <= 5:
    if n == 3:
        print(f"Breaking at n = {n}")
        break
    print(f"n = {n}")
    n += 1
else:
    print("This won't print because loop was broken")

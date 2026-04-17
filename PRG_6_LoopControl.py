"""
Program 6: Loop Control Statements in Python
Demonstrates break, continue, and pass statements
"""

print("=" * 50)
print("LOOP CONTROL STATEMENTS")
print("=" * 50)

# 1. BREAK statement in for loop
print("\n1. BREAK in for loop - stop when condition met:")
print("Numbers until 5:")
for i in range(1, 11):
    if i == 5:
        print(f"\nBreak at {i}")
        break
    print(i, end=" ")

# 2. BREAK in while loop
print("\n\n2. BREAK in while loop - exit on keyword:")
print("Counting, but break on 3:")
count = 0
while True:
    count += 1
    if count == 3:
        print(f"\nBreak triggered")
        break
    print(count, end=" ")

# 3. CONTINUE statement in for loop
print("\n\n3. CONTINUE in for loop - skip even numbers:")
print("Odd numbers only:")
for i in range(1, 11):
    if i % 2 == 0:
        continue
    print(i, end=" ")

# 4. CONTINUE in while loop
print("\n\n4. CONTINUE in while loop - skip multiples of 3:")
print("Numbers excluding multiples of 3:")
count = 0
while count < 10:
    count += 1
    if count % 3 == 0:
        continue
    print(count, end=" ")
print()

# 5. PASS statement - do nothing
print("\n5. PASS statement - empty loop body:")
print("Using pass in empty loop:")
for i in range(3):
    if i == 1:
        pass  # Do nothing here
    print(f"i = {i}")

# 6. PASS in conditional
print("\n6. PASS in if-else:")
for i in range(5):
    if i == 2:
        pass  # Placeholder for future code
    else:
        print(f"i = {i}")

# 7. Break with nested loops
print("\n\n7. BREAK in nested loop (breaks inner loop only):")
for i in range(3):
    for j in range(5):
        if j == 2:
            print(f"\nBreak at j={j}, continuing outer loop")
            break
        print(j, end=" ")

# 8. Using break to find element
print("\n\n8. BREAK to find element in list:")
numbers = [10, 20, 30, 40, 50]
search = 30
found = False
for num in numbers:
    if num == search:
        print(f"Found {search}!")
        found = True
        break
if not found:
    print(f"{search} not found")

# 9. CONTINUE to skip negative numbers
print("\n9. CONTINUE to process only positive numbers:")
values = [5, -3, 8, -1, 4, 0, -2, 6]
print("Positive values:")
for val in values:
    if val <= 0:
        continue
    print(val, end=" ")
print()

# 10. BREAK and CONTINUE together
print("\n10. BREAK and CONTINUE together:")
print("Numbers: skip even, break at 10:")
for i in range(1, 15):
    if i % 2 == 0:
        continue
    if i > 10:
        print(f"\nBreak at {i}")
        break
    print(i, end=" ")

# 11. Break with flag variable
print("\n\n11. BREAK with flag for nested loop:")
print("Find sum equals 10:")
found = False
for i in range(1, 6):
    for j in range(1, 6):
        if i + j == 10:
            print(f"{i} + {j} = 10")
            found = True
            break
    if found:
        break

# 12. CONTINUE in dictionary iteration
print("\n12. CONTINUE to skip specific keys:")
student = {"name": "John", "age": 20, "grade": "A", "email": "john@email.com"}
print("Displaying all except email:")
for key, value in student.items():
    if key == "email":
        continue
    print(f"{key}: {value}")

# 13. Complex break condition
print("\n13. BREAK on multiple conditions:")
print("Numbers where (n > 3) AND (n % 2 == 0):")
for n in range(1, 10):
    if n > 3 and n % 2 == 0:
        print(f"\nBreak at {n}")
        break
    print(n, end=" ")

# 14. Continue with calculation
print("\n\n14. CONTINUE to skip calculation:")
print("Processing numbers (skip if negative):")
for num in [5, -2, 8, -1, 3]:
    if num < 0:
        print(f"[Skipped {num}]", end=" ")
        continue
    print(f"[{num*2}]", end=" ")
print()

# 15. Pass statement as placeholder
print("\n15. PASS as placeholder for TODO:")
for i in range(3):
    if i == 0:
        pass  # TODO: Implement feature 1
    elif i == 1:
        pass  # TODO: Implement feature 2
    else:
        print(f"Processing {i}")

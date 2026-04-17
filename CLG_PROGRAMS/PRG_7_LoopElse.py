"""
Program 7: For-Else and While-Else Loops in Python
Demonstrates the else clause with loops
"""

print("=" * 50)
print("LOOP-ELSE STATEMENTS")
print("=" * 50)

# 1. For-else without break
print("\n1. For-else (loop completes normally):")
print("Loop from 1 to 4:")
for i in range(1, 5):
    print(i, end=" ")
else:
    print("\n✓ Loop completed normally")

# 2. For-else with break (else won't execute)
print("\n2. For-else with break (else skipped):")
print("Numbers until we find 3:")
for i in range(1, 10):
    print(i, end=" ")
    if i == 3:
        print("\n✗ Break encountered - else will NOT execute")
        break
else:
    print("\n✓ Loop completed normally")

# 3. While-else without break
print("\n\n3. While-else (loop completes normally):")
print("Countdown from 3:")
count = 3
while count > 0:
    print(count, end=" ")
    count -= 1
else:
    print("\n✓ Loop completed normally")

# 4. While-else with break
print("\n4. While-else with break (else skipped):")
print("Counting, break at 5:")
count = 0
while True:
    count += 1
    print(count, end=" ")
    if count == 5:
        print("\n✗ Break encountered - else will NOT execute")
        break
else:
    print("\n✓ Loop completed normally")

# 5. For-else searching for element
print("\n5. For-else - searching for element (not found):")
numbers = [1, 2, 3, 4, 5]
search = 10
print(f"Searching for {search}:")
for num in numbers:
    if num == search:
        print(f"Found {search}!")
        break
else:
    print(f"✓ Loop completed - {search} not found in list")

# 6. For-else searching for element (found)
print("\n6. For-else - searching for element (found):")
numbers = [1, 2, 3, 4, 5]
search = 3
print(f"Searching for {search}:")
for num in numbers:
    if num == search:
        print(f"Found {search}!")
        break
else:
    print(f"✓ Loop completed - {search} not found in list")

# 7. While-else validation
print("\n7. While-else - input validation (valid case):")
count = 0
valid = False
print("Checking values 1-5:")
while count < 5:
    count += 1
    if count == 3:
        print(f"Valid value found: {count}")
        break
    print(f"Checking {count}...", end=" ")
else:
    print("\n✓ All values checked - no break")

# 8. Multiple for loops with else
print("\n8. Multiple for-else loops:")
print("First loop (complete):")
for i in range(1, 3):
    print(i, end=" ")
else:
    print("✓ First loop done")

print("\nSecond loop (with break):")
for i in range(1, 5):
    if i == 2:
        break
    print(i, end=" ")
else:
    print("✓ Second loop done")

# 9. For-else with nested loop
print("\n\n9. For-else with nested loop:")
print("Finding pair that sums to 5:")
found = False
for i in range(1, 4):
    for j in range(1, 4):
        if i + j == 5:
            print(f"Found: {i} + {j} = 5")
            found = True
            break
    if found:
        break
else:
    print("✓ No pair found that sums to 5")

# 10. While-else with exit condition
print("\n10. While-else - processing items:")
items = ["apple", "banana", "cherry"]
print("Processing items:")
while items:
    item = items.pop(0)
    print(f"  - {item}")
else:
    print("✓ All items processed")

# 11. For-else with all() function
print("\n11. For-else - checking all values positive:")
numbers = [1, 2, 3, 4, 5]
print("Checking if all positive:")
for num in numbers:
    if num <= 0:
        print(f"✗ Negative value found: {num}")
        break
    print(f"  {num} ✓", end=" ")
else:
    print("\n✓ All values are positive")

# 12. For-else with all() - failed case
print("\n12. For-else - checking all values (with failure):")
numbers = [1, 2, -3, 4, 5]
print("Checking if all positive:")
for num in numbers:
    if num <= 0:
        print(f"\n✗ Negative value found: {num}")
        break
    print(f"{num} ✓", end=" ")
else:
    print("\n✓ All values are positive")

# 13. While-else with complex condition
print("\n13. While-else - login attempt:")
password = "secret"
attempts = 0
max_attempts = 3
while attempts < max_attempts:
    attempts += 1
    entered = "secret" if attempts == 1 else f"wrong{attempts}"  # Simulate input
    if entered == password:
        print(f"✓ Login successful on attempt {attempts}")
        break
    print(f"Attempt {attempts}: Wrong password")
else:
    print("✗ Login failed - max attempts reached")

# 14. For-else with range and step
print("\n14. For-else with range and step:")
print("Even numbers from 2 to 10:")
for num in range(2, 11, 2):
    print(num, end=" ")
else:
    print("\n✓ All even numbers processed")

# 15. Practical example: checking divisibility
print("\n15. Practical - checking if number is prime:")

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            print(f"\n✗ {n} is divisible by {i} - NOT PRIME")
            return False
    else:
        print(f"\n✓ {n} is PRIME")
        return True

print("Testing 17:")
for i in range(2, 17):
    if 17 % i == 0:
        print(f"✗ {17} is divisible by {i}")
        break
    print(f"  {17} % {i} ≠ 0", end=" ")
else:
    print("\n✓ 17 is PRIME")

# 16. Real-world example: searching in database
print("\n\n16. Real-world - searching in list:")
database = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]
search_id = 2
print(f"Searching for ID {search_id}:")
for record in database:
    if record["id"] == search_id:
        print(f"✓ Found: {record}")
        break
else:
    print(f"✗ ID {search_id} not found")

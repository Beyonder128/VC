def get_even_numbers(numbers):
    """
    Takes a list of numbers and returns a list of even numbers.
    
    Args:
        numbers: A list of integers
        
    Returns:
        A list containing only the even numbers from the input list
    """
    return [num for num in numbers if num % 2 == 0]


# Example usage
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_numbers = get_even_numbers(numbers)
print(even_numbers)  # Output: [2, 4, 6, 8, 10]
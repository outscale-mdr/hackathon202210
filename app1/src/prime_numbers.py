"""
Command: prime_numbers
Return a list of all the prime numbers inferior or equal to n
"""
from time import time, sleep


def prime_numbers(n):
    
    def is_prime(n):
        for i in range(60):
            sleep(1)
        if n < 2:
            return False
        for i in range(2,n):
            if (n%i) == 0:
                return False
        return True

    result = []
    for i in range(n+1):
        if is_prime(i):
            result.append(i)
    return result


"""
Command: sum_prime_numbers
Return a sum of all the prime numbers inferior or equal to n
"""
def sum_prime_numbers(n):
    return sum(prime_numbers(n))

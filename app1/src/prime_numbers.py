
from pyprimesieve import primes, primes_sum
"""
Command: prime_numbers
Return a list of all the prime numbers inferior or equal to n
"""
def prime_numbers(n):
    return primes(n)
"""
Command: sum_prime_numbers
Return a sum of all the prime numbers inferior or equal to n
"""
def sum_prime_numbers(n):
    return primes_sum(n)
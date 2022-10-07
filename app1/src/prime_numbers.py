"""
Command: prime_numbers
Return a list of all the prime numbers inferior or equal to n
"""

def prime_numbers(n):
    if n < 2:
        return []

    prime = [True for _ in range(n + 1)]

    p = 2
    while (p * p <= n):
        if (prime[p] == True):
            for i in range(p * p, n + 1, p):
                prime[i] = False
        p += 1

    all_prime_numbers = [2]
    for p in range(3, n, 2):
        if prime[p]:
            all_prime_numbers.append(p)
    return all_prime_numbers


"""
Command: sum_prime_numbers
Return a sum of all the prime numbers inferior or equal to n
"""
def sum_prime_numbers(n):
    return sum(prime_numbers(n))

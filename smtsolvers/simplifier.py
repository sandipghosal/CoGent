
from itertools import product

# Define the Boolean variables
a, b, c, d = 'a', 'b', 'c', 'd'

# Define the Boolean expression to simplify
exp = a*b*c + a*b*d + a*c*d + b*c*d


# Define the K-map function
def k_map(exp):
    # Initialize the K-map
    k_map = [[0]*2 for _ in range(2)]

    # Fill in the K-map based on the input expression
    for i, j, k, l in product(range(2), repeat=4):
        k_map[i^j][k^l] += exp(i, j, k, l)

    # Identify the groups of 1s in the K-map
    groups = []
    for i in range(2):
        for j in range(2):
            if k_map[i][j] == 1:
                group = set()
                if i > 0:
                    group.add((i-1,j))
                if i < 1:
                    group.add((i+1,j))
                if j > 0:
                    group.add((i,j-1))
                if j < 1:
                    group.add((i,j+1))
                groups.append(group)

    # Identify the essential primes and non-essential primes
    primes = []
    for group in groups:
        if len(group) == 1:
            prime = group.pop()
            primes.append(prime)
        else:
            primes.append(group)

    # Convert the primes to a simplified Boolean expression
    simplified_exp = ''
    for prime in primes:
        if isinstance(prime, tuple):
            i, j = prime
            literals = []
            if i == 0:
                literals.append(a)
            else:
                literals.append(Not(a))
            if j == 0:
                literals.append(b)
            else:
                literals.append(Not(b))
            simplified_exp += f'({"".join(literals)})'
        else:
            literals = []
            for i, j in prime:
                if i == 0:
                    literals.append(a)
                else:
                    literals.append(Not(a))
                if j == 0:
                    literals.append(b)
                else:
                    literals.append(Not(b))
            simplified_exp += f'({"+".join(literals)})'
            
    # Return the simplified Boolean expression
    return simplified_exp

# Call the K-map function on the input expression
simplified_exp = k_map(exp)

# Print the original and simplified expressions
print(f"Original expression: {exp}")
print(f"Simplified expression: {simplified_exp}")

# flake8: noqa
from langchain.prompts.prompt import PromptTemplate

template = (
    '''
Q: Olivia has $23. She bought five bagels for $3 each. How much money does she have left?

# solution in Python:


def solution():
    """Olivia has $23. She bought five bagels for $3 each. How much money does she have left?"""
    money_initial = 23
    bagels = 5
    bagel_cost = 3
    money_spent = bagels * bagel_cost
    money_left = money_initial - money_spent
    result = money_left
    return result





Q: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?

# solution in Python:


def solution():
    """Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?"""
    golf_balls_initial = 58
    golf_balls_lost_tuesday = 23
    golf_balls_lost_wednesday = 2
    golf_balls_left = golf_balls_initial - golf_balls_lost_tuesday - golf_balls_lost_wednesday
    result = golf_balls_left
    return result





Q: There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?

# solution in Python:


def solution():
    """There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?"""
    computers_initial = 9
    computers_per_day = 5
    num_days = 4  # 4 days between monday and thursday
    computers_added = computers_per_day * num_days
    computers_total = computers_initial + computers_added
    result = computers_total
    return result





Q: Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?

# solution in Python:


def solution():
    """Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?"""
    toys_initial = 5
    mom_toys = 2
    dad_toys = 2
    total_received = mom_toys + dad_toys
    total_toys = toys_initial + total_received
    result = total_toys
    return result





Q: Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?

# solution in Python:


def solution():
    """Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?"""
    jason_lollipops_initial = 20
    jason_lollipops_after = 12
    denny_lollipops = jason_lollipops_initial - jason_lollipops_after
    result = denny_lollipops
    return result





Q: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?

# solution in Python:


def solution():
    """Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?"""
    leah_chocolates = 32
    sister_chocolates = 42
    total_chocolates = leah_chocolates + sister_chocolates
    chocolates_eaten = 35
    chocolates_left = total_chocolates - chocolates_eaten
    result = chocolates_left
    return result





Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?

# solution in Python:


def solution():
    """If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?"""
    cars_initial = 3
    cars_arrived = 2
    total_cars = cars_initial + cars_arrived
    result = total_cars
    return result





Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?

# solution in Python:


def solution():
    """There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?"""
    trees_initial = 15
    trees_after = 21
    trees_added = trees_after - trees_initial
    result = trees_added
    return result





Q: In a city, it is estimated that 30% of households own an electric car. If you randomly select 10 households from this city, what is the probability that exactly 4 of those households own an electric car?

# solution in Python:


def solution():
    """In a city, it is estimated that 30% of households own an electric car. If you randomly select 10 households from this city, what is the probability that exactly 4 of those households own an electric car?"""
    import math
    p = 0.3  # probability of a household owning an electric car
    n = 10  # total number of households selected
    k = 4  # number of households owning an electric car
    result = (math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k)))
    return result





Q: Calculate the area of a circle with a radius of 7 units.

# solution in Python:

def solution():
    """Calculate the area of a circle with a radius of 7 units."""
    import math
    radius = 7
    result = math.pi * radius ** 2
    return result





Q: Solve the quadratic equation ax^2 + bx + c = 0 for a=1, b=-8, c=15.

# solution in Python:

def solution():
    """Solve the quadratic equation ax^2 + bx + c = 0 for a=1, b=-8, c=15."""
    import numpy as np
    a, b, c = 1, -8, 15
    result = np.roots([a, b, c])
    return result





Q: Simplify the algebraic expression 2*(x + 5) - 3*(x - 2) + x.

# solution in Python:

def solution():
    """Simplify the algebraic expression 2*(x + 5) - 3*(x - 2) + x."""
    import sympy as sp
    x = sp.symbols('x')
    expression = 2*(x + 5) - 3*(x - 2) + x
    result = sp.simplify(expression)
    return result





Q: A projectile is launched at an angle of 45 degrees to the horizontal with an initial speed of 20 m/s. Calculate the maximum height reached by the projectile.

# solution in Python:

def solution():
    """A projectile is launched at an angle of 45 degrees to the horizontal with an initial speed of 20 m/s. Calculate the maximum height reached by the projectile."""
    import math
    velocity = 20
    angle = math.radians(45)
    g = 9.81  # acceleration due to gravity in m/s^2
    result = (velocity ** 2) * (math.sin(angle) ** 2) / (2 * g)
    return result





Q: Evaluate the definite integral of the function f(x) = x^2 from x=0 to x=5.

# solution in Python:

def solution():
    """Evaluate the definite integral of the function f(x) = x^2 from x=0 to x=5."""
    import scipy.integrate as spi
    def f(x):
        return x**2
    result, _ = spi.quad(f, 0, 5)
    return result




Q: {question}

# solution in Python:
'''.strip()
    + "\n\n\n"
)
MATH_PROMPT = PromptTemplate(input_variables=["question"], template=template)

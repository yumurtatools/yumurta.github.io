"""
This program deals with the case that we know an incoming attack and want to defend it under the constraint that we win using minimal ressources.
"""

from scipy.optimize import minimize
import numpy as np

defense_units = {
"schwertkaempfer": {"def": {"schlag": 14, "stich": 8, "fern": 30}, "cost": 95+85},
"bogen": {"def": {"schlag": 7, "stich": 25, "fern": 13}, "cost": 120+75},
"hoplit": {"def": {"schlag": 18, "stich": 12, "fern": 7}, "cost": 75+150},
"miliz": {"def": {"schlag": 6, "stich": 8, "fern": 4}, "cost": 0},
}

attack_units = {
"reiter": 60,
"hoplit": 16,
"streitwagen": 56,
"schleuderer": 23,
}

mauerdef = [0, 3.7, 7.5, 11.4, 15.5, 19.7, 24.1, 28.5, 33.3, 38.0, 43.0, 48.1, 53.5, 59.0, 64.7, 70.5, 76.7, 82.9, 89.5, 96.2, 103.3, 110.4, 117.9, 125.6, 133.6, 141.9];
mauerdef = [1+el/100 for el in mauerdef]

n_reiter = 0
n_hopliten = 0
n_streitwagen = 0
n_schleuderer = 0

print("Attacker:")
n_reiter = int(input("Reiter: ").strip().lower())
n_hopliten = int(input("Hopliten: ").strip().lower())
n_streitwagen = int(input("Streitwagen: ").strip().lower())
n_schleuderer = int(input("Schleuderer: ").strip().lower())

# --------------------------Attack and defense boni ------------------------------
attack_bonus = (100 + int(input("What attack bonus you assume (%): ").strip().lower()))/100
defense_bonus = (100 + int(input("What defense bonus you have (%): ").strip().lower()))/100
wall_level = int(input("What is your city wall level: ").strip().lower())
# --------------------------------------------------------------------------------

A_schlag = n_reiter * attack_units["reiter"] * attack_bonus
A_stich = (n_hopliten * attack_units["hoplit"] + n_streitwagen * attack_units["streitwagen"]) * attack_bonus
A_fern = n_schleuderer * attack_units["schleuderer"] * attack_bonus
A_total = A_schlag + A_stich + A_fern
A = {"schlag": A_schlag, "stich": A_stich, "fern": A_fern}
print(A)

p_A_schlag = A_schlag/A_total
p_A_stich = A_stich/A_total
p_A_fern = A_fern/A_total
p = {"schlag": p_A_schlag, "stich": p_A_stich, "fern": p_A_fern}

# cost
# Schwertkaempfer, Hoplit, Bogen
c = [defense_units["schwertkaempfer"]["cost"], defense_units["hoplit"]["cost"], defense_units["bogen"]["cost"]]

# Bounds
n_schwertkaempfer = int(input("What is total amount of swordmen you have: ").strip().lower()) # Maximal value Schwertkaempfer # X1
n_hopliten4def = int(input("What is total amount of hoplits you have: ").strip().lower()) # Maximal value Hoplit # X2
n_bogen = int(input("What is total amount of archers you have: ").strip().lower()) # Bogen
n_militia = int(input("What is total amount of militia you have: ").strip().lower()) # Bogen
bounds = [(0,n_schwertkaempfer), (0,n_hopliten4def), (0,n_bogen)]


# ------------------------- Constraints ------------------------------
# L needs to be smaller than one
def ineq_constraint_type(x, n_militia, at):
    # Schwertkaempfer, Hoplit, Bogen
    u = defense_units["schwertkaempfer"]["def"][at]
    v = defense_units["hoplit"]["def"][at]
    w = defense_units["bogen"]["def"][at]
    m = defense_units["miliz"]["def"][at]
    V = ( x[0]*u + x[1]*v + x[2]*w + n_militia*m + 10*(wall_level+1))  * defense_bonus * mauerdef[wall_level]
    L = ( A[at]/ V )**1.2
    return 1 - L # >=0 is the default
    
def ineq_constraint_schlag(x):
    y = np.array([x[0] * p["schlag"], x[1] * p["schlag"], x[2] * p["schlag"]])
    if p["schlag"] > 0:
        return ineq_constraint_type(y, n_militia*p["schlag"], "schlag")
    else:
        return 1
    
def ineq_constraint_stich(x):
    y = np.array([x[0] * p["stich"], x[1] * p["stich"], x[2] * p["stich"]])
    if p["stich"] > 0:
        return ineq_constraint_type(y, n_militia*p["stich"], "stich")
    else:
        return 1

def ineq_constraint_fern(x):
    y = np.array([x[0] * p["fern"], x[1] * p["fern"], x[2] * p["fern"]])
    if p["fern"] > 0:
        return ineq_constraint_type(y, n_militia*p["fern"], "fern")
    else:
        return 1
    
# Only add constraints for attack types that are actually present
constraints = []
if p["schlag"] > 0:
    constraints.append({'type': 'ineq', 'fun': ineq_constraint_schlag})
if p["stich"] > 0:
    constraints.append({'type': 'ineq', 'fun': ineq_constraint_stich})
if p["fern"] > 0:
    constraints.append({'type': 'ineq', 'fun': ineq_constraint_fern})
# ---------------------------------------------------------------------
def objective_type(x, at):
    u = defense_units["schwertkaempfer"]["def"][at]
    v = defense_units["hoplit"]["def"][at]
    w = defense_units["bogen"]["def"][at]
    m = defense_units["miliz"]["def"][at]
    
    V = (x[0]*u + x[1]*v + x[2]*w + n_militia*m + 10*(wall_level+1) ) * p[at] * defense_bonus * mauerdef[wall_level] # X4 is militia and remains fixed.
    L = (A[at]/V )**1.2
    return L * (x[0]*c[0] + x[1]*c[1] + x[2]*c[2]) * p[at]
    
def objective(x):
    ret = 0
    for at in ["schlag","stich", "fern"]:
        if p[at] > 0:
            ret += objective_type(x, at)
    return ret
# ---------------------------------------------------------------------

print(objective([3,4,5]))

# schwertkaempfer, hoplit, bogen
x0 = [n_schwertkaempfer, n_hopliten4def, n_bogen]
result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
print(result)
# print(result.x)
print(5*"------------")
print("You are getting an attack consisting of: ")
print(f"Reiter: {n_reiter}")
print(f"Hopliten: {n_hopliten}")
print(f"Streitwagen: {n_streitwagen}")
print(f"Schleuderer: {n_schleuderer}")
print("You have the following units in town: ")
print(f"Schwertkaempfer: {n_schwertkaempfer}")
print(f"Hopliten: {n_hopliten4def}")
print(f"Bogenschuetzen: {n_bogen}")
print(f"Militia: {n_militia}")
print("You should keep the following units in the town:")
print(f"Schwertkaempfer: {result.x[0]}")
print(f"Hopliten: {result.x[1]}")
print(f"Bogenschuetzen: {result.x[2]}")

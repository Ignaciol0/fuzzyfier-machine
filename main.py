from MFIS_Classes import *
from MFIS_Read_Functions import *
import numpy as np
import skfuzzy as fuzz

def fuzzify(input, fuzzySetsDict):
    """Fuzzify the input using the fuzzy sets"""
    fuzzified = {}
    for var, value in input:
        # Find the fuzzy set for the variable
        set_key = next(key for key in fuzzySetsDict if key.startswith(var + "="))
        set = fuzzySetsDict[set_key]
        # Calculate the membership degree for the value
        set.memDegree = fuzz.interp_membership(set.x, set.y, value)
        fuzzified[set.var + "=" + set.label] = set.memDegree
    return fuzzified

def applyRules(rules, fuzzified):
    """Apply the rules to the fuzzified input"""
    results = {}
    for rule in rules:
        results[rule.consequent] = min([fuzzified[label] for label in rule.antecedent])
    return results

def defuzzify(results, fuzzySets):
    """Defuzzify the results using the centroid method"""
    defuzzified = {}
    for var, value in results.items():
        set = fuzzySets[var]
        x = set.x
        trapmf = set.y
        defuzzified[var] = fuzz.defuzz(x, trapmf, 'centroid')
    return defuzzified

# Read the fuzzy sets and the rules from the files
fuzzySets = readFuzzySetsFile('InputVarSets.txt')
rules = readRulesFile()
applications = readApplicationsFile()

# For each application, fuzzify the input, apply the rules, and defuzzify the results
for app in applications:
    # Fuzzify the input
    fuzzified = fuzzify(app.data, fuzzySets)

    # Apply the rules
    results = applyRules(rules, fuzzified)

    # Defuzzify the results
    defuzzified = defuzzify(results, fuzzySets)

    # Print the defuzzified results
    print(defuzzified)
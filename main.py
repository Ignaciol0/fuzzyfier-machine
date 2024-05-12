from MFIS_Classes import *
from MFIS_Read_Functions import *
import numpy as np
import skfuzzy as fuzz

def fuzzify(input, fuzzySetsDict):
    """Fuzzify the input using the fuzzy sets"""
    fuzzified = {}
    for var, value in input:
        # Find the fuzzy set for the variable
        set_key = [key for key in fuzzySetsDict if key.startswith(var + "=")]
        for degre in set_key:
            fuzzy_set = fuzzySetsDict[degre]
            # Calculate the membership degree for the value
            fuzzy_set.memDegree = fuzz.interp_membership(fuzzy_set.x, fuzzy_set.y, value)
            fuzzified[fuzzy_set.var + "=" + fuzzy_set.label] = fuzzy_set.memDegree
    return fuzzified

def applyRules(rules, fuzzified):
    """Apply the rules to the fuzzified input"""
    results = {}
    risk_high, risk_med, risk_low = [],[],[]
    value_low, value_high, value_med = None, None, None
    risk_fuzzys = readFuzzySetsFile('Risks.txt')

    # Find the max value for each variable
    for rule in rules:
        value = min([fuzzified[label] for label in rule.antecedent])
        risk_fuzzy = risk_fuzzys[rule.consequent]
        new_y = list(np.full(100,value))
        risk_fuzzy.y = new_y
        if risk_fuzzy.label == 'LowR':
            if value_low == None or value > value_low:
                value_low = value
        elif risk_fuzzy.label == 'MediumR':
            if value_med == None or value > value_med:
                value_med = value
        elif risk_fuzzy.label == 'HighR':
            if value_high == None or value > value_high:
                value_high = value  

    # Find the last result of the fuzzy with the clip min.
    for risk_key in risk_fuzzys.keys():
        fuzzy = risk_fuzzys[risk_key]
        if risk_key == 'Risk=LowR':
            fuzzy.y = list(np.full(100,value_low))
        elif risk_key == 'Risk=MediumR':
            fuzzy.y = list(np.full(100,value_med))
        elif risk_key == 'Risk=HighR':
            fuzzy.y = list(np.full(100,value_high))
        previous_value_list = np.zeros(100)
        for index in range(len(fuzzy.y)):
            previous_value_list[index] = max(previous_value_list[index],fuzzy.y[index])
        risk_fuzzys[risk_key].y = previous_value_list

    return risk_fuzzys

def defuzzify(results, fuzzySets):
    """Defuzzify the results using the centroid method"""
    defuzzified = {}
    for fuzzy_key in results.keys():
        fuzzy_set = results[fuzzy_key]
        x = fuzzy_set.x
        trapmf = fuzzy_set.y
        defuzzified[fuzzy_key] = fuzz.defuzz(x, trapmf, 'centroid')
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
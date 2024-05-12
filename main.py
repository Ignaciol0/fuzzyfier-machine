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
    value_low, value_high, value_med = None, None, None
    risk_fuzzys = readFuzzySetsFile('Risks.txt')
    for rule in rules:
        value = min([fuzzified[label] for label in rule.antecedent])
        risk_fuzzy = risk_fuzzys[rule.consequent]
        new_y = []
        # We perform clip the minimum to the risk
        for y in risk_fuzzy.y:
            new_y += [min(y,value)]
        risk_fuzzy.y = new_y
        if risk_fuzzy.label == 'LowR':
            risk_low += [risk_fuzzy]
        elif risk_fuzzy.label == 'MediumR':
            risk_med += [risk_fuzzy]
        elif risk_fuzzy.label == 'HighR':
            if value_high == None or value > value_high:
                value_high = value  

    return f"Low Risk: {round(value_low,2)}, Medium Risk: {round(value_med,2)}, High Risk: {round(value_high,2)}"
    

# Read the fuzzy sets and the rules from the files
fuzzySets = readFuzzySetsFile('InputVarSets.txt')
rules = readRulesFile()
applications = readApplicationsFile()
text = ''

# For each application, fuzzify the input, apply the rules, and defuzzify the results
for app in applications:
    # Fuzzify the input
    fuzzified = fuzzify(app.data, fuzzySets)

    # Apply the rules
    results = applyRules(rules, fuzzified)

    # Print the results
    text += f"Applicant {applications.index(app)+1}: {results}\n"
with open("Results.txt",'w') as f:
    f.write(text)

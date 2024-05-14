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
        if rule.consequent == 'Risk=LowR':
            if value_low == None or value > value_low:
                value_low = value  
        elif rule.consequent == 'Risk=MediumR':
            if value_med == None or value > value_med:
                value_med = value  
        elif rule.consequent == 'Risk=HighR':
            if value_high == None or value > value_high:
                value_high = value  
    
    for risky_key in risk_fuzzys.keys():
        risk_fuzzy = risk_fuzzys[risky_key]
        value = 0
        if risky_key == 'Risk=HighR':
            value = value_high
        elif risky_key == 'Risk=LowR':
            value = value_low
        elif risky_key == 'Risk=MediumR':
            value = value_med
        new_y = list(np.zeros(100))
        for index in range(len(risk_fuzzy.y)):
            new_y[index] = min(value,risk_fuzzy.y[index])
        risk_fuzzy.y = new_y
    
    fuzzy_high = risk_fuzzy['Risk=HighR']
    fuzzy_low = risk_fuzzy['Risk=LowR']
    fuzzy_med = risk_fuzzy['Risk=MediumR']
    new_y = list(np.zeros(100))
    for index in range(len(fuzzy_high.y)):
        new_y[index] = max(fuzzy_high[index],fuzzy_low[index],fuzzy_med[index])
    fuzzy = fuzzy_low
    fuzzy.y = new_y
    return fuzzy
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

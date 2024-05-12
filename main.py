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
            risk_high += [risk_fuzzy]
    risks = {'Risk=LowR':risk_low,'Risk=MediumR': risk_med,'Risk=HighR': risk_high}
    print(risks)
    for risk_key in risks.keys():
        risk = risks[risk_key]
        previous_value_list = np.zeros(100)
        for fuzzy in risk:
            for y in fuzzy.y:
                index = fuzzy.y.index(y)
                previous_value_list[index] = max(previous_value_list[index],y)
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

import io
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-i','--input', help='the file with matching patterns that needs to be verified',
                    type=str,required=True)
parser.add_argument('-b','--baseline', help='the file with correct approach (baseline)',type=str, 
                    required=True)

args = parser.parse_args()
print(args.input)
print(args.baseline)

baseline_output = []
test_output = []


with open(args.baseline,'r') as f:
    for line in f:

        line = line.strip()
        line = line.strip('[]')

        pattern = sorted(line.split(','))

        my_hash = hash(frozenset(pattern))

        baseline_output.append(my_hash)


match_baseline = True
with open(args.input, 'r') as f:
    for line in f:

        line = line.strip()
        line = line.strip('[]')

        pattern = sorted(line.split(','))

        my_hash = hash(frozenset(pattern))

        #if my_hash in test_output:
        #    print("duplicate detected: pattern " + str(pattern))
        
        if my_hash not in baseline_output:
            print("Pattern not found in baseline: " + str(pattern))
            match_baseline = False

        test_output.append(my_hash)
        
if len(test_output) > len(baseline_output):
    match_baseline = False

if match_baseline:
    print("The test output is same as the baseline (%d matches)" % len(baseline_output))
else:
    print("The test output is not same as the baseline")
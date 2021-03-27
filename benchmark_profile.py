import cProfile
import argparse
import main

import pstats


parser = argparse.ArgumentParser()
parser.add_argument('-a', '--algorithm', help='algorithm to run', default='clique', type=str)
parser.add_argument('-g', '--graph', help='choice of graph', default='er', type=str)
parser.add_argument('-m', '--mode', help='mode to run (static, dynamic, both)', default='both', type=str)
parser.add_argument('-p', '--plot', help='plot graph', action='store_true')
parser.set_defaults(plot=False)
parser.add_argument('-n', '--vertices', help='number of vertices', default=1000, type=int)
parser.add_argument('-e', '--edge_prob', help='probability of an edge', default=0.02, type=float)
parser.add_argument('-u', '--updates', help='number of updates', type=int)
parser.add_argument('--max', help='maximum pattern size', type=int)
parser.add_argument('--seed', help='random graph generator seed', default=42, type=int)
parser.add_argument('-f', '--file', help='output file for patterns', default=None, type=str)
parser.add_argument('--log_patterns', help='log found patterns', action='store_true')
parser.set_defaults(log_patterns=False)
parser.add_argument('--canonical', help='canonicalize patterns à la Arabesque before outputting', action='store_true')
parser.set_defaults(canonical=False)
parser.add_argument('--sort', help='sort patterns before outputting', action='store_true')
parser.set_defaults(sort=False)
parser.add_argument('-r', '--reset', help='reset graph', action='store_true')
parser.set_defaults(reset=False)
parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
parser.set_defaults(verbose=False)
args = parser.parse_args()

cProfile.run('main.main(args)', 'benchmark_data')

p = pstats.Stats('benchmark_data')
p.sort_stats('cumulative').print_stats(20)


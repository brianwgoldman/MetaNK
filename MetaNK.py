#!/usr/bin/python
import random

# Linkage Models
def NearestNeighbor(N, K):
    return [[j % N for j in range(i, (i + K + 1))] for i in range(N)]

def Unrestricted(N, K):
    options = set(range(N))
    return [[i] + random.sample(options - set([i]), K) for i in range(N)]



def Separable(N, K):
    def chunks(data, size):
        start = 0
        while start < len(data):
            step = size + 1 if (len(data) - start) % size else size
            yield data[start: start + step]
            start += step
    options = range(N)
    parts = []
    for chunk in chunks(options, 2 * K):
        parts += [[i] + random.sample(set(chunk) - set([i]), min(K, len(chunk) - 1)) for i in chunk]
    return parts

linkages = [NearestNeighbor, Unrestricted, Separable]

# Rearrangement Methods
def Scatter(N, epistasis):
    ordering = range(N)
    random.shuffle(ordering)
    return [[ordering[x] for x in group] for group in epistasis]

def NoChange(N, epistasis):
    return epistasis

rearrangement = [Scatter, NoChange]

# Value generators
def Uniform():
    return random.random()

def Normal():
    result = -1
    while result < 0 or result > 1:
        result = random.gauss(0.5, 0.2)
    return result

def Scaled():
    return random.uniform(0.54, 1) ** 3

rngs = [Uniform, Normal, Scaled]

# Number of unique values
def TwoValues(RNG, K):
    options = [RNG(), RNG()]
    def TwoValues_Inner():
        return random.choice(options)
    return TwoValues_Inner

def PowKValues(RNG, K):
    options = [RNG() for _ in range(2 << K)]
    def PowKValues_Inner():
        return random.choice(options)
    return PowKValues_Inner

def AllUnique(RNG, K):
    return RNG

value_count = [TwoValues, PowKValues, AllUnique]

def Create_Class():
    epistasis = random.choice(linkages)
    arrangement = random.choice(rearrangement)
    number_maker = random.choice(rngs)
    value_levels = random.choice(value_count)
    N = random.randint(50, 500)
    eval_const = random.choice([1, 4, 16])
    K = random.randint(1, 5)
    return N, K, eval_const, epistasis, arrangement, number_maker, value_levels 

def Create_Instance(N, K, eval_const, epistasis, arrangement, number_maker, value_levels):
    adjacency = arrangement(N, epistasis(N, K))
    rng = value_levels(number_maker, K)
    table = [[rng() for _ in range(2 << K)] for _ in range(N)]
    result = "{:03d} {:06d} {:d}\n".format(N, N * N / eval_const, K)
    for links, fits in zip(adjacency, table):
        result += " ".join(["{:03d}".format(l) for l in links])
        result += " " + " ".join(["{:.4f}".format(f) for f in fits]) + '\n'
    return result


def safe_make(directory):
    try:
        makedirs(directory)
    except OSError:
        pass

if __name__ == "__main__":
    import argparse
    import sys
    from os import makedirs, path
    parser = argparse.ArgumentParser(description="MetaNK Generator")
    parser.add_argument('-seed', dest='seed', type=int, default=None,
                        help='Seed for the random number generator')
    parser.add_argument('-folder', dest='folder', type=str, default="nk_out",
                        help='Name to use when creating the output folder')
    parser.add_argument('-training', dest='training', type=int, default=500,
                        help='The number of training instances to generate')
    parser.add_argument('-testing', dest='testing', type=int, default=50,
                        help='The number of testing instances to generate')
    
    args = parser.parse_args()
    
    # Set up folder structure
    training_folder = path.join(args.folder, "training")
    testing_folder = path.join(args.folder, "testing")
    results_folder = path.join(args.folder, "results")

    safe_make(args.folder)
    safe_make(training_folder)
    safe_make(testing_folder)
    safe_make(results_folder)
    
    # Set up random seed
    if args.seed == None:
        args.seed = random.randint(0, sys.maxint)
    random.seed(args.seed)
    
    chosen = Create_Class()
    with open(path.join(args.folder, "meta.txt"), "w") as f:
        f.write(" ".join(map(str, chosen)) + " " + str(args.seed) + "\n")

    training_files = []
    for instance in range(args.training):
        relative = path.join("training", "{:05d}.txt".format(instance))
        with open(path.join(args.folder, relative), "w") as f:
            f.write(Create_Instance(*chosen))
        training_files.append(relative)

    with open(path.join(args.folder, "trainingFiles.txt"), "w") as f:
        f.write("{0} {1}\n".format(args.training / 10, args.training))
        f.write("\n".join(training_files) + "\n")

    testing_files = []
    for instance in range(args.testing):
        relative = path.join("testing", "{:05d}.txt".format(instance))
        with open(path.join(args.folder, relative), "w") as f:
            f.write(Create_Instance(*chosen))
        testing_files.append(relative)

    with open(path.join(args.folder, "testingFiles.txt"), "w") as f:
        f.write("{0}\n".format(args.testing))
        f.write("\n".join(testing_files) + "\n")

#!/usr/bin/python3
import random
import math

'''
This section defines the different variable interaction models
'''


def NearestNeighbor(N, K):
    # Each variable depends on the K following
    return [[j % N for j in range(i, (i + K + 1))] for i in range(N)]


def Unrestricted(N, K):
    # Each variable depends on k random others
    options = set(range(N))
    return [[i] + random.sample(options - set([i]), K) for i in range(N)]


def Separable(N, K):
    # The genome is broken into 2 * K sized blocks, with each block using
    # Unrestricted
    def chunks(data, size):
        start = 0
        while start < len(data):
            step = size + 1 if (len(data) - start) % size else size
            yield data[start: start + step]
            start += step
    options = list(range(N))
    parts = []
    for chunk in chunks(options, 2 * K):
        parts += [[i] + random.sample(set(chunk) - set([i]),
                                      min(K, len(chunk) - 1)) for i in chunk]
    return parts


def Mesh(N, K):
    # Creates a K+1 dimensional hyper cube

    # Find the smallest hyper-cube with K+1 dimensions that has at least N
    # vertices
    width = int(math.ceil(N ** (1 / (K + 1.0))))

    def to_coordinates(value):
        # Convert an integer index into coordinates in the mesh
        coord = []
        for _ in range(K + 1):
            coord.append(value % width)
            value = int(value // width)
        return coord

    def from_coordinates(coord):
        # Convert coordinates in the mesh into an integer index
        value = 0
        for c in reversed(coord):
            value *= width
            value += c
        return value
    edges = []
    for i in range(N):
        coord = to_coordinates(i)
        for dimension in range(K + 1):
            # Create an edge going out in each dimension
            neighbor_coord = list(coord)
            neighbor_coord[dimension] += 1
            neighbor_index = from_coordinates(neighbor_coord)
            if neighbor_index >= N or neighbor_coord[dimension] >= width:
                # Toroidal
                neighbor_coord[dimension] = 0
                neighbor_index = from_coordinates(neighbor_coord)
            edges.append([i, neighbor_index])
    return edges


def SAT_like(N, K):
    # Creates 4.27 * N sets of K+1 random variables
    options = list(range(N))
    return [random.sample(options, K + 1) for i in range(int(4.27 * N))]

linkages = [NearestNeighbor, Unrestricted, Separable, Mesh, SAT_like]

'''
This section defines different rearrangement methods for the genome
'''


def Scatter(N, epistasis):
    # Randomly shuffle the genome ordering
    ordering = list(range(N))
    random.shuffle(ordering)
    return [[ordering[x] for x in group] for group in epistasis]


def NoChange(N, epistasis):
    # Leave the ordering as is
    return epistasis

rearrangement = [Scatter, NoChange]

'''
This section defines different methods for generating table values.
'''


def Uniform():
    # Generate a number uniformly at random (0, 1)
    return random.random()


def Normal():
    # Generate a normally distributed number, bound between 0 and 1.
    result = -1
    while result < 0 or result > 1:
        result = random.gauss(0.5, 0.2)
    return result


def Scaled():
    # Generate numbers biased toward small, but with a similar average
    # as Uniform and Normal
    return random.uniform(0.54, 1) ** 3

rngs = [Uniform, Normal, Scaled]

'''
This section defines different methods for controlling how many unique
values appear in each table. Fewer unique values means more plateaus.
'''


def TwoValues(RNG, variables_per_row):
    # Exactly 2 unique values will appear in the fitness table
    options = [RNG(), RNG()]

    def TwoValues_Inner():
        return random.choice(options)
    return TwoValues_Inner


def PowKValues(RNG, variables_per_row):
    # This method creates 2^k values to match the 2^k entries per row.
    options = [RNG() for _ in range(1 << variables_per_row)]

    def PowKValues_Inner():
        return random.choice(options)
    return PowKValues_Inner


def AllUnique(RNG, variables_per_row):
    # Allows every single entry in the table to be unique
    return RNG

value_count = [TwoValues, PowKValues, AllUnique]

'''
This section uses the previous tools to create problems.
'''


def Create_Class():
    # Determine all of the settings for this problem class
    epistasis = random.choice(linkages)
    arrangement = random.choice(rearrangement)
    number_maker = random.choice(rngs)
    value_levels = random.choice(value_count)
    N = random.randint(50, 300)
    eval_const = random.choice([1, 4, 16])
    K = random.randint(1, 5)
    return N, K, eval_const, epistasis, arrangement, number_maker, value_levels


def Create_Instance(N, K, eval_const, epistasis, arrangement, number_maker, value_levels):
    # Generate an instance from a class description
    adjacency = arrangement(N, epistasis(N, K))
    rows = len(adjacency)
    variables_per_row = len(adjacency[0])
    rng = value_levels(number_maker, variables_per_row)
    table = [[rng() for _ in range(1 << variables_per_row)]
             for _ in range(rows)]
    result = "{:03d} {:06d} {:d} {:d}\n".format(
        N, 2 * N * N // eval_const, variables_per_row, rows)
    for links, fits in zip(adjacency, table):
        result += " ".join(["{:03d}".format(l) for l in links])
        result += " " + " ".join(["{:.4f}".format(f) for f in fits]) + '\n'
    return result


def safe_make(directory):
    # if the directory doesn't exist, create it.
    try:
        makedirs(directory)
    except OSError:
        pass

if __name__ == "__main__":
    import argparse
    import sys
    from os import makedirs, path
    # Set up command line interface
    parser = argparse.ArgumentParser(description="Problem Class Generator")
    parser.add_argument('-seed', dest='seed', type=int, default=None,
                        help='Seed for the random number generator')
    parser.add_argument('-folder', dest='folder', type=str, default="problems",
                        help='Name to use when creating the output folder')
    parser.add_argument('-training', dest='training', type=int, default=200,
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

    with open(path.join(results_folder, ".gitignore"), "w") as f:
        f.write("*.json\n")

    # Set up random seed
    if args.seed == None:
        args.seed = random.randint(0, sys.maxsize)
    random.seed(args.seed)

    # Configure the problem class
    chosen = Create_Class()
    with open(path.join(args.folder, "meta.txt"), "w") as f:
        f.write(" ".join(map(str, chosen)) + " " + str(args.seed) + "\n")

    # Generate the problem instances
    for basename, number in [("training", args.training), ("testing", args.testing)]:
        filenames = []
        for instance in range(number):
            relative = path.join(basename, "{:05d}.txt".format(instance))
            with open(path.join(args.folder, relative), "w") as f:
                f.write(Create_Instance(*chosen))
            filenames.append(relative)

        with open(path.join(args.folder, basename + "Files.txt"), "w") as f:
            f.write("{0}\n".format(number))
            f.write("\n".join(filenames) + "\n")

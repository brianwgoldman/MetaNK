#!/usr/bin/env python3
'''
To perform overall ranking, we convert the results of each instance into
"ballots", which are then combined using the Schulze Voting method.

Competitor A is ranked higher for an instance than Competitor B if:
 * Found higher quality solution
 * Found the same quality solution earlier in its search (more evaluations remaining)

Given a collection of ballots, Schulze compares competitors pairwise to see how often A > B.
If A wins all of its pairwise matchups more than 50% of the time, A is the winner. If
no such competitor exists, Schulze rewards the one closest to doing so.

We also include "average rank" information for diagnostic purposes only. That information
has no say in how the final ranking is determined.
'''
import json
import sys
from collections import defaultdict


def schulze(ballots):
    '''
    Schulze Voting Scheme
    Input is an iterable of ballots
    All ballots must have the same candidates
    Each ballot must have all candidates

    A ballot is a list of candidates, with candidates occurring earlier
    in the list being preferred over candidates occurring later in the list.
    Each candidate may only appear once per ballot.
    Example Ballot: ['Pete', 'Frank', 'Oliver', 'Bob']
    This represents the opinion that Pete > Frank > Oliver > Bob
    This implementation comes from https://github.com/siggame/siggame-vote/blob/master/vote/schulze.py
    which is based on # https://en.wikipedia.org/wiki/Schulze_method
    '''
    candidates = ballots[0]
    # d is the pairwise preference grid. d is a stupid name
    d = {(i, j): 0 for i in candidates for j in candidates}
    for b in ballots:
        for (x, y) in d.keys():
            if b.index(x) < b.index(y):
                d[(x, y)] += 1

    # p is the strengths of the strongest paths grid. p is also a stupid name
    p = dict()
    for i in candidates:
        for j in candidates:
            if i != j:
                if d[(i, j)] > d[(j, i)]:
                    p[(i, j)] = d[(i, j)]
                else:
                    p[(i, j)] = 0
    for i in candidates:
        for j in candidates:
            if i != j:
                for k in candidates:
                    if i != k and j != k:
                        p[(j, k)] = max(p[(j, k)],
                                        min(p[(j, i)], p[(i, k)]))

    # For each candidate, count how many times they lose a matchup.
    # That is their rank
    ranks = {}
    for i in candidates:
        ranks[i] = 1
        for j in candidates:
            if i != j:
                if p[(i, j)] < p[(j, i)]:
                    ranks[i] += 1
    return sorted(ranks.keys(), key=ranks.get)


def test_schulze():
    ''' Verify that our implementation produces the same results as the wiki page '''
    ballots = [['A', 'C', 'B', 'E', 'D']] * 5 + \
              [['A', 'D', 'E', 'C', 'B']] * 5 + \
              [['B', 'E', 'D', 'A', 'C']] * 8 + \
              [['C', 'A', 'B', 'E', 'D']] * 3 + \
              [['C', 'A', 'E', 'B', 'D']] * 7 + \
              [['C', 'B', 'A', 'D', 'E']] * 2 + \
              [['D', 'C', 'E', 'B', 'A']] * 7 + \
              [['E', 'B', 'A', 'D', 'C']] * 8
    assert schulze(ballots) == ['E', 'A', 'C', 'B', 'D']


def average_rank(ballots):
    ''' Converts each ballot to a rank (1 through C) and averages that for each candidate '''
    candidate_to_ranks = defaultdict(list)
    for ballot in ballots:
        for rank, candidate in enumerate(ballot):
            candidate_to_ranks[candidate].append(rank + 1)
    paired = [(sum(value) / len(value), key)
              for key, value in candidate_to_ranks.items()]
    return sorted(paired)


def convert_problem_to_ballots(problem_results):
    ''' Given all of the jsons for a problem, return a ballot for each test instance '''
    grouped_by_instance = defaultdict(list)
    for competitor_key, results in problem_results.items():
        for i, result in enumerate(results['testingResults']):
            sortable = (result['bestValue'],
                        result['remainingEvaluationsWhenBestReached'], competitor_key)
            grouped_by_instance[i].append(sortable)

    ballots = []
    for instance_results in grouped_by_instance.values():
        instance_results.sort(reverse=True)
        ballot = [s[-1] for s in instance_results]
        ballots.append(ballot)
    return ballots

if __name__ == "__main__":
    print("""
          This program assumes either 1) You only give it results from 1
          training category or 2) You want to do cross category comparison
          """)
    test_schulze()  # Performs a sanity check
    # Gather together each problem's results
    grouped_by_problem = defaultdict(dict)
    for filename in sys.argv[1:]:
        with open(filename.strip(), 'r') as f:
            result = json.load(f)
        problem = result['problemClassName']
        # Combine name and language for each competitor
        competitor_key = result['competitorName'] + \
            "-" + result['competitorLanguage']
        grouped_by_problem[problem][competitor_key] = result

    combined_ballots = []
    for problem, results in grouped_by_problem.items():
        problem_ballots = convert_problem_to_ballots(results)
        print(problem)
        for competitor in schulze(problem_ballots):
            print('\t', competitor)
        combined_ballots += problem_ballots

    print("Overall")
    for competitor in schulze(combined_ballots):
        print('\t', competitor)

    print("Average Rank")
    for rank, competitor in average_rank(combined_ballots):
        print('\t', rank, competitor)

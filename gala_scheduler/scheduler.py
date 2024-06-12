#!/usr/bin/env python3
import argparse
import copy
import itertools
import math
import random

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *args, **_: args


class Score:
    def __init__(self, mixes, repeats):
        self.mixes = mixes
        self.repeats = repeats

    def __int__(self):
        return self.mixes * 3 + self.repeats * 1

    def __lt__(self, rhs): return int(self) < rhs
    def __le__(self, rhs): return int(self) <= rhs
    def __eq__(self, rhs): return int(self) == rhs
    def __ge__(self, rhs): return int(self) >= rhs
    def __gt__(self, rhs): return int(self) > rhs

    def __add__(self, rhs):
        return Score(self.mixes + rhs.mixes, self.repeats + rhs.repeats)

    def __str__(self):
        return f"{int(self)} [{self.mixes} / {self.repeats}]"


def score(act):
    mixes, repeats = 0, 0
    for a, b in itertools.pairwise(act):
        mixes += len(set(a[2]).intersection(b[2]))
    for i in range(len(act)-2):
        if act[i][0] == act[min(len(act)-1,i+2)][0]:
            repeats += 1
            if act[i][0] == act[min(len(act)-1,i+4)][0]:
                repeats += 5
    return Score(mixes, repeats)


def score2(perm):
    mid = len(perm) // 2
    sc1 = score(perm[:mid])
    sc2 = score(perm[mid:])
    return sc1 + sc2


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', help='input file')
    args = arg_parser.parse_args()

    with open(args.file) as f:
        data = [d.strip().replace(" ", "") for d in f.readlines() if d != "\n"]
    parsed = []
    for d in data:
        dance = d.split(":")[0].split("-")[0]
        act = d.split(":")[0].split("-")[1]
        people = d.split(":")[1].split(",")
        parsed.append((dance, act, people))
    random.shuffle(parsed)

    people = set(itertools.chain(*[p[2] for p in parsed]))
    acts = {a: [b for b in parsed if b[1] == a] for a in ("1", "2", "X")}
    print(f"Előadások száma: {len(parsed)}")
    print(f"Táncosok száma: {len(people)}")
    print(f"1. felvonás fix: {len(acts['1'])}")
    print(f"2. felvonás fix: {len(acts['2'])}")
    print()

    best = heuristic(acts)
    print_schedule(best)


def print_schedule(sched):
    mid = len(sched) // 2
    for i, act in enumerate([sched[:mid], sched[mid:]]):
        print()
        print(f"{i+1}. felvonás:")
        print(f"------------")
        for i in range(len(act)-1):
            a, b, c = act[i], act[i+1], act[min(len(act)-1, i+2)]
            rep = "*" if a[0] == c[0] else " "
            print(f"{rep} {a[0]}:".ljust(20), f"{', '.join(a[2])}")
            mix = set(a[2]).intersection(b[2])
            for m in mix:
                print(f"    -> {m}")
        print(f"  {b[0]}:".ljust(20), f"{', '.join(b[2])}")
    print()
    print(f"Végső pontszám: {score2(sched)}")
    print()
    act1 = [s[0] for s in sched[:mid]]
    act2 = [s[0] for s in sched[mid:]]
    groups = sorted(list(set([s[0] for s in sched])))
    fixes = [
        gr for gr in groups if
        all([s[1] == "1" for s in sched if s[0] == gr]) or
        all([s[1] == "2" for s in sched if s[0] == gr])
    ]
    pad = max(*[len(g) for g in groups], 7)
    print(f"| Csoport{' ' * (pad - 7)} | 1. felvonás | 2. felvonás |")
    print(f"|---------{'-' * (pad - 7)}|-------------|-------------|")
    for gr in groups:
        f1 = gr.ljust(pad)
        f2 = str(act1.count(gr) or " ").ljust(11)
        f3 = str(act2.count(gr) or " ").ljust(11)
        f4 = "*" if (
            (act1.count(gr) == 0 or
            act2.count(gr) == 0) and
            act1.count(gr) + act2.count(gr) > 1 and
            gr not in fixes
        ) else ""
        print(f"| {f1} | {f2} | {f3} | {f4}")


def heuristic(acts):
    low, best = float("inf"), None
    try:
        while True:
            act1 = acts["1"];
            act2 = acts["2"];
            actX = acts["X"]; random.shuffle(actX)
            perm = [*act1, *actX, *act2]
            mid = len(perm) // 2
            act1, act2 = perm[:mid], perm[mid:]
            random.shuffle(act1)
            random.shuffle(act2)
            perm = [*act1, *act2]
            sc = score2(perm)
            print("\r", end="")
            if sc.mixes < 5:
                mid = len(perm) // 2
                sc1, act1 = swap(perm[:mid])
                sc2, act2 = swap(perm[mid:])
                sc = sc1 + sc2
                perm = [*act1, *act2]
            if sc < low:
                low, best = sc, perm
            print(f"Jelenlegi legjobb: {low}  ", end="")
            if low < 5:
                return best
    except KeyboardInterrupt:
        pass
    finally:
        print("\r", end="")
        print(f"Jelenlegi legjobb: {low}  ")
    if not best:
        raise
    return best


def swap(perm):
    target = None
    for i, j in itertools.pairwise(range(len(perm))):
        if set(perm[i][2]).intersection(perm[j][2]):
            target = i
    if target is None:
        return score(perm), perm
    orig = score(perm)
    low, best = orig, perm
    for j in range(len(perm)):
        if target != j:
            new = copy.copy(perm)
            new[target], new[j] = perm[j], perm[target]
            sc1 = score(new)
            if sc1 < orig:
                sc2, new = swap(new)
                if sc2 < low:
                    low, best = sc2, new
    return low, best


def exhaustive(acts):
    low, best = float("inf"), None
    total = math.factorial(len(acts["1"]))
    for act_one in tqdm(itertools.permutations(acts["1"]), total=total, leave=False):
        total = math.factorial(len(acts["X"]))
        for either in tqdm(itertools.permutations(acts["X"]), total=total, leave=False):
            total = math.factorial(len(acts["2"]))
            for act_two in tqdm(itertools.permutations(acts["2"]), total=total, leave=False):
                perm = [*act_one, *either, *act_two]
                sc = score2(perm)
                if sc < low:
                    low, best = sc, perm
    if not best:
        raise
    return best


if __name__ == '__main__':
    main()

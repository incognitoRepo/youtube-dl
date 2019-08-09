import itertools

def brent_length(f, x0):
    # main phase: search successive powers of two
    hare = x0
    power = 1
    while True:
        tortoise = hare
        for i in range(1, power+1):
            hare = f(hare)
            if tortoise == hare:
                return i
        power *= 2

def brent(f, x0):
    lam = brent_length(f, x0)

    # Find the position of the first repetition of length lam
    mu = 0
    hare = x0
    for i in range(lam):
    # range(lam) produces a list with the values 0, 1, ... , lam-1
        hare = f(hare)
    # The distance between the hare and tortoise is now lam.

    # Next, the hare and tortoise move at same speed until they agree
    tortoise = x0
    while tortoise != hare:
        tortoise = f(tortoise)
        hare = f(hare)
        mu += 1

    return lam, mu

def iterate(f, x0):
    while True:
        yield x0
        x0 = f(x0)

if __name__ == '__main__':
    f = lambda x: (x * x + 1) % 255
    x0 = 3
    lam, mu = brent(f, x0)
    print("Cycle length: %d" % lam)
    print("Cycle start index: %d" % mu)
    print("Cycle: %s" % list(itertools.islice(iterate(f, x0), mu, mu+lam)))


def pattern(seq):
        storage = {}
        for length in range(1,len(seq)/2+1):
                valid_strings = {}
                for start in range(0,len(seq)-length+1):
                        valid_strings[start] = tuple(seq[start:start+length])
                candidates = set(valid_strings.values())
                if len(candidates) != len(valid_strings.values()):
                        print("Pattern found for " + str(length))
                        storage = valid_strings
                else:
                        print("No pattern found for " + str(length))
                        return set(filter(lambda x: storage.values().count(x) > 1, storage.values()))
        return storage
guess_seq_len(lnsi)
ptrn = [475,476,452,454,455,455]


def sub(s):
    d = {}
    MINLEN = 3
    MINCNT = 3
    # for sublen in range(MINLEN,int(len(s)/MINCNT)):
    for sublen in range(MINLEN,33):
        print(f"{sublen=}")
        for i in range(0,len(s)-sublen):
            print(f"{i=}")
            sub = s[i:i+sublen]
            cnt = s.count(sub)
            if cnt >= MINCNT and sub not in d:
                d[sub] = cnt
    return d
lnst = lns[300:400]
lnsti = [int(elm) for elm in lnst]
len(lnsti) # 100
print(sub(lnsi))


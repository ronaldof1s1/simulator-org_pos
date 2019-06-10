from random import randint

Memsize = 8 * 1024

Mem = []

def dfs():
    G_size = 10
    #for graph
    for i in range(G_size):
        for j in range(G_size):
            if i == j:
                Mem.append(1)
            else:
                conn = randint(0,1)
                Mem.append(conn)
    #for visited
    for i in range(G_size):
        Mem.append(0)

    #for stack
    for i in range(G_size):
        Mem.append(0)

    for i in range(len(Mem), Memsize):
        Mem.append(0)

    return Mem

def mxm():
    M = 10
    N = M
    P = M

    for i in range(M):
        for j in range(P):
            Mem.append(0)

    for i in range(P):
        for j in range(N):
            Mem.append(0)
    
    for i in range(M):
        for j in range(N):
            Mem.append(0)

    for i in range(len(Mem), Memsize):
        Mem.append(0)

    return Mem
    
def bs():
    N = 10
    for i in range(N*N):
        Mem.append(i)

    for i in range(N):
        Mem.append(randint(0,N))

    
    for i in range(len(Mem), Memsize):
        Mem.append(0)

    return Mem
from random import randint

Memsize = 1024**2

Mem = []

def dfs(G_size):
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

def mxm(M_size):
    M = M_size
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
    
def mult_bs(v_size):
    N = v_size
    for i in range(N*N):
        Mem.append(i)

    for i in range(N):
        Mem.append(N+1)

    
    for i in range(len(Mem), Memsize):
        Mem.append(0)

    return Mem

def bs(v_size):
    N = v_size
    for i in range(N):
        Mem.append(i)
    
    for i in range(len(Mem), Memsize):
        Mem.append(0)

    return Mem
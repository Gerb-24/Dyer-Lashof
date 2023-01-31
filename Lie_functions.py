import math

def cartan( i ):
    ans = []
    for k in range(0, i+1):
        ans.append( ( k, i-k ) )
    return ans

def nishida( r, s ):
    ans = []
    for t in range( 0, math.floor( r/2 ) + 1 ):
        try:
            nishida_factor = math.comb( s-r, r - 2*t )
        except ValueError:
            return ans   
        if nishida_factor % 2 == 1:
            ans.append( ( s - r + t, t) )
    return ans

def adem( r, s ):
    ans = []
    for k in range( 0, math.floor( r - s - 1 ) + 1 ):
        nishida_factor = math.comb(  2*s - r + 1 + 2*k, k )
        if nishida_factor % 2 == 1:
            ans.append( (2*s+1+k, r-s-1-k) )
    return ans
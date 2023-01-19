import math

def cartan( i ):
    ans = []
    for k in range(0, i+1):
        ans.append( ( k, i-k ) )
    return ans

def ordered_cartan( i ):
    ans = []
    for k in range(0, i+1):
        if i-k < k:
            ans.append( (k, i-k) )
    return ans

def nishida( r, s, d ):
    ans = []
    for i in range( 0, math.floor( r/2 ) + 1 ):
        try:
            nishida_factor = math.comb( d + s - r, r - 2*i )
        except ValueError:
            return ans
        if nishida_factor % 2 == 1:
            ans.append( ( s - r + 2*i, i) )
    return ans

def adem( r, s ):
    ans = []
    for j in range( math.ceil( (r + s)/2 ), math.floor( r - 1 ) + 1 ):
        adem_factor = math.comb( j-s-1, 2*j-r-s )
        if adem_factor % 2 == 1:
            ans.append( (r+2*s-2*j, j) )
    return ans
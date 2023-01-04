
import math
from main import operads

n = 5

max_weight = 4
max_dim = 100

# Encoding Q^i\colon H_d \to H_{i+2d}
def op_func( i, d ):
    return i + 2*d

def op_range( d ):
    return range( 1, min( n, max_dim ) )

# Encoding the Nishida relations: Sq_i Q_j( x^d ) = ...
def nishida( i, j, d ):
    ans = []
    for k in range( math.ceil( i-(d+j)/2 ), math.floor( i/2 ) + 1 ):
        nishida_factor = math.comb( d + j - i, i - 2*k )
        if nishida_factor % 2 == 1:
            ans.append( ( j - i + 2*k, k ) )
    return ans

# Encoding the Adem relations: Q_i Q_j ( x^d ) = ...
def adem( r, s, d ):
    ans = []
    for j in range( math.ceil( (r + s)/2 ), math.floor( r - 1 ) + 1 ):
        adem_factor = math.comb( j - s - 1, 2*j - r - s )
        if adem_factor % 2 == 1:
            ans.append( ( r+2*s-2*j, j ) )
    return ans

file = 'M2'

operads( file, max_weight, max_dim, adem, nishida, op_func, op_range )
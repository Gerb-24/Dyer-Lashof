import json
import math

class F2_Module():
    def __init__( self, filename ):
        def get_degs_and_ops( filename ):
            with open(filename, 'r') as file:
                data = json.load(file)
            gens = data['gens']
            degs = [ gen['deg'] for gen in gens ]
            ''' dualize ops '''
            dual_ops = [ {} for i, _ in enumerate( gens ) ]
            for i, gen in enumerate( gens ):
                for op in gen['ops']:
                    pow = op['i']
                    for x in op['hits']:
                        if pow in dual_ops[x]:
                            dual_ops[x][pow].append( i )
                        else:
                            dual_ops[x][pow] = [i]

            return degs, dual_ops
        self.degs, self.ops = get_degs_and_ops( filename )

# class BaseGenerator():
#     def __init__( self, index, deg, ops ):
#         self.deg = deg
#         self.index = index
#         self.ops = self.dualise( ops )
#
# class BaseOperation():
#     def __init__( self, pow, im ):
#         self.pow = pow
#         self.im = im

class Generator():
    def __init__( self, ops, gen ):
        self.ops = ops
        self.gen = gen
        self.weight = 2**(len(ops))

    def deg(self, base_degs ):
        return sum( self.ops ) + base_degs[ self.gen ]

    def __str__( self ):
        ops_str = [ f'Q^{i}' for i in self.ops ]
        gen_str = f'x_{self.gen}'
        spacing = '' if not len(self.ops) else ' '
        return f"{' '.join(ops_str)}{spacing}{gen_str}"

    def next( self ):
        return Generator( self.ops[1:], self.gen )

    def to_elt( self ):
        return Elt( [Monomial( [self] )] )

class Monomial():
    def __init__( self, gens ):
        self.gens = gens
        self.weight = sum( gen.weight for gen in self.gens )

    def deg( self, base_degs ):
        return sum( gen.deg( base_degs ) for gen in self.gens )

    def __str__( self ):
        gens_str = [ gen.__str__() for gen in self.gens ]
        return '*'.join( gens_str )

    def __add__( self, other ):
        return Monomial( self.gens + other.gens )

    def next( self ):
        return Monomial( self.gens[1:] )

class Elt():
    def __init__( self, mons ):
        self.mons = mons

    def __add__( self, other ):
        new_mons = []
        common = []
        for mon in other.mons:
            if mon not in self.mons:
                new_mons.append( mon )
            else:
                common.append( mon )
        for mon in self.mons:
            if mon not in common:
                new_mons.append( mon )
        return Elt( new_mons )

    def __mul__( self, other ):
        new_elts = []
        for mon in self.mons:
            for _mon in other.mons:
                new_elts.append( Elt( [mon + _mon] ) )
        return elt_sum( new_elts )


    def __str__( self ):
        mons_str = '+'.join( mon.__str__() for mon in self.mons )
        return mons_str

# general functions

def prods(w, n, gens, base_degs):
    if not len(gens):
        return []
    gen = gens[0]
    tot_prods = [Monomial([gens[0]])]
    restricted_gens = [ _gen for _gen in gens if _gen.weight <= w - gen.weight and _gen.deg(base_degs) <= n - gen.deg(base_degs) ]
    for x in prods( w - gen.weight, n - gen.deg(base_degs), restricted_gens, base_degs ):
        new_prod = [gen]
        new_prod.extend(x.gens)
        tot_prods.append(Monomial(new_prod))
    tot_prods.extend( prods(w, n, gens[1:], base_degs) )
    return tot_prods

def elt_sum( elts ):
    ans = Elt([])
    for elt in elts:
        ans += elt
    return ans

# for computing operations


def Sq_Mon(i, mon: Monomial):
    def cartan( i ):
        ans = []
        for k in range(0, i+1):
            ans.append( ( k, i-k ) )
        return ans

    # base cases
    if i == 0:
        return Elt( [ mon ] )
    if len(mon.gens) == 1:
        return Sq_Gen( i, mon.gens[0] )

    # iterative case
    gen = mon.gens[0]
    ans = [  Sq_Gen( a, gen ) * Sq_Mon( b, mon.next() )  for ( a, b ) in cartan(i) ]
    return elt_sum( ans )

def Sq_Gen(i, gen: Generator):
    def adem( i, j ):
        ans = []
        for k in range( 0, math.floor( i/2 ) + 1 ):
            adem_factor = math.comb( j - i, i - 2*k )
            if adem_factor % 2 == 1:
                ans.append( (j - i + k, k) )
        return ans

    # base cases
    if i == 0:
        return Elt( [ Monomial( [gen] ) ] )
    if len(gen.ops) == 0:
        if i in base_ops[ gen.gen ]:
            elt = Elt ( [ Monomial( [ Generator( [], x ) ] ) for x in base_ops[ gen.gen ][i] ] )
            return elt
        else:
            return Elt([])

    # iterative case
    j = gen.ops[0]
    ans = [DL( a, Sq_Gen(b, gen.next())) for a, b in adem(i, j) ]
    return elt_sum( ans )

def DL( i, elt: Elt ):
    # Here we assume that the elt is only a sum of base generators
    elt_list = []
    for mon in elt.mons:
        base_gen = mon.gens[0].gen
        _mon = Monomial( [Generator( [i], base_gen )] )
        elt_list.append( _mon )
    return Elt( elt_list )

# n = 7
# w = 2
# file = 's1'

n = 10
w = 2
file = "D_2s1to7mod"

base_module = F2_Module( f'{file}.json' )
base_degs = base_module.degs
base_ops = base_module.ops

gens = [ Generator( [], i ) for i in range(len(base_degs)) ]
new_gens = []
for j in range(len(base_degs)):
    j_new_gens = [ Generator( [i], j ) for i in range( base_degs[j] + 1, n-base_degs[j] + 1 ) ]
    new_gens.extend( j_new_gens )

gens.extend(new_gens)
print( f'{len( gens )} generators' )

mons_list = prods(w, n, gens, base_degs)
mons_list = [ mon for mon in mons_list if mon.weight != 1 ]
print( f'{len( mons_list )} monomials' )

mons_list.sort( key= lambda mon: mon.deg(base_degs) )
print( 'Mons sorted' )


min_deg = mons_list[0].deg( base_degs );
mon_ops = [[] for mon in mons_list ]

for ind, mon in enumerate( mons_list ):
    print( f'ops on monomial {ind}: {mon}' )
    for i in range( 1, mon.deg(base_degs) - min_deg + 1 ):
        for _mon in Sq_Mon( i, mon ).mons:
            print( f'   Sq_{i}: {_mon}' )

# ans_list = [
#     Sq_Mon( 2, Monomial( [ Generator([5], 1) ] )  ),
#     Sq_Mon( 1, Monomial( [ Generator([], 1),  Generator([], 3)] )  ),
#     Sq_Mon( 2, Monomial( [ Generator([], 1),  Generator([], 3)] )  ),
#     ]
# for ans in ans_list:
#     print( ans )

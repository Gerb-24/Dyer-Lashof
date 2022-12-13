import math
import json

class F2_Module():
    def __init__( self, filename ):
        def get_degs_and_ops( filename ):
            with open(filename, 'r') as file:
                data = json.load(file)
            gens = data['gens']
            degs = [ gen['deg'] for gen in gens ]
            ops = [{} for i, _ in enumerate( gens ) ]
            for i, gen in enumerate( gens ):
                for pow in gen['ops']:
                    ops[i] = { int(pow): gen['ops'][pow] }

            return degs, ops
        self.degs, self.ops = get_degs_and_ops( filename )

class Generator():
    def __init__( self, ops, gen ):
        self.ops = ops
        self.gen = gen
        self.weight = 2**(len(ops))

    def deg(self, base_degs ):
        ans = base_degs[ self.gen ]
        for op in self.ops:
            ans = 2*ans + op
        return ans

    def __str__( self ):
        ops_str = [ f'Q_{i}' for i in self.ops ]
        gen_str = f'x_{self.gen}'
        spacing = '' if not len(self.ops) else ' '
        return f"{' '.join(ops_str)}{spacing}{gen_str}"

    def next( self ):
        return Generator( self.ops[1:], self.gen )

    def to_elt( self ):
        return Elt( [Monomial( [self] )] )
    
    def __eq__( self, other ):
        return self.ops == other.ops and self.gen == other.gen

class Bracket():
    def __init__(self, gen1, gen2):
        self.gen1 = gen1
        self.gen2 = gen2
        self.weight = 2

    def deg( self, base_degs, n ):
        ans = self.gen1.deg( base_degs ) + self.gen2.deg( base_degs ) + n-1
        return ans

    def __str__( self ):
        return f'[{self.gen1}, {self.gen2}]'

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
        tot_gens = self.gens + other.gens
        tot_gens.sort( key=lambda gen: gen.deg(base_degs) )
        return Monomial( tot_gens)
    
    def __eq__( self, other ):
        return self.gens == other.gens

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

def elt_sum( elts ):
    ans = Elt([])
    for elt in elts:
        ans += elt
    return ans

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

def Sq_Gen( i, gen: Generator ) :

    # base cases
    if i == 0:
        return Elt( [ Monomial( [ gen ] ) ] )
    if len( gen.ops ) == 0:
        if i in base_ops[ gen.gen ]:
            elt = Elt ( [ Monomial( [ Generator( [], x ) ] ) for x in base_ops[ gen.gen ][ i ] ] )
            return elt
        else:
            return Elt([])

    # iterative case
    j = gen.ops[0]
    ans = [ DL( a, Sq_Gen( b, gen.next() ) ) for a, b in nishida( i, j, gen.next().deg( base_degs ) ) ]
    return elt_sum( ans )

def DL( i, elt: Elt ):

    # Here we assume that the elt is only a sum of base generators

    #squaring
    if i == 0:
        elt_list = []
        for mon in elt.mons:
            base_gen = mon.gens[0].gen
            _mon = Monomial( [Generator( [], base_gen ), Generator( [], base_gen )] )
            elt_list.append( _mon )
        return Elt(elt_list)

    elt_list = []
    for mon in elt.mons:
        base_gen = mon.gens[0].gen
        _mon = Monomial( [Generator( [i], base_gen )] )
        elt_list.append( _mon )
    return Elt( elt_list )

def nishida( i, j, d ):
    ans = []
    for k in range( math.ceil( (i-j)/2 ), math.floor( i/2 ) + 1 ):
        nishida_factor = math.comb( d + j - i, i - 2*k )
        if nishida_factor % 2 == 1:
            ans.append( (j - i + 2*k, k) )
    return ans

file = 'Brow'
base_module = F2_Module( f'json_files/{file}.json' )
base_degs = base_module.degs
base_ops = base_module.ops


def Sq_Brac( i, brac ):
    def cartan( i ):
        ans = []
        for k in range(0, i+1):
            ans.append( ( k, i-k ) )
        return ans

    # base cases
    if i == 0:
        return brac
    
    # default case
    for ( a, b ) in cartan(i):
        ans = Brac_of_Elts( Sq_Gen( a, brac.gen1 ), Sq_Gen( b, brac.gen2 ) )
        for brac in ans:
            print( brac )
def Brac_of_Elts( elt1, elt2 ):
    bracs = []
    for mon in elt1.mons:
        for _mon in elt2.mons:
            b = Bracket( mon.gens[0], _mon.gens[0] )
            bracs.append( b )
    return bracs

b = Bracket( Generator([], 1), Generator([], 2) )
print( Sq_Brac(1, b) )

n = 3
d = 2
min_deg = 2

# as our operations are already bounded, we can compute all of them. However we still need weight.
_n = 100
w = 2

gens = [ Generator( [], i ) for i in range(len(base_degs)) ]
new_gens = []
for j in range(len(base_degs)):
    j_new_gens = [ Generator( [i], j ) for i in range( 1, n ) ]
    new_gens.extend( j_new_gens )
new_bracs = []
for i in range(len(base_degs)):
    new_brac = [ Bracket( Generator([], i), Generator([], j) ) for j in range(i+1, len(base_degs)) ]
    new_bracs.extend( new_brac )

gens.extend(new_gens)
gens.extend( new_bracs )
print( f'{len( gens )} generators' )


# mons_list = prods(w, _n, gens, base_degs)
# mons_list = [ mon for mon in mons_list if mon.weight != 1 ]
# print( f'{len( mons_list )} monomials' )

# mons_list.sort( key= lambda mon: mon.deg(base_degs) )
# print( 'Mons sorted' )

# min_deg = mons_list[0].deg( base_degs );
# mon_ops = [[] for mon in mons_list ]

# data_list = [ {'name': mon.__str__(), 'deg': mon.deg(base_degs), 'ops': {}} for mon in mons_list ]

# for ind, mon in enumerate( mons_list ):
#     print( f'ops on monomial {ind}: {mon}' )
#     for i in range( 1, mon.deg(base_degs) - min_deg + 1 ):
#         sq_list = []
#         for _mon in Sq_Mon( i, mon ).mons:
#             index = mons_list.index( _mon )
#             # print( f'   Sq_{i}: {_mon}: {index}' )
#             sq_list.append( index )
#         if sq_list:
#             data_list[ind]['ops'][i] = sq_list

# data = { 'gens': data_list }
# with open('output.json', 'w') as file:
#     _data = json.dumps(data, indent=2)
#     file.write(_data)


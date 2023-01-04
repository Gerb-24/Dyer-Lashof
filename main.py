import json
from typing import Callable, List, Iterable

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
    def __init__( self, ops, gen, gen_deg, op_func ):
        # we use this to create next and other stuff
        self.op_func = op_func
        self.gen_deg = gen_deg

        # real data
        self.ops = ops
        self.gen = gen
        self.deg =  self.get_deg( gen_deg, op_func )
        self.weight = 2**(len(ops))

    def get_deg( self, gen_deg, op_func ):
        ans = gen_deg
        for i in self.ops:
            ans = op_func( i, ans )
        return ans

    def __str__( self ):
        ops_str = [ f'Q_{i}' for i in self.ops ]
        gen_str = f'x_{self.gen}'
        spacing = '' if not len(self.ops) else ' '
        return f"{' '.join(ops_str)}{spacing}{gen_str}"

    def next( self ):
        return Generator( self.ops[1:], self.gen, self.gen_deg, self.op_func )

    def to_elt( self ):
        return Elt( [Monomial( [self] )] )
    
    def __eq__( self, other ):
        return self.ops == other.ops and self.gen == other.gen

class Monomial():
    def __init__( self, gens ):
        self.gens = gens
        self.weight = sum( gen.weight for gen in self.gens )
        self.deg = sum( gen.deg for gen in self.gens )

    def __str__( self ):
        gens_str = [ gen.__str__() for gen in self.gens ]
        return '*'.join( gens_str )

    def __add__( self, other ):
        tot_gens = self.gens + other.gens
        tot_gens.sort( key=lambda gen: gen.deg )
        return Monomial( tot_gens)
    
    def __eq__( self, other ):
        self.gens.sort( key=lambda gen: gen.gen_deg )
        other.gens.sort( key=lambda gen: gen.gen_deg )
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

def elt_sum( elts: List[ Elt ]) -> Elt:
    ans = Elt([])
    for elt in elts:
        ans += elt
    return ans

def prods( max_weight: int, max_dim: int, gens: List[ Generator ] ):
    if not len(gens):
        return []
    gen = gens[0]
    tot_prods = [ Monomial( [ gen ] ) ]
    restricted_gens = [ _gen for _gen in gens if _gen.weight <= max_weight - gen.weight and _gen.deg <= max_dim - gen.deg ]
    for x in prods( max_weight - gen.weight, max_dim - gen.deg, restricted_gens ):
        new_prod = [ gen ]
        new_prod.extend( x.gens )
        tot_prods.append( Monomial( new_prod ) )
    tot_prods.extend( prods( max_weight, max_dim, gens[1:]) )
    return tot_prods

def create_Sq_Mon( Sq_Gen: Callable[ [int, Generator], Elt ] ):
    def Sq_Mon(i, mon: Monomial  ):
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
    return Sq_Mon

def Nishida_to_Sq_Gen( nishida: Callable[ [ int, int, int ], List ], base_ops: List[ dict ], base_degs: List[ int ], DL_Elt: Callable[ [int, Elt], Elt ] ):
    def Sq_Gen( i, gen: Generator ) :

        # base cases
        if i == 0:
            return Elt( [ Monomial( [ gen ] ) ] )
        if len( gen.ops ) == 0:
            if i in base_ops[ gen.gen ]:
                elt = Elt ( [ Monomial( [ Generator( [], x, base_degs[ x ], gen.op_func ) ] ) for x in base_ops[ gen.gen ][ i ] ] )
                return elt
            else:
                return Elt([])

        # iterative case
        j = gen.ops[0]
        ans = [ DL_Elt( a, Sq_Gen( b, gen.next() ) ) for a, b in nishida( i, j, gen.next().deg ) ]
        return elt_sum( ans )
    return Sq_Gen

def create_DL_Elt( DL_Mon: Callable[ [ int, Monomial ], Elt ] ):
    def DL_Elt( i: int, elt: Elt ):
        ans = [ DL_Mon( i, mon ) for mon in elt.mons ]
        return elt_sum( ans )
    return DL_Elt

def create_DL_Mon( DL_Gen: Callable ) -> Callable[ [ int, Monomial ], Elt ]:
    def DL_Mon( i: int, mon: Monomial ) -> Elt:
        def cartan( i ):
            ans = []
            for k in range(0, i+1):
                ans.append( ( k, i-k ) )
            return ans

        if len( mon.gens ) == 1:
            return DL_Gen( i, mon.gens[0] )

        # iterative case
        gen = mon.gens[0]
        ans = [  DL_Gen( a, gen ) * DL_Mon( b, mon.next() )  for ( a, b ) in cartan(i) ]
        return elt_sum( ans )
    return DL_Mon

def Adem_to_DL_Gen( adem: Callable[ [ int, int, int ], List ] ) -> Callable[ [int, Generator], Elt ]:
    def DL_Gen( i, gen: Generator ):
        # base cases
        if i < 0:
            return Elt([])
        if i == 0:
            return Elt([ Monomial( [ gen, gen] ) ])
        if len(gen.ops) == 0:
            new_gen = Generator( [ i ], gen.gen, gen.gen_deg, gen.op_func )
            return Elt([ Monomial( [ new_gen ] ) ])
        if i < gen.ops[0]:
            new_gen = Generator( [i, *gen.ops], gen.gen, gen.gen_deg, gen.op_func )

        # constructing DL_Elt for iterative case
        DL_Mon = create_DL_Mon( DL_Gen )
        DL_Elt = create_DL_Elt( DL_Mon )

        # ieterative case
        j = gen.ops[0]
        ans = [ DL_Elt( a, DL_Gen( b, gen.next() ) ) for a, b in adem( i, j, gen.next().deg ) ]
        return elt_sum( ans )

    return DL_Gen

def base_degs_to_gens( max_weight: int, max_dim: int, base_degs: List[ int ], op_func: Callable[ [ int, int ], int ], op_range: Callable[ [ int ], Iterable ] ) -> List[ Generator ]:
    gens = [ Generator( [], i, base_degs[i], op_func ) for i in range(len(base_degs)) ]
    new_gens = gens.copy()
    weight = 2
    while weight <= max_weight:
        newer_gens = []
        for gen in new_gens:
            next_op = gen.ops[0] if gen.ops else max_dim
            gen_with_ops = [ Generator( [i, *gen.ops], gen.gen, gen.gen_deg, gen.op_func ) for i in range( 1, min( 5, max_dim ) ) if i <= next_op ]
            newer_gens.extend( gen_with_ops )
        gens.extend( newer_gens )
        new_gens = newer_gens # update for next iteration
        weight *= 2 # see the definition of weight in the Generator class
    print( f'{len( gens )} generators' )
    return gens

def gens_to_mons( max_weight: int, mad_dim: int, gens: List[ Generator ] ) -> List[ Monomial ]:
    mons_list = prods( max_weight, mad_dim, gens )
    mons_list = [ mon for mon in mons_list if mon.weight != 1 ]
    print( f'{len( mons_list )} monomials' )

    mons_list.sort( key= lambda mon: mon.deg )
    print( 'Mons sorted' )
    return mons_list

def mons_list_to_data( mons_list: List[Monomial], Sq_Mon: Callable[ [Monomial], Elt ] ):
    min_deg = mons_list[0].deg
    data_list = [ {'name': mon.__str__(), 'deg': mon.deg, 'ops': {}} for mon in mons_list ]
    for ind, mon in enumerate( mons_list ):
        print( f'ops on monomial {ind}: {mon}' )
        for i in range( 1, mon.deg - min_deg + 1 ):
            sq_list = []
            for _mon in Sq_Mon( i, mon ).mons:
                index = mons_list.index( _mon )
                print( f'   Sq_{i}: {_mon}: {index}' )
                sq_list.append( index )
            if sq_list:
                data_list[ind]['ops'][i] = sq_list

    data = { 'gens': data_list }
    return data

def operads( file, max_weight, max_dim, adem, nishida, op_func, op_range ):
    base_module = F2_Module( f'json_files/{file}.json' )
    base_degs = base_module.degs
    base_ops = base_module.ops

    # constructing the monomials
    gens = base_degs_to_gens( max_weight, max_dim, base_degs, op_func, op_range )
    mons_list = gens_to_mons( max_weight, max_dim, gens )
    for mon in mons_list:
        print( mon )

    # constructing Sq_Mon to compute the steenrod squares
    DL_Gen = Adem_to_DL_Gen( adem )
    DL_Mon = create_DL_Mon( DL_Gen )
    DL_Elt = create_DL_Elt( DL_Mon )
    Sq_Gen = Nishida_to_Sq_Gen( nishida, base_ops, base_degs, DL_Elt )
    Sq_Mon = create_Sq_Mon( Sq_Gen )

    # compute steenrod squares
    data = mons_list_to_data( mons_list, Sq_Mon )

    # save as output.json in the current directory
    with open('output.json', 'w') as file:
        _data = json.dumps(data, indent=2)
        file.write(_data)

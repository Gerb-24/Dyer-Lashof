from main import F2_Module
from typing import Callable, List, Iterable
import math
import json

class Generator():
    def __init__(self, ops, brac) -> None:
        self.ops = ops
        self.brac = brac
        self.deg = self.get_deg()
        self.weight = 2**len(self.ops) * self.brac.weight

    def get_deg( self ):
        ans = self.brac.deg
        for i in self.ops:
            ans = self.op_func( i, ans )
        return ans
    
    def op_func(self, i, d ):
        return d + i - 1

    def next( self ):
        return Generator( self.ops[1:], self.brac )

    def __str__(self) -> str:
        ops_str = [ f'Q_{i}' for i in self.ops ]
        return f"{' '.join(ops_str)}{self.brac}"
    
    def __eq__(self, other) -> bool:
        return self.brac == other.brac and self.ops == other.ops

class Elt():
    def __init__(self, gens) -> None:
        self.gens = gens
    
    def __str__(self) -> str:
        gens_str = '+'.join( gen.__str__() for gen in self.gens )
        return gens_str

    def __add__( self, other ):
        # encoding mod-2-ness
        new_gens = []
        common = []
        for gen in other.gens:
            if gen not in self.gens:
                new_gens.append( gen )
            else:
                common.append( gen )
        for gen in self.gens:
            if gen not in common:
                new_gens.append( gen )
        return Elt( new_gens )

class BracketGenerator():
    def __init__(self, index, deg):
        self.weight = 1
        self.index = index
        self.deg = deg

    def __str__(self) -> str:
        return f'x_{self.index}'

    def __eq__(self, other) -> bool:
        if not self.weight == other.weight:
            return False
        return self.index == other.index

class Bracket():
    def __init__(self, brac_0, brac_1):
        self.bracket = ( brac_0, brac_1 )
        self.weight = brac_0.weight + brac_1.weight
        self.deg = brac_0.deg + brac_1.deg - 1

    def __str__(self) -> str:
        return f' \left [ { self.bracket[0].__str__() }, { self.bracket[1].__str__() } \\right ]'

    def __eq__(self, other) -> bool:
        if not self.weight == other.weight:
            return False
        return self.bracket == other.bracket

def naive_bracket( b0, b1 ) -> Elt:
    # note that for checking inequalities in our order
    # we need to check if the weights are not the same, and if they are we need to check the index
    i_b0, i_b1 = brackets_dic[ b0.weight ].index( b0 ), brackets_dic[ b1.weight ].index( b1 )
    # if w_1 > w_2 then [w_1, w_2] = [w_2, w_1]
    if b0.weight > b1.weight:
        return naive_bracket( b1, b0 )
    if b0.weight == b1.weight:
        if i_b0 > i_b1:
            return naive_bracket( b1, b0 )

        # if w_1 = w_2 then [w_1, w_2] = Q^{w_1.deg}(w_1)
        elif i_b0 == i_b1:
            ans = Elt([
                Generator(
                    [ b1.deg ],
                    b1
                )
            ])
            return ans
    # if w_2 is not a bracket, then [w_1,w_2] is a basic product
    if b1.weight == 1:
        ans = Elt([
            Generator(
                [],
                Bracket( b0, b1 )
            )
        ])
        return ans

    b1_0, b1_1 = b1.bracket
    i_b1_0 = brackets_dic[ b1_0.weight ].index( b1_0 )

    # if w_1 < w_2 and w_2 = [ w_3, w_4 ] with w_1 < w_3 then ...
    if b1_0.weight > b0.weight:
        elt1_0 = Elt( [ Generator( [], b1_0 ) ] )
        elt1_1 = Elt( [ Generator( [], b1_1 ) ] )
        ans = [
            Brac_Elt( elt1_0, naive_bracket( b0, b1_1 ) ),
            Brac_Elt( elt1_1, naive_bracket( b0, b1_0 ) )
        ]
        return elt_sum( ans )
    if b1_0.weight == b0.weight:
        if i_b1_0 > i_b0:
            elt1_0 = Elt( [ Generator( [], b1_0 ) ] )
            elt1_1 = Elt( [ Generator( [], b1_1 ) ] )
            ans = [
                Brac_Elt( elt1_0, naive_bracket( b0, b1_1 ) ),
                Brac_Elt( elt1_1, naive_bracket( b0, b1_0 ) )
            ]
            return elt_sum( ans )

    # everything is checked and this is a basic product
    ans = Elt([
        Generator(
            [],
            Bracket( b0, b1 )
        )
    ])
    return ans

def elt_sum( elts: List[ Elt ]) -> Elt:
    ans = Elt([])
    for elt in elts:
        ans += elt
    return ans

file = 'M2'
max_dim = 10
max_weight = 5

base_module = F2_Module( f'json_files/{file}.json' )
base_degs = base_module.degs
base_ops = base_module.ops

def base_degs_to_brackets( max_weight: int, base_degs: List[ int ]):
    gens = [ BracketGenerator( i, d ) for i, d in enumerate( base_degs ) ]
    bracs = []
    for i_1, gen_1 in enumerate( gens ):
        for i_0 in range( i_1 ):
            gen_0 = gens[ i_0 ]
            # check that the degree is not too big
            if gen_0.deg + gen_1.deg - 1 > max_dim:
                continue
            bracs.append( Bracket( gen_0, gen_1 ) )
    brac_weight_data = {
        1:  gens,
        2:  bracs.copy()
    }
    weight = 2

    while weight < max_weight:
        bracs = []
        weight += 1
        for key_1 in brac_weight_data:
            key_0 = weight - key_1
            if key_0 > key_1:
                continue

            for i_1, brac_1 in enumerate( brac_weight_data[ key_1 ] ):
                brac_1_0 = brac_1.bracket[0]
                i_1_0 = brac_weight_data[ brac_1_0.weight ].index( brac_1_0 )
                if brac_1_0.weight > key_0:
                    continue
                if key_0 == key_1: 
                    # in this case we need the index to be lower
                    # we also do not need to check for brac_1_0 to have lower weight as this already lower than key_1
                    for i_0 in range( i_1 ):
                        brac_0 = brac_weight_data[ key_0 ][ i_0 ]
                        # dimension check
                        if brac_0.deg + brac_1.deg - 1 >= max_dim:
                            continue
                        bracs.append( Bracket( brac_0, brac_1 ) )
                elif key_0 == brac_1_0.weight:
                    for i_0 in range( i_1_0, len( brac_weight_data[ key_0 ] ) ):
                        brac_0 = brac_weight_data[ key_0 ][ i_0 ]
                        # dimension check
                        if brac_0.deg + brac_1.deg - 1 >= max_dim:
                            continue
                        bracs.append( Bracket( brac_0, brac_1 ) )
                else:
                    for brac_0 in brac_weight_data[ key_0 ]:
                        # dimension check
                        if brac_0.deg + brac_1.deg - 1 >= max_dim:
                            continue
                        bracs.append( Bracket( brac_0, brac_1 ) )

        brac_weight_data[ weight ] = bracs.copy()
    return brac_weight_data

brackets_dic = base_degs_to_brackets( max_weight, base_degs )

def bracs_to_gens( max_weight: int, max_dim: int, brackets_dic ):
    # make the brackets into generators without any ops
    generators_dic = {}
    for key in brackets_dic:
        generators_dic[ key ] = [ Generator( [], bracket ) for bracket in brackets_dic[ key ] ]
    new_generator_dic = generators_dic.copy()
    index = 1
    while new_generator_dic:
        index += 1
        for w_key in new_generator_dic:
            newer_generator_dic = {}
            new_w_key = 2 * w_key
            if new_w_key <= max_weight:
                for generator in generators_dic[ w_key ]:
                    # we want the sequence of operators to be completelt undadmissible
                    if generator.ops:
                        min_deg = 2 * generator.ops[0] + 1
                    # we want the operators degree to be at least that of the bracket
                    else:
                        min_deg = generator.deg
                    # the max dimension is correct but maybe a bit unclear
                    new_generator_list = [ Generator( [i, *generator.ops], generator.brac ) for i in range( min_deg, max_dim - generator.deg ) ]
                    if new_w_key in newer_generator_dic:
                        newer_generator_dic[ new_w_key ].extend( new_generator_list )
                    else:
                        newer_generator_dic[ new_w_key ] = new_generator_list
            for key in newer_generator_dic:
                if key in generators_dic:
                    generators_dic[ key ].extend( newer_generator_dic[ key ] )
                else:
                    generators_dic[ key ] = newer_generator_dic[ key ].copy()
            new_generator_dic = newer_generator_dic
    return generators_dic

generators_dic = bracs_to_gens( max_weight, max_dim, brackets_dic )

generators_list = []
for key in range( 2, max_weight + 1 ):
    if key in generators_dic:
        generators_list.extend( generators_dic[key] )

# for gen in generators_list:
#     print( gen, gen.deg )

def Sq_Gen( i: int, generator: Generator ) -> Elt:
    # Encoding the Nishida relations: Sq_i Q^j( x^d ) = ...
    def nishida( r, s, d ):
        ans = []
        for t in range( 0, math.floor( r/2 ) + 1 ):
            nishida_factor = math.comb( s-r, r - 2*t )
            if nishida_factor % 2 == 1:
                ans.append( ( s - r + t, t) )
        return ans
    
    if i == 0:
        return Elt( [ generator ] )
    # Only a single bracket
    if not generator.ops:
        return Sq_Brac( i, generator.brac )
    
    # iterative case
    j = generator.ops[0]
    ans = [ DL_Elt( a, Sq_Gen( b, generator.next() ) ) for a, b in nishida( i, j, generator.next().deg ) ]
    return elt_sum( ans )
       
def Sq_Brac( i:int, bracket: Bracket ) -> Elt:
    # print(f'Sq_{i}( {bracket} )')
    def cartan( i ):
        ans = []
        for k in range(0, i+1):
            ans.append( ( k, i-k ) )
        return ans
    # when its the identity map
    if i == 0:
        ans = Elt( [ Generator( [], bracket ) ] )
        return ans
    
    # we have reached the base generator
    if bracket.weight == 1:
        if i in base_ops[ bracket.index ]:
            elt = Elt( [ Generator( [], BracketGenerator( x, base_degs[x] ) ) for x in base_ops[ bracket.index ][ i ] ] )
            return elt
        else:
            return Elt([])
    # the iterative case
    ans = [  Brac_Elt( Sq_Brac( a, bracket.bracket[0] ), Sq_Brac( b, bracket.bracket[1] ) )  for ( a, b ) in cartan(i) ]
    return elt_sum( ans )

def Brac_Elt( elt_0: Elt, elt_1: Elt ):
    # print( f'BE: [ {elt_0},{elt_1} ]' )
    ans = []
    for gen_0 in elt_0.gens:
        for gen_1 in elt_1.gens:
            ans.append( Brac_Gen( gen_0, gen_1 ) )
    return elt_sum( ans )

def Brac_Gen( gen_0: Generator, gen_1: Generator ):
    # print( f'BG: [ {gen_0} , {gen_1} ]')
    if gen_0.ops or gen_1.ops:
        return Elt([])
    return naive_bracket( gen_0.brac, gen_1.brac )

def DL_Elt( i: int, elt: Elt ) -> Elt:
    # print(f'DL_Elt: Q_{ i } { elt } ')
    ans = [ DL_Gen( i, gen ) for gen in elt.gens ]
    return elt_sum( ans )

def DL_Gen( i: int, generator: Generator ) -> Elt:
    # print(f'DL_Gen: Q_{i} { generator }')
    # Encoding the Adem relations: 
    def adem( r, s, d ):
        ans = []
        for k in range( 0, math.floor( r - s - 1 ) + 1 ):
            nishida_factor = math.comb(  2*s - r + 1 + 2*k, k )
            if nishida_factor % 2 == 1:
                ans.append( (2*s+1+k, r-s-1-k) )
        return ans
    
    # if we reached a bracket
    if not generator.ops:
        # but the degree is too low
        if i < generator.deg:
            ans = Elt([])
            return ans
        else:
            ans = Elt( [ Generator( [i], generator.brac ) ] )
            return ans
    
    if i > 2*generator.ops[0]:
        ans = Elt( [ Generator( [i, *generator.ops], generator.brac ) ] )
        return ans

    # iterative case
    j = generator.ops[0]
    ans = [ DL_Elt( a, DL_Gen( b, generator.next() ) ) for a, b in adem( i, j, generator.next().deg ) ]
    return elt_sum( ans )

mons_list = generators_list
min_deg = mons_list[0].deg
data_list = [ {'name': mon.__str__(), 'deg': mon.deg, 'ops': {}} for mon in mons_list ]
for ind, mon in enumerate( mons_list ):
    print( f'ops on monomial {ind}: {mon}' )
    for i in range( 1, mon.deg - min_deg + 1 ):
        sq_list = []
        for _mon in Sq_Gen( i, mon ).gens:
            index = mons_list.index( _mon )
            print( f'   Sq_{i}: {_mon}: {index}' )
            sq_list.append( index )
        if sq_list:
            data_list[ind]['ops'][i] = sq_list

data = { 'gens': data_list }

# save as output.json in the current directory
with open('output.json', 'w') as file:
    _data = json.dumps(data, indent=2)
    file.write(_data)
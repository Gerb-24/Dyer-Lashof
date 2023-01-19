import json
from E_n_functions import nishida, adem, cartan, ordered_cartan

n = 5

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

class Operation():
    def __init__(self, power, node) -> None:
        self.power = power
        self.next = node
        self.degree = power + 2*node.degree
        self.weight = 2*node.weight
    
    def __str__(self) -> str:
        return f'Q_{self.power}({self.next})'

    def output_str(self):
        return f'Q_{self.power}({self.next.output_str()})'

    def __eq__(self, __o: object) -> bool:
        return self.__class__ == __o.__class__ and self.power == __o.power and self.next == __o.next

class Product():
    def __init__(self, node_0, node_1) -> None:
        self.next_0 = node_0
        self.next_1 = node_1
        self.degree = node_0.degree + node_1.degree
        self.weight = node_0.weight + node_1.weight
    
    def __str__(self) -> str:
        return f'{self.next_0} * {self.next_1}'
    
    def output_str(self):
        return f'{self.next_0.output_str()} * {self.next_1.output_str()}'
    
    def __eq__(self, __o: object) -> bool:
        return self.__class__ == __o.__class__ and self.next_0 == __o.next_0 and self.next_1 == __o.next_1

class Browder():
    def __init__(self, node_0, node_1 ) -> None:
        self.next_0 = node_0
        self.next_1 = node_1
        self.degree = node_0.degree + node_1.degree + ( n - 1 )
        self.weight = node_0.weight + node_1.weight

    def __str__(self) -> str:
        return f'[{self.next_0},{self.next_1}]'

    def output_str(self):
        return f'\left [{self.next_0.output_str()},{self.next_1.output_str()} \\right ]'

    def __eq__(self, __o: object) -> bool:
        return self.__class__ == __o.__class__ and self.next_0 == __o.next_0 and self.next_1 == __o.next_1

class Generator():
    def __init__(self, index, degree) -> None:
        self.index = index # index in base_degrees
        self.next = None
        self.degree = degree # degree of this base generator
        self.weight = 1
    
    def __str__(self) -> str:
        return f'x_{self.index}'

    def output_str(self):
        return self.__str__()
    
    def __eq__(self, __o: object) -> bool:
        return self.__class__ == __o.__class__ and self.index == __o.index

class Element():
    def __init__(self, nodes) -> None:
        self.nodes = nodes
    
    def __str__(self) -> str:
        nodes_str = '+'.join( node.__str__() for node in self.nodes )
        return nodes_str

    def __add__(self, __o ):
        new_nodes = []
        common_nodes = []
        for node in __o.nodes:
            if node not in self.nodes:
                new_nodes.append( node )
            else:
                common_nodes.append( node )
        for node in self.nodes:
            if node not in common_nodes:
                new_nodes.append( node )
        return Element( new_nodes )


def elt_sum( elt_list):
    ans = Element([])
    for elt in elt_list:
        ans += elt
    return ans

file = 'M2'
max_dim = 15
max_weight = 4

base_module = F2_Module( f'json_files/{file}.json' )
base_degs = base_module.degs
base_ops = base_module.ops

def Steenrod( i, node ):
    if i == 0:
        elt = Element([
            node
        ]
        )
        return elt

    if node.__class__ == Generator:
        if i in base_ops[ node.index ]:
            elt = Element(
                [
                    Generator( j, base_degs[j] ) for j in base_ops[ node.index ][ i ]
                ]
            )
            return elt
        else:
            return Element([])

    if node.__class__ == Operation:
        # nishida relations
        elt_list = [
            Operation_func(
                a,
                Steenrod(
                    b,
                    node.next
                )
            )
            for ( a, b ) in nishida( i, node.power, node.next.degree )
        ]
        if node.power == n-1:
            top_elt_list = [
                Browder_func(
                    Steenrod( a, node.next ),
                    Steenrod( b, node.next ),
                )
                for ( a, b ) in ordered_cartan( i )
            ]
            elt_list.extend( top_elt_list )
        return elt_sum( elt_list )

    if node.__class__ == Product:
        # cartan formula
        elt_list = [
            Product_func(
                Steenrod(
                    a,
                    node.next_0
                ),
                Steenrod(
                    b,
                    node.next_1
                )
            )
            for ( a, b ) in cartan( i )
        ]
        return elt_sum( elt_list )

    if node.__class__ == Browder:
        # cartan formula
        elt_list = [
            Browder_func(
                Steenrod(
                    a,
                    node.next_0
                ),
                Steenrod(
                    b,
                    node.next_1
                )
            )
            for ( a, b ) in cartan( i )
        ]
        return elt_sum( elt_list )

def Product_func( node_0, node_1 ):
    if node_0.__class__ == Element and node_1.__class__ == Element:
        # bilinear
        elt_list = []
        for _node_0 in node_0.nodes:
            for _node_1 in node_1.nodes:
                elt_list.append( 
                    Product_func( _node_0, _node_1 ) 
                )
        return elt_sum( elt_list )
    
    if node_0.__class__ == Product:
        elt_0 = Element(
            [
                node_0.next_0
            ]
        )
        elt = Product_func(
            elt_0,
            Product_func(
                node_0.next_1,
                node_1
            )
        )
        return elt

    if node_0.__class__ in { Browder, Operation, Generator }:
        if node_1.__class__ == Product:
            if operation_order.index( node_0 ) < operation_order.index( node_1.next_0 ):
                elt_0 = Element(
                    [
                        node_1.next_0
                    ]
                )
                
                elt = Product_func(
                    node_0,
                    node_1.next_1
                )
                return elt

        if node_1.__class__ in { Browder, Operation, Generator }:
            if node_0 == node_1:
                elt = Element(
                    [
                        Operation(
                            0,
                            node_0
                        )
                    ]
                )
                return elt

            if operation_order.index( node_0 ) < operation_order.index( node_1):
                elt = Product_func(
                    node_1,
                    node_0
                )
                return elt

        elt = Element(
            [
                Product(
                    node_0,
                    node_1
                )
            ]
        )
        return elt
    raise Exception

def Browder_func( node_0, node_1 ):
    if node_0.__class__ == Element and node_1.__class__ == Element:
        # Biliniearity
        elt_list = []
        for _node_0 in node_0.nodes:
            for _node_1 in node_1.nodes:
                elt_list.append( 
                    Browder_func( _node_0, _node_1 ) 
                )
        return elt_sum( elt_list )

    if node_0.__class__ == Operation and node_0.power < n-1:
        # Dyer–Lashof vanishing
        return Element([])
    
    if node_1.__class__ == Operation and node_1.power < n-1:
        # Dyer–Lashof vanishing
        return Element([])

    if node_0 == node_1:
        # Antisymmetry 2
        return Element([])

    if node_0.__class__ == Operation and node_0.power == n-1:
        # Adjoint identity
        elt_0 = Element(
            [
                node_0.next
            ]
        )
        elt = Browder_func(
            elt_0,
            Browder_func(
                elt_0,
                node_1
            )
        )
        return elt

    if node_1.__class__ == Operation and node_1.power == n-1:
        # Adjoint identity
        elt_0 = Element(
            [
                node_1.next
            ]
        )
        elt = Browder_func(
            elt_0,
            Browder_func(
                elt_0,
                node_0
            )
        )
        return elt

    if node_0.__class__ == Product:
        # Leibniz rule
        elt_0 = Element(
            [
                node_0.next_0
            ]
        )
        elt_1 = Element(
            [
                node_0.next_1
            ]
        )
        elt_list = [
            Product_func(
                Browder_func(
                    node_1,
                    node_0.next_0
                ),
                elt_1
            ),
            Product_func(
                elt_0,
                Browder_func(
                    node_1,
                    node_0.next_1
                )
            )
        ]
        return elt_sum( elt_list )

    if node_1.__class__ == Product:
        # Leibniz rule
        elt_0 = Element(
            [
                node_1.next_0
            ]
        )
        elt_1 = Element(
            [
                node_1.next_1
            ]
        )
        elt_list = [
            Product_func(
                Browder_func(
                    node_0,
                    node_1.next_0
                ),
                elt_1
            ),
            Product_func(
                elt_0,
                Browder_func(
                    node_0,
                    node_1.next_1
                )
            )
        ]
        return elt_sum( elt_list )

    if node_0.__class__ in { Browder, Generator } and node_1.__class__ in { Browder, Generator }:
        
        index_0, index_1 = browder_order.index( node_0 ), browder_order.index( node_1 )

        if index_0 > index_1:
            return Browder_func( node_1, node_0 )

        if node_1.__class__ == Browder:
            index_1_0 = browder_order.index( node_1.next_0 )
            if index_1_0 > index_0:
                elt_list = [
                    Browder_func(
                        Element(
                            [
                                node_1.next_0
                            ]
                        ),
                        Browder_func(
                            node_0,
                            node_1.next_1
                        )
                    ),
                    Browder_func(
                        Element(
                            [
                                node_1.next_1
                            ]
                        ),
                        Browder_func(
                            node_0,
                            node_1.next_0
                        )
                    ),
                ]
                return elt_sum( elt_list )
                

        
        elt = Element(
            [
                Browder(
                    node_0,
                    node_1
                )
            ]
        )
        return elt

    raise Exception

def Operation_func( i, node ):
    if node.__class__ == Element:
        if not node.nodes:
            return Element([])
            
        if i == n-1:
            # Top additivity
            if len( node.nodes ) == 1:
                elt = Operation_func( i, node.nodes[0] )
                return elt
            elt_list = [
                Operation_func( 
                    i, 
                    node.nodes[0],
                ),
                Operation_func( 
                    i, 
                    Element( node.nodes[1:] ),
                ),
                Browder_func( 
                    Element( 
                        [ 
                            node.nodes[0] 
                        ] 
                    ), 
                    Element( 
                        node.nodes[1:] 
                    )  
                )
            ]
        # Additivity
        elt_list = [ 
            Operation_func( 
                i, 
                _node
                ) 
            for _node in node.nodes 
            ]
        return elt_sum( elt_list )

    if i < 0:
        return Element([])

    if node.__class__ == Operation:
        if i <= node.power:
            elt = Element(
                [
                    Operation(
                        i,
                        node
                    )
                ]
            )
            return elt
        # adem relation
        elt_list = [
            Operation_func(
                a,
                Operation_func(
                    b,
                    node.next
                )
            )
            for ( a, b ) in adem( i, node.power )
        ]
        return elt_sum( elt_list )

    if node.__class__ == Product:
        # Cartan formula
        elt_list = [
            Product_func(
                Operation_func(
                    a,
                    node.next_0
                ),
                Operation_func(
                    b,
                    node.next_1
                )
            )
            for ( a, b ) in cartan( i )
        ]
        if i == n-1:
            # Top Cartan formula
            elt_0 = Element(
                [
                    node.next_0
                ]
            )
            elt_1 = Element(
                [
                    node.next_1
                ]
            )
            top_elt = Product_func(
                elt_0,
                Product_func(
                    Browder_func(
                        node.next_0,
                        node.next_1,
                    ),
                    elt_1
                )
            )
            elt_sum.append( top_elt )

        return elt_sum( elt_list )
    
    if node.__class__ in { Browder, Generator}:
        elt = Element(
            [
                Operation(
                    i,
                    node
                )
            ]
        )
        return elt
    
    raise Exception

def Browder_Basis_func():
    generators = [ Generator( i, d ) for i, d in enumerate( base_degs ) ]
    weight = 1
    while weight < max_weight:
        brackets = []
        weight += 1

        for index_1, node_1 in enumerate( generators ):
            for index_0, node_0 in enumerate( generators[:index_1] ):
                # check dimension
                if node_0.degree + node_1.degree + n-1 > max_dim:
                    continue

                # check weight
                if node_0.weight + node_1.weight != weight:
                    continue

                # check jacobi
                if node_1.__class__ == Product:
                    index_1_0 = generators.index( node_1.next_0 )
                    if index_1_0 > index_0:
                        continue
                brackets.append( Browder( node_0, node_1 ) )
        generators.extend( brackets )

    return generators

def Operation_Basis_func( generators ):
    operations = generators.copy()
    while operations:
        new_operations = []
        for node in operations:       
            if 2*node.weight > max_weight:
                continue
            if node.__class__ == Operation:
                operations_list = [
                    Operation(
                        power,
                        node
                    )
                for power in range( 0, min( [ n - 1, max_dim - 2*node.degree, node.power ] ) + 1 )
                ]
            else:
                operations_list = [
                    Operation(
                        power,
                        node
                    )
                for power in range( 0, min( [ n - 1, max_dim - 2*node.degree] ) + 1 )
                ]
            new_operations.extend( operations_list )
        generators.extend( new_operations )
        operations = new_operations.copy()
    return generators

def Product_Basis_func( operation_order ):
    generators = operation_order.copy()
    products = operation_order.copy()
    while products:
        new_products = []
        for node in products:
            for index, operation in enumerate( operation_order ):
                if operation.degree + node.degree > max_dim:
                    continue
                if operation.weight + node.weight > max_weight:
                    continue
                if node.__class__ in { Operation, Generator, Browder }:
                    if index > operation_order.index( node ):
                        new_product = Product(
                            operation,
                            node
                        )
                        new_products.append( new_product )
                
                if node.__class__ == Product:
                    if index > operation_order.index( node.next_0):
                        new_product = Product(
                            operation,
                            node
                        )
                        new_products.append( new_product )
        generators.extend( new_products )
        products = new_products.copy()
    return generators

def monomials_to_data( monomials ):
    min_deg = min( [ mon.degree for mon in monomials ] )
    data_list = [ {'name': node.output_str(), 'deg': node.degree, 'ops': {}} for node in monomials ]
    for ind, node in enumerate( monomials ):
        print( f'ops on monomial {ind}: {node}' )
        for i in range( 1, node.degree - min_deg + 1 ):
            sq_list = []
            for _node in Steenrod( i, node ).nodes:
                index = monomials.index( _node )
                print( f'   Sq_{i}: {_node}: {index}' )
                sq_list.append( index )
            if sq_list:
                data_list[ind]['ops'][i] = sq_list

    data = { 'gens': data_list }
    return data

browder_order = Browder_Basis_func(  )
operation_order = Operation_Basis_func( browder_order )
monomials = Product_Basis_func( operation_order )[ len( base_degs): ]
data = monomials_to_data( monomials )

# save as output.json in the current directory
with open('output.json', 'w') as file:
    _data = json.dumps(data, indent=2)
    file.write(_data)
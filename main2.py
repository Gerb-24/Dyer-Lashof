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

class Operation():
    def __init__(self, power, node) -> None:
        self.power = power
        self.next = node
        self.degree = power + node.degree - 1
        self.weight = 2*node.weight
    
    def __str__(self) -> str:
        return f'Q^{self.power}({self.next})'

    def __eq__(self, __o: object) -> bool:
        return self.power == __o.power and self.next == __o.next

class Product():
    def __init__(self, node_0, node_1) -> None:
        self.next_0 = node_0
        self.next_1 = node_1
        self.degree = node_0.degree + node_1.degree - 1
        self.weight = node_0.weight + node_1.weight
    
    def __str__(self) -> str:
        return f'[{self.next_0},{self.next_1}]'
    
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
    
    def __eq__(self, __o: object) -> bool:
        return self.__class__ == __o.__class__ and self.index == __o.index

class Element():
    def __init__(self, nodes) -> None:
        self.nodes = nodes
    
    def __str__(self) -> str:
        nodes_str = '+'.join( node.__str__() for node in self.nodes )
        return nodes_str

file = 'M2'
max_dim = 10
max_weight = 5

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
            for ( a, b ) in nishida( i, node.power )
        ]
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
    
    if node_0.__class__ == Operation or node_1.__class__ == Operation:
        return Element([])
    
    if node_0.__class__ in { Product, Generator } and node_1.__class__ in { Product, Generator }:
        if node_0 == node_1:
            elt = Element(
                [
                    Operation(
                        node_0.degree,
                        node_0
                    )
                ]
            )
            return elt
        
        index_0, index_1 = bracket_order.index( node_0 ), bracket_order.index( node_1 )

        if index_0 > index_1:
            return Product_func( node_1, node_0 )

        if node_1.__class__ == Product:
            index_1_0 = bracket_order.index( node_1.next_0 )
            if index_1_0 > index_0:
                elt_list = [
                    Product_func(
                        Element(
                            [
                                node_1.next_0
                            ]
                        ),
                        Product_func(
                            node_0,
                            node_1.next_1
                        )
                    ),
                    Product_func(
                        Element(
                            [
                                node_1.next_1
                            ]
                        ),
                        Product_func(
                            node_0,
                            node_1.next_0
                        )
                    ),
                ]
                return elt_sum( elt_list )
                

        else:
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

def Operation_func( i, node ):
    if node.__class__ == Element:
        # additivity
        elt_list = [ 
            Operation_func( 
                i, 
                _node
                ) 
            for _node in node.nodes 
            ]
        return elt_sum( elt_list )

    if i < node.degree:
        return Element([])

    if node.__class__ == Operation:
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

    if node.__class__ == Product or node.__class__ == Generator:
        elt = Element(
            [
                Operation(
                    i,
                    node
                )
            ]
        )
        return elt


def elt_sum():
    return

def cartan():
    return

def nishida():
    return

def adem():
    return


def Product_Basis_func():
    generators = [ Generator( i, d ) for i, d in enumerate( base_degs ) ]
    weight = 1
    while weight < max_weight:
        brackets = []
        weight += 1

        for index_1, node_1 in enumerate( generators ):
            for index_0, node_0 in enumerate( generators[:index_1] ):
                # check dimension
                if node_0.degree + node_1.degree - 1 >= max_dim:
                    continue

                # check weight
                if node_0.weight + node_1.weight != weight:
                    continue

                # check jacobi
                if node_1.__class__ == Product:
                    index_1_0 = generators.index( node_1.next_0 )
                    if index_1_0 > index_0:
                        continue
                brackets.append( Product( node_0, node_1 ) )
        generators.extend( brackets )

    return generators

def Operation_Basis_func():
    generators = bracket_order
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
                for power in range( 2*node.power + 1, max_dim - node.degree )
                ]
            else:
                operations_list = [
                    Operation(
                        power,
                        node
                    )
                for power in range( node.degree, max_dim - node.degree )
                ]
            new_operations.extend( operations_list )
        generators.extend( new_operations )
        operations = new_operations.copy()
    return generators

bracket_order = Product_Basis_func()
monomials = Operation_Basis_func()[len(base_degs):]


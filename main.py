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


def create_unary_node( degree_func, output_tex_func ):
    class UnaryNode():
        def __init__(self, power, node) -> None:
            self.power = power
            self.next = node
            self.degree = degree_func( power, node.degree )
            self.weight = 2*node.weight

        def __str__(self) -> str:
            return output_tex_func( self.power, str( self.next ) )

        def __eq__(self, __o: object) -> bool:
            return self.__class__ == __o.__class__  and self.power == __o.power and self.next == __o.next

    return UnaryNode

def create_binary_node( degree_func, output_tex_func ):
    class BinaryNode():
        def __init__(self, node_0, node_1) -> None:
            self.next_0 = node_0
            self.next_1 = node_1
            self.degree = degree_func( node_0.degree, node_1.degree )
            self.weight = node_0.weight + node_1.weight
        
        def __str__(self) -> str:
            return output_tex_func( str( self.next_0 ), str( self.next_1 ) )
        
        def __eq__(self, __o: object) -> bool:
            return self.__class__ == __o.__class__ and self.next_0 == __o.next_0 and self.next_1 == __o.next_1

    return BinaryNode

NodeTypes = {
    'Operation':    create_unary_node(
        lambda x,y: x+y-1,                  # degree_func
        lambda x,y: f'Q^{x}({y})'           # output_tex_func
        ),
    'Product' :     create_binary_node(
        lambda x,y: x+y-1,                  # degree_func
        lambda x,y: f'[{x},{y}]'            # output_tex_func
    )
}

def operad( file, max_dim, max_weight ):
    base_module = F2_Module( f'json_files/{file}.json' )
    base_degs = base_module.degs
    base_ops = base_module.ops

    def unary_basis_func( generators, range_func, adem_bool ):
        unaries = generators.copy()
        prev_unaries = unaries.copy()
        while prev_unaries:
            cur_unaries = []
            for node in prev_unaries:
                for power in range_func( node.degree, max_dim ):
                    if 2*node.weight > max_weight:
                        continue
                    if node.__class__ == NodeTypes['Operation']:
                        if adem_bool( power, node.power ):
                            continue
                    cur_unaries.append(
                        NodeTypes['Operation'](
                            power,
                            node
                        )
                    )
            unaries.extend( cur_unaries )
            prev_unaries = cur_unaries.copy()
        return unaries
    
    def binary_basis_func( generators ):
        binaries = generators.copy()
        prev_binaries = binaries.copy()
        while prev_binaries:
            cur_binaries = []
        return binaries

    generators = [ Generator( i, d ) for i, d in enumerate( base_degs ) ]
    operations = unary_basis_func( 
        generators, 
        lambda d, max_d: range( d, max_d-d ),       # range_func
        lambda i,j: i > 2*j                         # adem_bool
    )

    for op in operations:
        print(op)

file = 'M2'
max_dim = 10
max_weight = 5
operad( file, max_dim, max_weight )





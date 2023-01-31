

class Generator:
    def __init__(self, s) -> None:
        self.string = s
        self.weight = 1
    
    def __str__(self) -> str:
        return self.string
    
    def __eq__(self, __o: object) -> bool:
        return self.__class__ == __o.__class__ and self.string == __o.string  

class ProductNode:
    def __init__(self, next_0, next_1) -> None:
        self.next_0 = next_0
        self.next_1 = next_1
        self.weight = next_0.weight + next_1.weight
        self.neighbours = []

    def get_neighbours( self, free_list ):
        neighbours = []

        # Commutativity
        new_node = ProductNode( self.next_1, self.next_0 )
        index = free_list.index( new_node )
        neighbours.append( index )
        
        # Associativity
        if self.next_0.__class__ == ProductNode:
            new_node = ProductNode(
                self.next_0.next_0,
                ProductNode(
                    self.next_0.next_1,
                    self.next_1
                )
            )
            index = free_list.index( new_node )
            neighbours.append( index )

        if self.next_1.__class__ == ProductNode:
            new_node = ProductNode(
                ProductNode(
                    self.next_0,
                    self.next_1.next_0
                ),
                self.next_1.next_1
            )
            index = free_list.index( new_node )
            neighbours.append( index )
        
        self.neighbours = neighbours

    def __str__(self) -> str:
        return f'[{self.next_0},{self.next_1}]'

    def __eq__(self, __o: object) -> bool:
        return self.__class__ == __o.__class__ and self.next_0 == __o.next_0 and self.next_1 == __o.next_1

'''generate a list of free products over the generators'''
def product_basis_func( generators, max_weight ):
    products = generators.copy()
    prev_products = products.copy()
    while prev_products:
        cur_products = []
        for prod in prev_products:
            for _prod in products:
                if products.index(prod) <= products.index(_prod):
                    continue
                # check weight
                if prod.weight + _prod.weight > max_weight:
                    continue
                cur_products.append(
                    ProductNode( prod, _prod )
                )
                cur_products.append(
                    ProductNode( _prod, prod )
                )
        products.extend( cur_products )
        prev_products = cur_products.copy()
    return products

generators = [ 'a', 'b', 'c' ]
generators = [ Generator( s ) for s in generators  ]
products = product_basis_func( generators, 4 )
prod = products[260]
print(prod)
# test_node = ProductNode( 'a', ProductNode( 'b', 'c' ) )
# print( test_node.neighbours )

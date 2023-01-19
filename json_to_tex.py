import json

filename = 'output.json'
with open(filename, 'r') as file:
    data = json.load(file)

gens = data['gens']


min_deg = min( [gen['deg'] for gen in gens ] )
max_deg = max( [gen['deg'] for gen in gens] )
cols = max_deg - min_deg + 1

# sort by degrees
deg_data = {}
for gen in gens:
    if gen['deg'] in deg_data:
        deg_data[gen['deg']].append( gen['name'] )
    else:
        deg_data[gen['deg']] = [ gen['name'] ]

rows = max( len(  deg_data[deg] ) for deg in deg_data  )

# give coord to each string
coords = {}
for deg in deg_data:
    for i, s in enumerate( deg_data[deg] ):
        coords[s] = [ deg - min_deg , i ]

dual_coords = {}
for s in coords:
    coord = coords[s]
    dual_coords[ str( coord ) ] = s

# for coord in dual_coords:
#     print( f'{coord} : {dual_coords[coord]}' )

r_strings = []
for r in range(rows):
    c_strings = []
    for c in range(cols):
        
        if str( [c, r] ) in dual_coords:

            s = dual_coords[ str( [c,r] ) ]
        else:
            s = ''
        c_strings.append(s)
    s = ' & '.join( c_strings )
    if r == rows - 1:
         r_strings.append( s )
    else:
        r_strings.append( s + r'\\' )

tot_gen_s = '\n'.join( r_strings )

op_strings_dic = {}
for gen in gens:
    _c,_r = coords[ gen['name'] ]
    ops =  gen['ops']
    for pow in ops:
        for i in ops[pow]:
            c,r = coords[ gens[i]['name'] ]
            if pow == '1':
                s = f'''\\arrow["\\Sq_{pow}"{{description}},from={_r+1}-{_c+1}, to={r+1}-{c+1}]'''
            else:
                s = f'''\\arrow["\\Sq_{pow}"{{description}},curve={{height=12pt}},from={_r+1}-{_c+1}, to={r+1}-{c+1}]'''
            if pow in op_strings_dic:
                op_strings_dic[pow].append( s )
            else:
                op_strings_dic[pow] = [ s ]

ans_list = []
for pow in op_strings_dic:
    pow_text = f'The dual Steenrod operations for $i={pow}$'
    tot_op_s = '\n'.join( op_strings_dic[pow] )
    ans = f'''
\\begin{{tikzcd}}
{tot_gen_s}
{tot_op_s}
\end{{tikzcd}}'''
    ans_list.append( ans )

tot_ans = '\n\n'.join( ans_list ) 

with open('output.tex', 'w') as file:
    file.write( tot_ans )
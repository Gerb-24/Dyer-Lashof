import json
dirname = 'json_files/'
filename = 'Brow'

def get_lines(file, line_numbers):
    return (x for i, x in enumerate(file) if i in line_numbers)

with open( f'{dirname}{filename}.txt', 'r' ) as file:
    num_lines = sum(1 for line in file)
    line_indeces = [2]
    line_indeces.extend( range( 4, num_lines ) )

with open( f'{dirname}{filename}.txt', 'r' ) as file:
    lines = get_lines( file, line_indeces )
    _lines = []
    for line in lines:
        _lines.append(line.strip())
str_gens = _lines[0].split(' ')

data = { 'gens':[] }
for x in str_gens:
    data['gens'].append({ 'deg': int(x), 'ops': {} })

pre_ops = _lines[1:]
str_ops = [ op.split(' ') for op in pre_ops ]
for x in str_ops:
    data['gens'][int(x[0])]['ops'][int(x[1])] = [int(y) for y in x[3:]]


with open( f'{dirname}{filename}.json', 'w' ) as f:
    json.dump( data, f, indent=2 )

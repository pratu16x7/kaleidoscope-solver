# The most basic representations:
# Either a plain 1D coord + data list
# Or a 2D with just data, no coords (because the indices of the 2d elements IS the coords)

SHAPE_COORD_LIMIT = 3
    
def gen_windows_for_boundary(pattern, which_boundary):
    """
    All, top left right and bottom boundaries
    """
    pass
    
def get_no_of_windows_for_boundary(pattern, which_boundary):
    pass
    
def gen_window_for_coord(coord):
    """
    ???
    """
    pass
    
def calc_shape_score_for_window(window, shape):
    pass
    
shapes = {
    'l-top-left-long': [ [0,0], [0,1], [1,0], [2,0] ],
    'l-top-right-long': [ [0,0], [0,1], [1,1], [2,1] ],
    'l-bottom-right-wide': [ [0,2], [1,0], [1,1], [1,2] ],
    't-up': [ [0,1], [1,0], [1,1], [1,2] ],
    't-left': [ [0,1], [1,0], [1,1], [2,1] ],
    'z-left': [ [0,0], [0,1], [1,1], [1,2] ],
    'z-right': [ [0,1], [0,2], [1,0], [1,1] ],
    'square': [ [0,0], [0,1], [1,0], [1,1] ],
}

pattern1 = [ [0,0], [0,1], [0,2], [0,3], [1,0], [1,3], [2,0], [2,3] ]

pattern2 = [ 
    [0,0], [0,1], [0,2], [0,3], 
    [1,0], [1,1], [1,2], [1,3], 
    [2,0], [2,1], [2,2], [2,3] 
]
    
def print_pattern(points):
    height = max([p[0] for p in points]) + 1
    length = max([p[1] for p in points]) + 1
    coords = points
    for i in range(height):
        row_points = [p for p in coords if p[0] == i]
        s = ''
        for j in range(length):
            if [i, j] in row_points:
                s += ' ▢'
            else:
                s += '  '
        print(s)  
    
def gen_edges(points):
    obj_grid = []
    prev_blocks = []
    prev_coords = []
    
    height = max([p[0] for p in points]) + 1
    length = max([p[1] for p in points]) + 1
    
    for i in range(height):
        blocks = [] 
        
        row_edge = ''
        if i == 0:
            row_edge = 'u'
        elif i == height - 1:
            row_edge = 'd'
            
        row_coords = [p for p in points if p[0] == i]
        
        if prev_blocks:
            for block in prev_blocks:
                down_coord = block['coord'][:]
                down_coord[0] = i
                if down_coord not in row_coords:
                    block['edges'].append('d')
        
        coords_parsed = 0
        prev = None
        for j in range(length):
            coord = [i, j]
            if coord in row_coords:
                
                edges = []
                if row_edge:
                    edges.append(row_edge)
                    
                if prev_coords:
                    up_coord = coord[:]
                    up_coord[0] -= 1
                    if up_coord not in prev_coords:
                        edges.append('u')
                    
                if not prev:
                    edges.append('l')
                
                coords_parsed += 1
                if coords_parsed == len(row_coords):
                    edges.append('r') 
                
                blocks.append({
                    'coord': coord,
                    'edges': edges
                })
                
                prev = coord
            else:
                if blocks:
                    last_edges = blocks[-1]['edges']
                    if 'r' not in last_edges:
                        last_edges.append('r')
                    prev = None
                
        obj_grid.append(blocks)
        prev_blocks = blocks
        prev_coords = row_coords
        
    return obj_grid

    
for s in shapes:
    print(s)
    print_pattern(shapes[s])
    print(gen_edges(shapes[s]))
    print('')
    

print_pattern(pattern1)
print('')
print_pattern(pattern2)

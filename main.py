# The most basic representations:
# Either a plain 1D coord + data list
# Or a 2D with just data, no coords (because the indices of the 2d elements IS the coords)

# You HAVE to implement a binary tree
# And you have to figure out how to know that the run failed

# Start with the most crooked oedge of a shape first, the one with the most delta.
# Straight smooth edges have very little information

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
    

    
shapes = {
    'l-top-left-long': [ [0,0], [0,1], [1,0], [2,0] ],
    'l-top-right-long': [ [0,0], [0,1], [1,1], [2,1] ],
    'l-bottom-right-wide': [ [0,2], [1,0], [1,1], [1,2] ],
    't-up': [ [0,1], [1,0], [1,1], [1,2] ],
    't-left': [ [0,1], [1,0], [1,1], [2,1] ],
    'z-left': [ [0,0], [0,1], [1,1], [1,2] ],
    'z-right': [ [0,1], [0,2], [1,0], [1,1] ],
    'square': [ [0,0], [0,1], [1,0], [1,1] ]
}

pattern1 = [ [0,0], [0,1], [0,2], [0,3], [1,0], [1,3], [2,0], [2,3] ]

pattern2 = [ 
    [0,0], [0,1], [0,2], [0,3], 
    [1,0], [1,1], [1,2], [1,3], 
    [2,0], [2,1], [2,2], [2,3] 
]

def get_shape_scores_window(window):
    window_grid = gen_edges(window)

    for s in shapes:
        # s = 'l-bottom-right-wide'
        score = is_shape_inside_window(window, shapes[s])
        if score:
            print(s)
            print_pattern(shapes[s])
            
            shape_grid = gen_edges(shapes[s])
            edge_scores = calc_edges_score(window_grid, shape_grid)
            
            print(edge_scores)
            print('')
            
            
def calc_edges_score(window_grid, shape_grid):
    shape_edges_count = 0
    matched_edges_count = 0
    window_edges_count = 0 
             
    for row in window_grid:
        for block in row:
            if block:
                window_edges_count += len(block['edges'])
                if len(shape_grid[0]) >= block['coord'][1] + 1:
                    # TODO: needs custom rules for how a square 
                    # (or a smaller piece than window) 
                    # should be placed
                    # And also rotation should be factored in
                    shape_block = shape_grid[block['coord'][0]][block['coord'][1]]
                    if shape_block:
                        s_edge_set = set(shape_block['edges'])
                        w_edge_set = set(block['edges'])
            
                        shape_edges_count += len(shape_block['edges'])
                        common_edges = list(w_edge_set.intersection(s_edge_set))
                        print(common_edges)
                        matched_edges_count += len(common_edges)
    return {
        'shape_edges': shape_edges_count,
        'window_edges': window_edges_count,
        'matched_edges': matched_edges_count,
        
        'window_edge_match': matched_edges_count/window_edges_count,
        'shape_edge_match': matched_edges_count/shape_edges_count
    }


def is_shape_inside_window(window, shape):
    window_set = set([str(p[0]) + str(p[1]) for p in window])
    shape_set = set([str(p[0]) + str(p[1]) for p in shape])

    is_present = shape_set.issubset(window_set)
    
    if is_present:
        return {
            'boundary_matches': [5,10],
            'edge_touching_blocks': [3, 4],
            'is_rare_shape': 0
        }
    
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
        all_blocks = []
        
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
                
                block = {
                    'coord': coord,
                    'edges': edges
                }
                
                all_blocks.append(block)
                blocks.append(block)
                
                prev = coord
            else:
                if blocks:
                    last_edges = blocks[-1]['edges']
                    if 'r' not in last_edges:
                        last_edges.append('r')
                    prev = None
                    
                # TODO: use all blocks for real to check up and down everything
                # Your losing much information in the current implementation adn running 
                # too many checks for up and down edge checks
                
                all_blocks.append(None)
                
        obj_grid.append(all_blocks)
        prev_blocks = blocks
        prev_coords = row_coords
        prev_coords = row_coords
        
    return obj_grid

print_pattern([ [0,1], [1,0], [1,1], [1,2] ])
get_shape_scores_window([ [0,1], [1,0], [1,1], [1,2] ])
print_pattern([ [0,1], [0,2], [1,0], [1,1], [1,2] ])
get_shape_scores_window([ [0,1], [0,2], [1,0], [1,1], [1,2] ])
print_pattern([ [0,0], [0,1], [0,2], [1,0], [1,1], [1,2] ])
get_shape_scores_window([ [0,0], [0,1], [0,2], [1,0], [1,1], [1,2] ])



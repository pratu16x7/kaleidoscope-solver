# The most basic representations:
# Either a plain 1D coord + data list
# Or a 2D with just data, no coords (because the indices of the 2d elements IS the coords)

# You HAVE to implement a binary tree
# And you have to figure out how to know that the run failed

# Start with the most crooked oedge of a shape first, the one with the most delta.
# Straight smooth edges have very little information

SHAPE_COORD_LIMIT = 3
HORI_WINDOW_SIZE = [3,2]
VERT_WINDOW_SIZE = [2,3]

ROT_90_EDGE_MAP = {
    'u': 'l',
    'l': 'd',
    'd': 'r',
    'r': 'u'
}

OPP_EDGES_MAP = {
    'u': 'd',
    'd': 'u',
    'l': 'r',
    'r': 'l'
}

EDGE_OPNS = {
    'u': [-1, 0],
    'd': [1, 0],
    'l': [0, -1],
    'r': [0, 1],
}

    
SHAPES = {
    'l-left': {
        'name': 'l-left',
        'coords': [ [0,0], [1,0], [1,1], [1,2] ],
        'rare': 0
    },
    'l-right': {
        'name': 'l-right',
        'coords': [ [0,2], [1,0], [1,1], [1,2] ],
        'rare': 0
    },
    't': {
        'name': 't',
        'coords': [ [0,1], [1,0], [1,1], [1,2] ],
        'rare': 1
    },
    'z-left': {
        'name': 'z-left',
        'coords': [ [0,0], [0,1], [1,1], [1,2] ],
        'rare': 1
    },
    'z-right': {
        'name': 'z-right',
        'coords': [ [0,1], [0,2], [1,0], [1,1] ],
        'rare': 1
    }
}

pattern1 = [ [0,0], [0,1], [0,2], [0,3], [1,0], [1,3], [2,0], [2,3] ]

pattern2 = [ 
    [0,0], [0,1], [0,2], [0,3], 
    [1,0], [1,1], [1,2], [1,3], 
    [2,0], [2,1], [2,2], [2,3] 
]

windowable_pattern1 = [ 
    [0,0], [0,1], [0,2], [0,3], 
    [1,0], [1,1], [1,2], [1,3], 
    [2,0], [2,1], [2,2], [2,3],
    [3,0], [3,1], [3,2],
           [4,1]
]

def get_shape_scores_window(window_grid, shapes=SHAPES.values()):
    all_scores = []
    
    for shape in shapes:
        name = shape['name']
        coords = shape['coords']
        score = is_shape_inside_window(get_coords_from_grid(window_grid), coords)
        shape_grid = gen_obj_grid(coords)
        
        if score:
            # print(name)
#             print_pattern(coords)
            
            edge_score = calc_edges_score(window_grid, shape_grid)
            
            edge_score['shape'] = name
            edge_score['rot'] = 0
            edge_score['rare'] = shape['rare']
            
            all_scores.append(edge_score)
        
        rotated_180_shape_grid = get_180_rotated(shape_grid)
        if is_shape_inside_window(get_coords_from_grid(window_grid), get_coords_from_grid(rotated_180_shape_grid)):
                        #
            # print('ROT')
            #
            # print_pattern(get_coords_from_grid(rotated_180_shape_grid))
        
            edge_score = calc_edges_score(window_grid, rotated_180_shape_grid)
            edge_score['shape'] = name
            edge_score['rot'] = 1
            edge_score['rare'] = shape['rare']
            
            all_scores.append(edge_score)
            
    return all_scores
            
def calc_edges_score(window_grid, shape_grid):
    shape_edges_count = 0
    matched_edges_count = 0
    window_edges_count = 0 
    
    # just to track TODO: remove
    common_edges_list = []
             
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
                        
                        # just to track TODO: remove
                        common_edges_list.append(common_edges) 
                        
                        matched_edges_count += len(common_edges)
                        
              
    w_match = matched_edges_count/window_edges_count 
    s_match = matched_edges_count/shape_edges_count   
      
    return {
        'SE': shape_edges_count,
        'WE': window_edges_count,
        'ME': matched_edges_count,
        
        'W_MATCH': w_match,
        'S_MATCH': s_match,
        
        'W_X_S': w_match * s_match,
        
        'common_edges': common_edges_list
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
        
def get_coords_from_grid(grid):
    coords = []
    for row in grid:
        for block in row:
            if block:
                coords.append(block['coord'])
    return coords
    
    
# TODO: this repeats obj_grid's work
# abstract out taking care of null blocks
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
        
# def print_pattern_with_edges():
#     height =
    
    
def gen_obj_grid(points):
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
    
    
def get_window(patt, coord, size):
    l, h = size
    y0, x0 = coord
    
    import copy

    def offset_coords(row):
        new_row = []
        for block in row:
            b = None
            if block:
                b = copy.copy(block)
                c = b['coord']
                b['coord'] = [c[0] - y0, c[1] - x0]
            new_row.append(b)
        return new_row
        
    window_grid = [offset_coords(patt[row_no][x0:x0+l]) for row_no in range(y0, y0+h)]
    return {
        'grid': window_grid,
        'coord': coord
    }
    
    
def get_90_rotated(patt):
    l = len(patt[0])
    h = len(patt)
    
    import copy
    
    rotated_patt = []
    
    ir = 0
    for i in range(l-1, -1, -1):  
      row = []
      jr = 0
      
      for j in range(h):
        b = copy.copy(patt[j][i])
        if b:
            b['coord'] = [ir, jr]
            b['edges'] = [ROT_90_EDGE_MAP[e] for e in b['edges']]
        row.append(b)
        jr += 1
        
      rotated_patt.append(row)
      ir += 1
      
    return rotated_patt
    
    
def get_180_rotated(patt):
    l = len(patt[0])
    h = len(patt)
    
    import copy
    
    rotated_patt = []
    
    ir = 0
    for i in range(h - 1, -1, -1):
        row = []
        jr = 0
        
        for j in range(l - 1, -1, -1):
            b = copy.copy(patt[i][j])
            if b:
                b['coord'] = [ir, jr]
                b['edges'] = [OPP_EDGES_MAP[e] for e in b['edges']]
            row.append(b)
            jr += 1

        rotated_patt.append(row)
        ir += 1

    return rotated_patt
    

def get_x_direction_windows(patt):
    l = len(patt[0])
    h = len(patt)
    
    # [0, 0], [0, 1]
    # [3, 0], [3, 1]
    w_size = HORI_WINDOW_SIZE 
  
    wl, wh = w_size
  
    c_range = range(l - wl + 1) 
    offset_c = h - wh
  
    start_coords = [[0, c] for c in c_range]
    end_coords = [[offset_c, c] for c in c_range]
    
    # TODO: shift window down if >= half empty
  
    windows = [get_window(patt, c, w_size) for c in start_coords + end_coords]

    return windows


def get_all_options(patt, shapes):
    options = []
    patt_windows = get_x_direction_windows(patt)
    
    for w in patt_windows:
        win = w['grid']
        
        scores = get_shape_scores_window(win, shapes)
        
        if scores:
            option = sorted(scores, key=lambda x: x['W_MATCH'], reverse=True)[0]
            option['coord'] = w['coord']
            options.append(option)
    
    return options
    
    
def solve(patt_values, shapes_set=None):
    solution = []
    
    shapes = SHAPES.values()
    if shapes_set:
        shapes = [s for s in SHAPES if s['name'] in shapes_set]
    
    # current_hole = [1]
    patt = gen_obj_grid(patt_values)
    print_pattern(get_coords_from_grid(patt))
    
    while patt:
        rotated_patt = get_90_rotated(patt)
        print_pattern(get_coords_from_grid(rotated_patt))
    
        patt_options = get_all_options(patt, shapes)
        rot_patt_options = get_all_options(rotated_patt, shapes)
    
        patt_opt = get_best_option(patt_options) if patt_options else None
        rot_patt_opt = get_best_option(rot_patt_options) if patt_options else None
    
        def fill(pattern, option):
            import copy
            patt_clone = copy.copy(pattern)
            solution.append(option)
            return fill_piece(patt_clone, option['coord'], option['shape'], option['rot'])
    
        if patt_opt and rot_patt_opt:
            if patt_opt['W_X_S'] > rot_patt_opt['W_X_S']:
                patt = fill(patt, patt_opt)
            else:
                patt = fill(rotated_patt, rot_patt_opt)
            
        elif patt_opt:
            patt = fill(patt, patt_opt)
        elif rot_patt_opt:
            patt = fill(rotated_patt, rot_patt_opt)
        else:
            # TODO: Something weird happened. Analyse and rerun.
            print_pattern(get_coords_from_grid(patt))
            break


        patt = get_trimmed_pattern(patt)
        print("NOW PATT")
        print_pattern(get_coords_from_grid(patt))
        print(patt)
    
    print('final_patt', patt)
    print(solution)
    
    
def get_best_option(options):
    return sorted(options, key=lambda x: x['W_X_S'], reverse=True)[0]
    
    
def fill_piece(patt, coord, shape, rotate=False):
    shape = SHAPES[shape]

    shape_grid = gen_obj_grid(shape['coords'])
    if rotate:
        shape_grid = get_180_rotated(shape_grid)
        
    for row in shape_grid:
        for block in row:
            
            if block:
                curr_coord = [block['coord'][0] + coord[0], block['coord'][1] + coord[1]]
                patt[curr_coord[0]][curr_coord[1]] = None
                edges = block['edges'] or []
                
                transfer_edges(patt, edges, curr_coord)

    return patt
    

def transfer_edges(patt, edges, curr_coord):
    """
        MUTATEs Pattern
    """
    l = len(patt[0])
    h = len(patt)
    for e in edges:
        opn = EDGE_OPNS[e]
        y = curr_coord[0] + opn[0]
        x = curr_coord[1] + opn[1]
        
        if y >=0 and x >= 0 and y < h and x < l:
            neighbour = patt[y][x]
            if neighbour:
                opp_edge = OPP_EDGES_MAP[e]
                if neighbour['edges']:
                    neighbour['edges'].append(opp_edge)
                else:
                    neighbour['edges'] = [opp_edge]
                    
                    
def get_trimmed_pattern(patt):
    current_patt = []
    
    for row in patt:
        if not all(x == None for x in row):
            current_patt.append(row)
    
    rotated = get_180_rotated(current_patt)
    
    current_patt = []
    for row in rotated:
        if not all(x == None for x in row):
            current_patt.append(row)
            
    return current_patt


solve(windowable_pattern1, [])


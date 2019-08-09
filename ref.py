 #   - -     -
 # | ▢ ▢ ▢ ▢ ▢
 # | ▢ ▢ - ▢ ▢ | -
 #   - -   - ▢ ▢ ▢
   
shapes = {
    'l-top-left-long': [ [0,0], [0,1], [1,0], [2,0] ],
    'l-top-right-long': [ [0,0], [0,1], [1,1], [2,1] ],
    't-left': [ [0,1], [1,0], [1,1], [2,1] ],
    # 'square': [ [0,0], [0,1], [1,0], [1,1] ]
}

def get_y_direction_windows():

    # [0, 0]     [0, 2]
    # [1, 0]     [1, 2]
    # [2, 0]     [2, 2]

    w_size = VERT_WINDOW_SIZE

    wl, wh = w_size

    c_range = range(h - wh + 1)
    offset_c = l - wl

    start_coords = [[c, 0] for c in c_range]
    end_coords = [[c, offset_c] for c in c_range]

    windows = [get_window(patt, c, w_size) for c in start_coords + end_coords]

    returnwindows


shapes = {
    'top-left-long-l': [
        {
            'coord': [0,0],
            'edges': ['u', 'l']
        },
        {
            'coord': [1,0],
            'edges': ['l', 'r']
        },
        {
            'coord': [2,0],
            'edges': ['l', 'r', 'd']
        },
        {
            'coord': [0,1],
            'edges': ['u', 'r', 'd']
        },
    ],
    
    'top-right-long-l': [
        {
            'coord': [0,0],
            'edges': ['l', 'u', 'd']
        },
        {
            'coord': [0,1],
            'edges': ['u', 'r']
        },
        {
            'coord': [1,1],
            'edges': ['l', 'r']
        },
        {
            'coord': [2,1],
            'edges': ['l', 'r', 'd']
        },
    ],
    
    'square': [
        {
            'coord': [0,0],
            'edges': ['l', 'u']
        },
        {
            'coord': [1,0],
            'edges': ['l', 'd']
        },
        {
            'coord': [0,1],
            'edges': ['u', 'r']
        },
        {
            'coord': [1,1],
            'edges': ['r', 'd']
        },
    ]
}

pattern1 = [
    [ [0,0], [0,1], [0,2], [0,3] ],
    [ [1,0],  None,  None, [1,3] ],
    [ [2,0],  None,  None, [2,3] ],
]

pattern2 = [
    [ [0,0], [0,1], [0,2], [0,3] ],
    [ [1,0], [1,1], [1,2], [1,3] ],
    [ [2,0], [2,1], [2,2], [2,3] ],
]

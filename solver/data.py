# # Never fear, you can always map into whatever you want
# # And even use it as direct source instead of intermediate
# # Just do the most condensed version, least redundant info now
# # How it will be stored, and How it will be displayed are anyway 2 different things
# # Pref horizontal over vertical
# # colors: r, b, y, x(black)
# # 'left' and 'right' char representations are not 'l' and 'r' as those are taken for shapes/colors
# #   can think of some chirality representation in general
# #   'left' identifies conventional orientation, and 'right' the opposite
# # All orients = 4 unless specified


PIECES = [
  # # octomino (8-0 deviation)
  {
    'name': 'magic_wand',
    'val': '00r01x02r03x04r05x06r07x',
  },
  
  
  # # tetrominoes
  
  # line (4-0 deviation)
  {
    'name': 'line4',
    'val': '00r01x02r03x'
  },
  
  # Ls (4-1-1 deviation)
  {
    'name': 'l4_left_r',
    'val': '00r10x11r12x'
  },
  {
    'name': 'l4_left_x',
    'val': '00x10r11x12r'
  },
  {
    'name': 'l4_right_r',
    'val': '02r10x11r12x'
  },
  {
    'name': 'l4_right_x',
    'val': '02x10r11x12r'
  },
  
  # Ts (4-1-2 deviation)
  {
    'name': 't_r',
    'val': '00r01x02r11r'
  },
  {
    'name': 't_x',
    'val': '00x01r02x11x'
  },
  
  # Zs (4-2-1 deviation)
  {
    'name': 'z_left',
    'val': '00r01x11r12x'
  },
  {
    'name': 'z_right',
    'val': '00x01r11x12r'
  },
  
  # Square (4-2-2 deviation)
  {
    'name': 'small_wand',
    'val': '00r01x10x11r',
    'positions': 2
  },
  
  
  # # triminoes
  
  # lines (3-0 deviation)
  {
    'name': 'line3_r',
    'val': '00r01x02r',
    'positions': 2
  },
  {
    'name': 'line3_x',
    'val': '00x01r02x',
    'positions': 2
  },
  
  # Ls (3-1-1 deviation)
  {
    'name': 'l3_r',
    'val': '00r10x11r'
  },
  {
    'name': 'l3_x',
    'val': '00x10r11x'
  },
  
  
  # # domino (singleton)
  {
    'name': 'dom',
    'val': '00r01x'
  },
  
  # # monominoes (singletons)
  {
    'name': 'mono_r',
    'val': '00r',
    'positions': 1
  },
  {
    'name': 'mono_x',
    'val': '00x',
    'positions': 1
  }
]

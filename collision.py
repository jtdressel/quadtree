import pygame
import numpy

### Naive ###

def rect_rects_any_naive( rect, list_of_rects ):
    ## Assume this is true:
    # group = list( group )
    
    for i, otherrect in enumerate( list_of_rects ):
        if rect.colliderect( otherrect ): return i
    
    return -1

def rect_rects_all_naive( rect, list_of_rects ):
    ## Assume this is true:
    # group = list( group )
    
    result = []
    for i, otherrect in enumerate( list_of_rects ):
        if rect.colliderect( otherrect ): result.append( i )
    
    return result

### pygame ###

def rect_rects_any_pygame( rect, list_of_rects ):
    return rect.collidelist( list_of_rects )

def rect_rects_all_pygame( rect, list_of_rects ):
    return rect.collidelistall( list_of_rects )

### bins ###

class Bins( object ):
    def __init__( self, world_rect, num_xbins, num_ybins ):
        
        self.world_rect = world_rect.copy()
        self.num_xbins = num_xbins
        self.num_ybins = num_ybins
        
        self.bins = []
        for x in num_xbins:
            self.bins.append( [] )
            for y in num_ybins:
                self.bins[-1].append( [] )
        
    def bin_xy_for_point( self, x, y ):
        assert x >= self.world_rect.left
        assert x < self.world_rect.right
        assert y >= self.world_rect.top
        assert y < self.world_rect.bottom
        
        x -= self.world_rect.left
        y -= self.world_rect.top
        
        return int( x / self.num_xbins ), int( y / self.num_ybins )
    
    def add_rect( self, rect, key ):
        leftbin, topbin = self.bin_xy_for_point( rect.left, rect.top )
        rightbin, bottombin = self.bin_xy_for_point( rect.right, rect.bottom )
        
        for bx in xrange( leftbin, rightbin+1 ):
            for by in xrange( topbin, bottombin+1 ):
                self.bins[ bx ][ by ].append( key )
    
    def keys_of_bins_for_rect( self, rect ):
        leftbin, topbin = self.bin_xy_for_point( rect.left, rect.top )
        rightbin, bottombin = self.bin_xy_for_point( rect.right, rect.bottom )
        
        keys = []
        for bx in xrange( leftbin, rightbin+1 ):
            for by in xrange( topbin, bottombin+1 ):
                keys.extend( self.bins[ bx ][ by ] )
        
        return list( frozenset( keys ) )

def rect_rects_any_bins( rect, list_of_rects, world_rect, num_xbins = 10, num_ybins = 10 ):
    ## Assume this is true:
    # group = list( group )
    
    bins = Bins( world_rect, num_xbins, num_ybins )
    
    for i, otherrect in enumerate( list_of_rects ):
        bins.add_rect( otherrect, i )
    
    possible_collisions = bins.keys_of_bins_for_rect( rect )
    return rect_rects_any_pygame( rect, [ list_of_rects[ i ] for i in possible_collisions ] )

def rect_rects_all_bins( rect, list_of_rects, world_rect, num_xbins = 10, num_ybins = 10 ):
    ## Assume this is true:
    # group = list( group )
    
    bins = Bins( world_rect, num_xbins, num_ybins )
    
    for i, otherrect in enumerate( list_of_rects ):
        bins.add_rect( otherrect, i )
    
    possible_collisions = bins.keys_of_bins_for_rect( rect )
    return rect_rects_all_pygame( rect, [ list_of_rects[ i ] for i in possible_collisions ] )

### four-pass ###

def rect_rects_all_fourpass( rect, list_of_rects ):
    ## Assume this is true:
    # group = list( group )
    
    extents = numpy.empty( ( len( list_of_rects ), 4 ), dtype = int )
    for i, otherrect in enumerate( list_of_rects ):
        extents[i,0] = otherrect.left
        extents[i,1] = otherrect.right
        extents[i,2] = otherrect.top
        extents[i,3] = otherrect.bottom
    
    tests = numpy.zeros( ( len( list_of_rects ), 4 ), dtype = bool )
    tests[:,0] = extents[:,0] > rect.right
    tests[:,1] = extents[:,1] < rect.left
    tests[:,2] = extents[:,2] > rect.bottom
    tests[:,3] = extents[:,3] < rect.top
    
    result = list( numpy.where( tests.all( axis = 1 ) )[0] )
    
    return result

### four-pass-filter ###

def rect_rects_all_fourpass_filter( rect, list_of_rects ):
    ## Assume this is true:
    # group = list( group )
    
    maybe = [ i for i, otherrect in enumerate( list_of_rects ) if otherrect.left < rect.right ]
    maybe = [ i for i in maybe if list_of_rects[i].right > rect.left ]
    maybe = [ i for i in maybe if list_of_rects[i].top < rect.bottom ]
    maybe = [ i for i in maybe if list_of_rects[i].bottom > rect.top ]
    
    return maybe

### blitting ###

def rect_rects_some_blitting( rect, list_of_rects ):
    ## Assume this is true:
    # group = list( group )
    
    ## We can only handle less than 2^23 rects.
    assert len( list_of_rects ) < ( 1 << 23 )
    
    ## Create a surface the size of 'rect'
    surf = pygame.Surface( ( rect.width, rect.height ) )
    ## Fill it with zeros at first.
    surf.fill( ( 0, 0, 0 ) )
    ## Fill every other rect with a unique color.
    for i, otherrect in enumerate( list_of_rects ):
        rgb = ( (i+1) >> 16 ), ( ( (i+1) & 0x00F0 ) >> 8 ), ( (i+1) & 0x000F )
        surf.fill( rgb, otherrect.move( -rect.left, -rect.top ) )
    
    ## Extract the drawn colors
    view = surf.get_view( '3' )
    result = set()
    for column in view:
        for color in column:
            result.add( tuple( color ) )
    
    ## Remove the zero-color.
    result.remove( ( 0,0,0 ) )
    
    ## If any colors are left, we collided.
    return [ ( col[0] << 16 ) + ( col[1] << 8 ) + col[0] - 1 for col in result ]

### quadtree ###


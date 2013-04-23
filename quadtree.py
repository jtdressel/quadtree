import numpy
import pygame

class QuadTree( object ):
    def __init__( self, id2rect, bounds = None, depth = None ):
        '''
        Given a dictionary 'id2rect' whose keys are unique integers and whose values are pygame.Rect objects,
        creates a quad tree where the .items field stores the unique integers within
        'bounds'
        and the .sub00, .sub01, .sub10, .sub11 fields store recursive QuadTree objects
        if they are not None.
        
        Also takes an optional 'bounds' parameter in the form of a pygame.Rect.
        
        Also takes an optional integer 'depth' parameter.  The depth parameter
        determines how many times to subdivide.  A value of 0 means that
        there are no children of the returned QuadTree, a value of 1 means
        that there is one level of children, and so on.  The default value is 8,
        so by default the quadtree will be divided 2^8 times in both x and y.
        So the bins will, in x, linspace( bounds[0][0], bounds[1][0], 2**8 + 1 )
        and, in y, linspace( bounds[0][1], bounds[1][1], 2**8 + 1 ).
        '''
        
        if depth is None:
            ## By default, divide in half in each dimension 8 times,
            ## so, 1/2^8 = 1/256.
            depth = 8
        assert depth >= 0
        self.depth = depth
        
        if bounds is None:
            bounds = id2rect.values()[0].unionall( id2rect.values() )
            ## Pad bounds by 1.
            bounds = bounds.inflate( 1, 1 )
        
        self.bounds = bounds.copy()
        
        ## These sub-quadrants are named by whether the origin or center coordinate
        ## is used for the x,y coordinates of the sub-QuadTree's origin.
        ## In other words, use the 0 and 1
        ## as the index W into ( origin[coord], center[coord] )[ W ]
        ## for each coordinate.
        ## +zero, +zero
        self.sub00 = None
        ## +zero, +one
        self.sub01 = None
        ## +one, +zero
        self.sub10 = None
        ## +one, +one
        self.sub11 = None
        
        self.items = [ id for id, rect in id2rect.iteritems() if self.bounds.colliderect( rect ) ]
        if len( self.items ) > 1 and depth > 0:
            
            origin, opposite = numpy.array( [ self.bounds.left, self.bounds.top ] ), numpy.array( [ self.bounds.right, self.bounds.bottom ] )
            center = .5 * ( origin + opposite )
            def bounds_for_subquadrant( S0, S1 ):
                sub_origin = ( ( origin[0], center[0] )[ S0 ], ( origin[1], center[1] )[ S1 ] )
                sub_opp = ( ( center[0], opposite[0] )[ S0 ], ( center[1], opposite[1] )[ S1 ] )
                return pygame.Rect( sub_origin[0], sub_origin[1], sub_opp[0]-sub_origin[0], sub_opp[1]-sub_origin[1] )
            
            subdict = dict([ ( id, id2rect[ id ] ) for id in self.items ])
            self.sub00 = QuadTree( subdict, bounds_for_subquadrant( 0,0 ), depth-1 )
            self.sub01 = QuadTree( subdict, bounds_for_subquadrant( 0,1 ), depth-1 )
            self.sub10 = QuadTree( subdict, bounds_for_subquadrant( 1,0 ), depth-1 )
            self.sub11 = QuadTree( subdict, bounds_for_subquadrant( 1,1 ), depth-1 )
            
            ## Cull empty children.
            if len( self.sub00.items ) == 0: self.sub00 = None
            if len( self.sub01.items ) == 0: self.sub01 = None
            if len( self.sub10.items ) == 0: self.sub10 = None
            if len( self.sub11.items ) == 0: self.sub11 = None
        
        self._update_convenience_aliases()
    
    def _update_convenience_aliases( self ):
        ## For convenience, set north-east, north-west, south-east, south-west and children:
        self.ne = self.sub11
        self.nw = self.sub01
        self.se = self.sub10
        self.sw = self.sub00
        self.children = [ self.sub00, self.sub01, self.sub10, self.sub11 ]
    
    def descendents( self, path ):
        '''
        Returns the sequence of QuadTrees named by the elements of 'path',
        a sequence of integers each in the range [0,3] and each representing
        a QuadTree child by converting the integer to a 2-digit
        binary number BB and using the child '.subBB'.
        
        The result will have length equal to the length of 'path'.
        If 'path' is 0-length, returns '[]'.
        If 'path' is deeper than the QuadTree, an exception will be raised.
        '''
        
        result = []
        
        q = self
        for p in path:
            if q is None:
                raise RuntimeError, 'QuadTree child does not exist!'
            
            if 0 == p:
                q = q.sub00
            elif 1 == p:
                q = q.sub01
            elif 2 == p:
                q = q.sub10
            elif 3 == p:
                q = q.sub11
            else:
                raise RuntimeError, 'QuadTree child must be named by an integer in [0,3]!'
            
            result.append( q )
        
        return result
    
    def possible_collisions( self, rect, few_enough_not_to_recurse = None ):
        '''
        Given a pygame.Rect 'rect' and
        an optional limiting parameter 'few_enough_not_to_recurse',
        returns a set() of id's that 'rect' may collide with.
        
        The optional parameter 'few_enough_not_to_recurse', if set, is an integer that
        specifies if the number of rects in a child node is less than or equal to
        'few_enough_not_to_recurse' then they should all be returned rather
        than recursing for a more fine-grained result.
        '''
        
        results = set()
        
        if few_enough_not_to_recurse is not None and len( self.items ) <= few_enough_not_to_recurse:
            return set( self.items )
        
        for child in self.children:
            if child.bounds.colliderect( rect ):
                results.update( child.possible_collisions( rect, few_enough_not_to_recurse )
        
        return results

def main():
    pass

if __name__ == '__main__': main()

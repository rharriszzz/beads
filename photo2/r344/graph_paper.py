"""General 6.5-beads/turn graph paper, with string-interval rather than strip cuts.

This module is presentation geometry only; it never infers pigment or identity.
"""
X0 = -1
X_SCALE, Y_SCALE = 24, 32
RX, RY = 18, 14


def representative(k, x0=X0):
    """Unique lattice site of integer k in a thirteen-unit horizontal strip."""
    x = x0 + (2*k-x0) % 13
    y = (2*k-x)//13
    return x, y


def boundary(k, x0=X0):
    """Cut just before k; all index<k centers are below this step profile."""
    x, y = representative(k, x0)
    first = x0 + (y-x0) % 2
    left, right = x0-1, x0+13
    if x == first:
        return [[left,y-.5],[right,y-.5]]
    return [[left,y+.5],[x-1,y+.5],[x-1,y-.5],[right,y-.5]]


def strip_sides(lower, upper, x0=X0):
    """Lines halfway between each row's basic beads and its side copies."""
    sides={'left':[], 'right':[]}
    for y in range(lower,upper+1):
        xs=list(range(x0+(y-x0)%2,x0+13,2))
        for name,x in [('left',xs[0]-1),('right',xs[-1]+1)]:
            sides[name].extend([[x,y-.5],[x,y+.5]])
    return sides


def layout(length, start=0, x0=X0, extension_rows=8, minimum_rows=40, side_beads=7):
    if length <= 0 or int(length) != length:
        raise ValueError('A repeat must contain a positive integer number of positions')
    lower = representative(start,x0)[1]-extension_rows
    upper = representative(start+length-1,x0)[1]+extension_rows
    shortage=max(0,minimum_rows-(upper-lower+1))
    lower-=shortage//2;upper+=shortage-shortage//2
    points=[]
    for y in range(lower,upper+1):
        basic_x=list(range(x0+(y-x0)%2,x0+13,2))
        n=len(basic_x)
        for slot in range(-side_beads,n+side_beads):
            # Actual horizontal steps: x changes by2 and k changes by1.
            # Do not approximate seven beads by one whole duplicate strip.
            x=basic_x[0]+2*slot;k=(x+13*y)//2
            cx,cy=representative(k,x0);seam=(x-cx)//13
            side='left' if slot<0 else 'right' if slot>=n else 'basic'
            points.append(dict(x=x,y=y,a=(x+y)//2,b=(y-x)//2,k=k,
                               position=(k-start)%length,repeat_copy=(k-start)//length,
                               row_slot=slot,basic_row_count=n,side=side,
                               lateral_copy=seam,canonical_xy=[cx,cy],
                               in_chosen_interval=side=='basic' and start<=k<start+length))
    return dict(length=length,start=start,x0=x0,strip=[x0,x0+13],rows=[lower,upper],
                start_boundary=boundary(start,x0),end_boundary=boundary(start+length,x0),
                side_boundaries=strip_sides(lower,upper,x0),
                side_beads=side_beads,points=points,display_units=dict(x_scale=X_SCALE,y_scale=Y_SCALE,ellipse_rx=RX,ellipse_ry=RY),
                membership='Exactly one canonical representative per k in [start,start+length). Lateral copies are never additional members or observations.',
                axes='Physical display y increases upward; screen ordinate is inverted at rendering.')


def pattern_layout(strict_colors, provisional_colors=None, **geometry):
    """Make this presentation from color sequences without photographic inputs.

    Accept a string of R/Y/B/? codes or a list of full color names. The two
    interpretations must have the same length. Colors never depend on placement.
    """
    codes={'R':'red','Y':'yellow','B':'black','?':'?'}
    def normalize(colors):
        values=[c for c in colors if not c.isspace()] if isinstance(colors,str) else list(colors)
        result=[codes.get(c,c) for c in values]
        if not result or any(c not in ['red','yellow','black','?'] for c in result):
            raise ValueError('Use R/Y/B/? or lists of red/yellow/black/? colors')
        return result
    strict=normalize(strict_colors)
    provisional=normalize(provisional_colors) if provisional_colors is not None else strict
    if len(strict)!=len(provisional):raise ValueError('Color sequences must have equal lengths')
    paper=layout(len(strict),**geometry)
    for point in paper['points']:
        i=point['position'];point.update(strict_color=strict[i],provisional_color=provisional[i],tentative=strict[i]=='?' and provisional[i]!='?')
    return paper


def main():
    from common import OUT, ROOT, read, save
    if OUT != ROOT/'photo2/r344':
        save(OUT/'presentation-input-seal.json',read(ROOT/'photo2/r344/presentation-input-seal.json'))
    p=read(OUT/'pattern208.json');paper=pattern_layout(p['strict_sequence'],p['provisional_sequence'])
    save(OUT/'graph-paper-layout.json',paper)
    print('GRAPH PAPER',len(paper['points']),'display symbols,',paper['side_beads'],'per side per row;',sum(r['in_chosen_interval'] for r in paper['points']),'in block;',paper['rows'])


if __name__=='__main__':
    main()

"""General 6.5-beads/turn graph paper, with string-interval rather than strip cuts.

This module is presentation geometry only; it never infers pigment or identity.
"""
from common import *

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


def layout(length, start=0, x0=X0, extension_rows=8, minimum_rows=40, lateral_copies=1):
    if length <= 0 or int(length) != length:
        raise ValueError('A repeat must contain a positive integer number of positions')
    lower = representative(start,x0)[1]-extension_rows
    upper = representative(start+length-1,x0)[1]+extension_rows
    shortage=max(0,minimum_rows-(upper-lower+1))
    lower-=shortage//2;upper+=shortage-shortage//2
    points=[]
    for copy_index in range(-lateral_copies,lateral_copies+1):
        # K=(13,-1) moves one duplicate strip without changing k.
        for source_y in range(lower-1,upper+2):
            for source_x in range(x0,x0+13):
                if (source_x+source_y)%2:
                    continue
                x,y=source_x+13*copy_index,source_y-copy_index
                if not lower <= y <= upper:
                    continue
                k=(source_x+13*source_y)//2
                points.append(dict(x=x,y=y,a=(x+y)//2,b=(y-x)//2,k=k,
                                   position=(k-start)%length,repeat_copy=(k-start)//length,
                                   lateral_copy=copy_index,canonical_xy=[source_x,source_y],
                                   in_chosen_interval=copy_index==0 and start<=k<start+length))
    return dict(length=length,start=start,x0=x0,strip=[x0,x0+13],rows=[lower,upper],
                start_boundary=boundary(start,x0),end_boundary=boundary(start+length,x0),
                points=points,display_units=dict(x_scale=X_SCALE,y_scale=Y_SCALE,ellipse_rx=RX,ellipse_ry=RY),
                membership='Exactly one canonical representative per k in [start,start+length). Lateral copies are never additional members or observations.',
                axes='Physical display y increases upward; screen ordinate is inverted at rendering.')


def main():
    if OUT != ROOT/'photo2/r344':
        save(OUT/'presentation-input-seal.json',read(ROOT/'photo2/r344/presentation-input-seal.json'))
    p=read(OUT/'pattern208.json');paper=layout(p['length'])
    for point in paper['points']:
        e=p['entries'][point['position']]
        point.update(strict_color=e['strict_color'],provisional_color=e['provisional_color'],tentative=e['tentative'])
    save(OUT/'graph-paper-layout.json',paper)
    print('GRAPH PAPER',len([r for r in paper['points'] if r['lateral_copy']==0]),'canonical display beads;',sum(r['in_chosen_interval'] for r in paper['points']),'in block;',paper['rows'])


if __name__=='__main__':
    main()

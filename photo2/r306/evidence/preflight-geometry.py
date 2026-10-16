"""Periodic planar geometry with numerical true-arclength inversion.

The immutable photographic reference supplies a spatial prior, not body centers.
Radius fixes the world-unit gauge. No local circle, splice, or registration reset.
All N bodies participate in every visibility/contact query, including across cuts.
"""
from functools import lru_cache
from copy import deepcopy
import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.integrate import cumulative_simpson
from scipy.spatial import cKDTree
from photo2.r299.forward import Surface
from photo2.r297.geometry import reference, periodic_field, R, PITCH, unit, contact
from photo2.r295.geometry import AXES

FIELD = 32

@lru_cache(maxsize=24)
def axis(elevation, roll, perspective, scale, nodes, anchor, arc0, resolution=16385):
    ref = reference()
    e, r = np.radians([elevation, roll])
    right = np.array([1., 0., 0.])
    down = np.array([0., np.sin(e), -np.cos(e)])
    right, down = np.cos(r)*right+np.sin(r)*down, -np.sin(r)*right+np.cos(r)*down
    eye = np.cross(right, down)
    # Displacements use the original photographic normal, without mutating it.
    original = CubicSpline(ref.arc, np.vstack([ref.points[:-1], ref.points[0]]), bc_type='periodic')
    u = np.linspace(0, ref.length, 1025)
    t = unit(original(u, 1)); normal = np.c_[-t[:, 1], t[:, 0]]
    correction = CubicSpline(np.linspace(0, ref.length, len(nodes)+1), np.r_[nodes, nodes[0]], bc_type='periodic')(u)
    image = (original(u)+normal*correction[:, None]-anchor)/scale
    base = image @ np.array([right, down])
    if perspective:
        d = 1/perspective; denominator = d*eye[2]-base[:, 2]
        if np.min(abs(denominator)) < .1*d*abs(eye[2]):
            raise ValueError('Camera-plane singularity')
        f = d*eye[2]/denominator
        plane = (f[:, None]*base+(1-f[:, None])*d*eye)[:, :2]
    else:
        plane = (base-base[:, 2, None]/eye[2]*eye)[:, :2]
    plane[-1] = plane[0]
    spline = CubicSpline(u, plane, bc_type='periodic')
    dense = np.linspace(0, ref.length, resolution)
    length = cumulative_simpson(np.linalg.norm(spline(dense, 1), axis=1), x=dense, initial=0)
    inverse = PchipInterpolator(length, dense)
    origin = float(np.interp(arc0, dense, length))
    return right, down, eye, spline, inverse, origin, float(length[-1])

class Chain(Surface):
    def __init__(self, p, data, resolution=16385):
        self.p = p; self.n = int(p['count']); self.radius = p['radius']; self.axial = p['axial']; self.scale = p['scale']
        self.start = int(np.ceil(self.n*p.get('seam_fraction', -.5)))
        self.indices = np.arange(self.start, self.start+self.n)
        self.closed = p['topology'] == 'closed'; self.direction = data['direction']
        self.dims = np.array([self.axial, 1., 1.])*self.radius/R
        self.bound = self.radius*np.sqrt(1+(.7*self.axial)**2)
        self.distance = 1/p['perspective'] if p['perspective'] else np.inf
        self.offset = np.asarray(data['anchor']['measured_photo_location'])
        self.right, self.down, self.eye, self.spline, self.inverse, self.a0, self.length = axis(
            p['elevation'], p['roll'], p['perspective'], p['scale'], tuple(p['axis_nodes']), tuple(self.offset), data['arc0'], resolution)
        fine = np.linspace(self.start, self.start+self.n, 4*self.n+1)
        rate = 1+periodic_field(p['local_spacing'], fine/self.n)
        if np.max(abs(rate-1)) > .020001:
            raise ValueError('Interpolated stitch correction exceeds 2 percent')
        phase_derivative = periodic_field(p['local_phase'], fine/self.n, 1)/self.n
        if np.max(abs(phase_derivative)) > .02*2*np.pi/6.5:
            raise ValueError('Distributed phase-rate correction exceeds 2 percent')
        self.extent = self.length if self.closed else self.length*(1-p['gap_steps']/self.n)
        integral = cumulative_simpson(rate, x=fine, initial=0)
        integral -= np.interp(0., fine, integral)
        self.integral_grid = fine; self.integral = integral*self.extent/(integral[-1]-integral[0])
        self.effective_pitch = self.extent/self.n/PITCH
        self.line, self.g, self.phase = self.placement(self.indices)
        self.centers = self.line+p['minor']*self.g['radial']
        self.pc = self.project(self.centers); self.tree = cKDTree(self.pc)
        self.axis_xy = self.project(self.line)
        self.query_radius = self.bound*self.scale
        if np.isfinite(self.distance):
            depth = self.centers@self.eye
            if np.max(depth+self.bound) > .85*self.distance:
                raise ValueError('Camera bound')
            self.query_radius *= np.max((1+np.linalg.norm(self.centers, axis=1)/self.distance)/(1-(depth+self.bound)/self.distance)**2)
        self.station_px = self.station(self.indices)*self.scale

    def station(self, k):
        k = np.asarray(k, float); cycles = np.floor((k-self.start)/self.n); wrapped = k-cycles*self.n
        return self.p['s0']/self.scale+np.interp(wrapped, self.integral_grid, self.integral)+cycles*self.extent

    def placement(self, k):
        k = np.atleast_1d(k).astype(float); p = self.p
        a = (self.a0+self.direction*self.station(k)) % self.length
        u = self.inverse(a); xy = self.spline(u)
        t = unit(self.spline(u, 1))*self.direction
        tangent = np.c_[t, np.zeros(len(k))]
        normal = np.c_[-t[:, 1], t[:, 0], np.zeros(len(k))]; z = np.tile([0., 0., 1.], (len(k), 1))
        turns = p['winding']/self.n if self.closed else 1/p['turn']
        phase = p['phase']+p['hand']*2*np.pi*k*turns+periodic_field(p['local_phase'], k/self.n)
        radial = np.sin(phase)[:, None]*normal+np.cos(phase)[:, None]*z
        circum = np.cos(phase)[:, None]*normal-np.sin(phase)[:, None]*z
        tilt = np.radians(p.get('tilt', 0.))
        body_axis = np.cos(tilt)*tangent+np.sin(tilt)*circum
        other = unit(np.cross(radial, body_axis)); third = np.cross(body_axis, other)
        return np.c_[xy, np.zeros(len(k))], dict(zip(AXES, (body_axis, other, third)), radial=radial, axis_tangent=tangent), phase

    def closure(self):
        line, g, phase = self.placement([self.start, self.start+self.n])
        u = np.array([0., reference().length])
        return dict(topology=self.p['topology'], count=self.n, hand=self.p['hand'],
            geometric_axis_closed=True, axis_storage_position_gap=float(np.linalg.norm(self.spline(u)[1]-self.spline(u)[0])),
            axis_storage_tangent_gap=float(np.linalg.norm(self.spline(u, 1)[1]-self.spline(u, 1)[0])),
            string_axis_endpoint_gap=float(np.linalg.norm(line[1]-line[0])),
            radial_endpoint_gap=float(np.linalg.norm(g['radial'][1]-g['radial'][0])),
            tangent_endpoint_gap=float(np.linalg.norm(g['axis_tangent'][1]-g['axis_tangent'][0])),
            phase_turns=float((phase[1]-phase[0])/(2*np.pi)),
            total_twist_turns=float(self.n*(1/(self.n/self.p['winding'] if self.closed else self.p['turn'])-1/6.5)),
            geometric_length_units=self.length, mean_advance_units=self.extent/self.n,
            effective_pitch=self.effective_pitch, seam_indices=[int(self.indices[-1]), int(self.indices[0])],
            interpretation='Axis closure is imposed. Physical joining and identities remain conditional; open ends are not duplicated as guards.')

def canonical(p):
    q = deepcopy(p)
    q.update(radius=R, yaw=0., local_metric=0., local_turn=0., phase_transport=0., local_phase_bias=0.,
             bend=[0.]*5, strain=[0.]*5, phase_knots=[0.]*5, local_bend=[0.]*FIELD)
    q.setdefault('axis_nodes', [0.]*FIELD)
    if len(q['axis_nodes']) != FIELD:
        q['axis_nodes'] = CubicSpline(np.linspace(0, 1, len(q['axis_nodes'])+1), np.r_[q['axis_nodes'], q['axis_nodes'][0]], bc_type='periodic')(np.arange(FIELD)/FIELD).tolist()
    for key, limit in [('local_spacing', .015), ('local_phase', .30)]:
        values = np.asarray(q.get(key, [0.]*FIELD)); values -= values.mean()
        q[key] = (values*min(1., limit/max(1e-12, abs(values).max()))).tolist()
    q.setdefault('roll', 0.); q.setdefault('tilt', 0.); q.setdefault('gap_steps', 1.)
    q.setdefault('seam_fraction', -.5); q.setdefault('light_az', 130.); q.setdefault('light_el', 65.); q.setdefault('roughness', 10.)
    q['winding'] = round(q['count']/6.5)
    q['turn'] = float(np.clip(q.get('turn', 6.5), 6.5*q['count']/(q['count']+6.5), 6.5*q['count']/(q['count']-6.5)))
    q['phase'] = float((q['phase']+np.pi)%(2*np.pi)-np.pi)
    return q

def valid(p, count_range=(1800, 3200)):
    bounds = dict(scale=(7., 10.5), axial=(.45, 1.12), minor=(3.5, 5.4), elevation=(40., 88.),
                  roll=(-70., 70.), perspective=(0., .001), s0=(-40., 40.), tilt=(-12., 12.),
                  gap_steps=(.5, 8.), seam_fraction=(-.85, -.15), light_az=(-180., 180.), light_el=(25., 88.), roughness=(7., 18.))
    if not all(np.isfinite(p[k]) and lo <= p[k] <= hi for k, (lo, hi) in bounds.items()): return False
    if not count_range[0] <= p['count'] <= count_range[1]: return False
    turn = p['count']/p['winding'] if p['topology']=='closed' else p['turn']
    if abs(p['count']*(1/turn-1/6.5)) > 1.000001: return False
    for key, limit in [('axis_nodes', 30.), ('local_spacing', .02), ('local_phase', .45)]:
        if len(p[key]) != FIELD or not np.isfinite(p[key]).all() or max(abs(np.asarray(p[key]))) > limit: return False
    return p['hand'] in (-1, 1) and p['topology'] in ('open', 'closed')

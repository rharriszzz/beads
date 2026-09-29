"""Python placement/projection primitives for the beads.pov model.

Forward geometry, not an image detector. Indices are full-string model indices.
No photo palette, location, masks, or inferred correspondence enters this module.
"""
from dataclasses import dataclass
import numpy as np


def place_tube_coordinates(major_angle_deg, minor_angle_deg, chain_major,
                           chain_minor, bead_radius):
    """Place by two geometric angles, without bead_index or total bead count.

    Circular prototype: major angle is position along the planar centerline;
    minor angle is position around the tube. Angles follow the legacy loop's
    sign/zero conventions. A noncircular necklace will use centerline arc length
    and its local planar frame instead of a constant major radius.
    """
    theta,phi=np.broadcast_arrays(np.radians(major_angle_deg),np.radians(minor_angle_deg))
    radial=chain_major-chain_minor*np.sin(phi)
    xyz=np.stack((radial*np.cos(theta),radial*np.sin(theta),
                  chain_minor*np.cos(phi)+chain_minor+2*bead_radius),axis=-1)
    return xyz,np.degrees(theta)


@dataclass(frozen=True)
class Rope:
    nbeads: int
    beads_per_row: float = 6.5
    chain_minor: float = 4.0
    rclock: float = 0.0
    helicity: int = 1

    def __post_init__(self):
        if self.nbeads < 1 or self.beads_per_row <= 0 or self.chain_minor <= 0:
            raise ValueError('Positive bead count, row size and minor radius required')
        if self.helicity not in (-1, 1) or self.nrows < 1:
            raise ValueError('Helicity must be +/-1 and at least one row is required')

    @property
    def nrows(self):
        return int(np.floor(.5 + self.nbeads/self.beads_per_row))

    @property
    def exact_beads_per_row(self):
        return self.nbeads/self.nrows

    @property
    def bead_radius(self):
        # Literal legacy expression: POV-Ray sin() takes radians. Do not quietly
        # replace 180 with pi while calling this an exact port of beads.pov.
        return self.chain_minor*.96*np.sin(180/self.beads_per_row)

    @property
    def chain_major(self):
        return .65*(2*self.bead_radius)*1.05*self.nrows/(2*np.pi)

    def coordinates(self, indices):
        """Legacy generator's index-to-angle mapping; not needed by the direct API."""
        i = np.asarray(indices, dtype=float)
        return (360*(i/self.nbeads + self.rclock*.1666),
                self.helicity*360*(i/self.exact_beads_per_row + self.rclock))

    def place(self, indices):
        return place_tube_coordinates(*self.coordinates(indices),self.chain_major,
                                      self.chain_minor,self.bead_radius)


def unit(vector):
    vector = np.asarray(vector, dtype=float)
    norm = np.linalg.norm(vector)
    if norm < 1e-12:
        raise ValueError('Degenerate camera basis')
    return vector/norm


@dataclass(frozen=True)
class Camera:
    location: tuple
    look_at: tuple
    width: int
    height: int
    angle: float = 10.0
    sky: tuple = (0., 1., 0.)

    def basis(self):
        forward = unit(np.asarray(self.look_at)-self.location)
        # POV's default camera frame is left-handed: right x, up y, forward z.
        right = unit(np.cross(self.sky, forward))
        up = unit(np.cross(forward, right))
        return right, up, forward

    def project(self, xyz):
        """Square pixels, horizontal FOV, POV right=x*(width/height), y down.

        Pixel centers have coordinates 0..width-1, 0..height-1. A coordinate may
        be outside the image or on an occluded bead; projection is not visibility.
        """
        if self.width < 1 or self.height < 1 or not 0 < self.angle < 180:
            raise ValueError('Invalid camera dimensions/FOV')
        right, up, forward = self.basis()
        delta = np.asarray(xyz)-self.location
        depth = delta @ forward
        if np.any(depth <= 0):
            raise ValueError('Point at or behind camera')
        focal = self.width/(2*np.tan(np.radians(self.angle)/2))
        xy = np.stack(((self.width-1)/2+focal*(delta@right)/depth,
                       (self.height-1)/2-focal*(delta@up)/depth), axis=-1)
        return xy, depth


def fit_similarity(source_xy, target_xy):
    """Fit a proper 2-D rotation, uniform scale and translation to supplied pairs.

    Does NOT discover pairs or fit unknown 3-D geometry. Callers must preserve
    association uncertainty and test held-out observations.
    """
    source = np.asarray(source_xy, float); target = np.asarray(target_xy, float)
    if source.shape != target.shape or source.ndim != 2 or source.shape[1] != 2 or len(source) < 2:
        raise ValueError('At least two paired 2-D coordinates required')
    a, b = source-source.mean(0), target-target.mean(0)
    denom = np.sum(a*a)
    if denom < 1e-12:
        raise ValueError('Coincident source coordinates')
    u, s, vt = np.linalg.svd(a.T@b)
    correction = np.diag([1., np.linalg.det(u@vt)])
    rotation = u@correction@vt
    scale = np.sum(s*np.diag(correction))/denom
    translation = target.mean(0)-scale*source.mean(0)@rotation
    return dict(scale=float(scale), rotation=rotation.tolist(), translation=translation.tolist())


def apply_similarity(xy, fit):
    return fit['scale']*np.asarray(xy)@np.asarray(fit['rotation'])+fit['translation']


def bead_surface_samples(rope, index, profile_steps=32, angular_steps=256,
                         roundedness=.8, height_ratio=.7):
    """Sample the exposed boundary of the legacy rounded annular bead macro.

    This returns the individual bead's surface before neighbor occlusion. Each
    sample is on an analytic wall, flat annular end, or elliptical fillet.
    It does not approximate the bead as a sphere or fill its hole. Accuracy of
    an extremum selected from these samples must be checked with denser sampling.
    """
    if not 0 < roundedness < 1 or height_ratio <= 0 or min(profile_steps,angular_steps)<4:
        raise ValueError('Invalid surface sampling parameters')
    radius=rope.bead_radius
    if radius<=0:
        raise ValueError('Legacy radius expression is nonpositive for this row size')
    major=radius*.57; minor=radius-major; hole=major-minor
    rounding=roundedness*minor; extra=minor-rounding
    stretch=height_ratio*radius/minor
    cy=stretch*extra; top=height_ratio*radius
    outside=major+extra; inside=major-extra
    q=np.linspace(0,np.pi/2,profile_steps)
    profiles=[np.column_stack((np.full(profile_steps,radius),np.linspace(-cy,cy,profile_steps))),
              np.column_stack((np.full(profile_steps,hole),np.linspace(-cy,cy,profile_steps)))]
    for sign in [-1,1]:
        profiles.append(np.column_stack((np.linspace(inside,outside,profile_steps),np.full(profile_steps,sign*top))))
        for radial_sign in [-1,1]:
            center=outside if radial_sign==1 else inside
            profiles.append(np.column_stack((center+radial_sign*rounding*np.cos(q),
                                             sign*(cy+stretch*rounding*np.sin(q)))))
    profile=np.concatenate(profiles)
    az=np.linspace(0,2*np.pi,angular_steps,endpoint=False)
    local=np.stack((profile[:,0,None]*np.cos(az),
                    np.broadcast_to(profile[:,1,None],(len(profile),len(az))),
                    profile[:,0,None]*np.sin(az)),axis=-1).reshape(-1,3)
    center,angle=rope.place(index);theta=np.radians(angle)
    rotation=np.array([[np.cos(theta),-np.sin(theta),0],
                       [np.sin(theta),np.cos(theta),0],[0,0,1]])
    return local@rotation.T+center


def closest_camera_sample(surface, camera):
    """Finite-distance nearest sampled surface point, before neighbor occlusion."""
    d=np.asarray(surface)-camera.location
    return np.asarray(surface)[np.argmin(np.sum(d*d,axis=1))]


def minor_outward_point(rope, index):
    """Outer-wall midpoint in the minor-circle radial direction (R119).

    On the reference torus of minor radius chain_minor + bead_radius. The
    original bead has a straight outer-wall band parallel to its hole axis;
    choose its midpoint, not an arbitrary endpoint of the equal-support band.
    """
    center, angle = rope.place(index)
    theta=np.radians(angle)
    axis=np.array([rope.chain_major*np.cos(theta),rope.chain_major*np.sin(theta),
                   rope.chain_minor+2*rope.bead_radius])
    return center+rope.bead_radius*unit(center-axis)

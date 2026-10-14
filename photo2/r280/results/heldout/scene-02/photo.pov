#version 3.7;
global_settings {assumed_gamma 1.0}
#declare bead_radius=1.784536980648071;
#declare hole_size_per_bead_size=.14;
#macro bead(bead_material, roundedness, height_per_bead_size, bead_relative_size)
#local bead_actual_radius = bead_radius * bead_relative_size;
#local bead_major = bead_actual_radius * 0.5 * ( 1 + hole_size_per_bead_size );
#local bead_minor = bead_actual_radius - bead_major;
#local hole_radius = bead_major - bead_minor;

#local bead_round = roundedness * bead_minor;
#local bead_extra_half_width  = bead_minor - bead_round;
#local bead_total_half_width  = bead_minor;

#local bead_desired_half_height = height_per_bead_size * bead_actual_radius;
#local bead_height_scaling = bead_desired_half_height / bead_minor;
#local bead_extra_half_height = bead_height_scaling * bead_extra_half_width;
#local bead_total_half_height = bead_desired_half_height;

merge {
  // short wide
  difference { cylinder { <0, -bead_extra_half_height, 0>, <0, bead_extra_half_height, 0>, 
                          bead_major+bead_total_half_width }
               cylinder { <0, -bead_extra_half_height * 1.0001, 0>, <0, bead_extra_half_height * 1.0001, 0>, 
                          bead_major-bead_total_half_width } }
  // tall narrow
  difference { cylinder { <0, -bead_total_half_height, 0>, <0, bead_total_half_height, 0>, 
                          bead_major+bead_extra_half_width }
               cylinder { <0, -bead_total_half_height * 1.0001, 0>, <0, bead_total_half_height * 1.0001, 0>, 
                          bead_major-bead_extra_half_width } }
  // outer
  torus {bead_major+bead_extra_half_width bead_round 
         scale <1.0, bead_height_scaling, 1.0> translate <0, bead_extra_half_height, 0>}
  torus {bead_major+bead_extra_half_width bead_round 
         scale <1.0, bead_height_scaling, 1.0> translate <0, -bead_extra_half_height, 0>}
  // inner
  torus {bead_major-bead_extra_half_width bead_round 
         scale <1.0, bead_height_scaling, 1.0> translate <0, bead_extra_half_height, 0>}
  torus {bead_major-bead_extra_half_width bead_round 
         scale <1.0, bead_height_scaling, 1.0> translate <0, -bead_extra_half_height, 0>}
  material { bead_material } }
#end


camera {orthographic location <-13.8918542134,0,78.784620241> direction <0.173648177667,-0,-0.984807753012> right <37.727639702,-11.5052495035,6.65240079792> up <-7.93132123794,-26.81675455,-1.39850592692> }
background {color rgb <0.65,0.63,0.52>}
light_source {<64,8,56> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.09563437808,2.53318925413>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-0.326253126446,3.98667265994>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-3.46630017737,1.9961871356>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-3.61191273826,-1.71874558071>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-0.637300412377,-3.9489046816>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,2.88785694356,-2.76772149493>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,3.91827985886,0.804414661519>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,1.56381636773,3.68164071686>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-2.14158196113,3.37840594124>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-3.99693079643,0.156665913868>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-2.39944900002,-3.20041317587>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,1.27084601944,-3.79274971424>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,3.84329464436,-1.1086416358>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.09563437808,2.53318925413>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <0,-0.326253126446,3.98667265994>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-3.46630017737,1.9961871356>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-3.61191273826,-1.71874558071>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-0.637300412377,-3.9489046816>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,2.88785694356,-2.76772149493>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,3.91827985886,0.804414661519>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,1.56381636773,3.68164071686>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-2.14158196113,3.37840594124>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-3.99693079643,0.156665913868>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-2.39944900002,-3.20041317587>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,1.27084601944,-3.79274971424>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,3.84329464436,-1.1086416358>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.09563437808,2.53318925413>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-0.326253126446,3.98667265994>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.15 roughness 0.08}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-3.46630017737,1.9961871356>}
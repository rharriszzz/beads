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


camera {orthographic location <33.8094609393,-0,72.5046229629> direction <-0.422618261741,0,-0.906307787037> right <28.6266338862,-16.3255139267,-13.3488186083> up <-10.3571582794,-22.110197007,4.82962222242> }
background {color rgb <0.47,0.31,0.43>}
light_source {<24,-72,44> color rgb 0.55 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.99366514319,0.225030495881>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,2.45385684554,-3.15889008698>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-1.20576600824,-3.8139386903>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-3.82376316971,-1.17423814533>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.13852410489,2.47985210104>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,0.257993368208,3.99167125675>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,3.43163797963,2.05520334196>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.64079175133,-1.65669412489>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,0.704772908615,-3.93742239889>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-2.84007846366,-2.81672759071>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.93146981493,0.737255108038>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-1.62658034573,3.65434486316>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,2.08346391065,3.41455387028>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.99366514319,0.225030495881>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,2.45385684554,-3.15889008698>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-1.20576600824,-3.8139386903>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-3.82376316971,-1.17423814533>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.13852410489,2.47985210104>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,0.257993368208,3.99167125675>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,3.43163797963,2.05520334196>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.64079175133,-1.65669412489>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,0.704772908615,-3.93742239889>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-2.84007846366,-2.81672759071>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.93146981493,0.737255108038>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-1.62658034573,3.65434486316>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,2.08346391065,3.41455387028>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.99366514319,0.225030495881>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,2.45385684554,-3.15889008698>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-1.20576600824,-3.8139386903>}

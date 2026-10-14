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


camera {orthographic location <-34.8173072993,0,72.026072449> direction <0.435216341242,-0,-0.900325905612> right <21.4935207334,32.0948240236,10.3899392383> up <20.2270610532,-16.7111314021,9.77773431904> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-39.7173624315,37.2254482705,80> color rgb 0.9671233509297689 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-2.71680653866,2.93580691318>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-3.95944374123,-0.568159537482>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-1.78163427346,-3.58130972071>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,1.93527649659,-3.50067206144>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.98035897924,-0.395907055231>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,2.58692673429,3.05087037932>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-1.04127521899,3.86209087391>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-3.76995022139,1.33696496896>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-3.24187641642,-2.34312554095>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,0.0867588105362,-3.99905900291>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.34044565989,-2.20032333836>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,3.70842002497,1.49920676305>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,0.872799704628,3.90361635866>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-2.71680653866,2.93580691318>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.95944374123,-0.568159537482>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-1.78163427346,-3.58130972071>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,1.93527649659,-3.50067206144>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.98035897924,-0.395907055231>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,2.58692673429,3.05087037932>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-1.04127521899,3.86209087391>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-3.76995022139,1.33696496896>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-3.24187641642,-2.34312554095>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,0.0867588105362,-3.99905900291>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.34044565989,-2.20032333836>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,3.70842002497,1.49920676305>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,0.872799704628,3.90361635866>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-2.71680653866,2.93580691318>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-3.95944374123,-0.568159537482>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-1.78163427346,-3.58130972071>}
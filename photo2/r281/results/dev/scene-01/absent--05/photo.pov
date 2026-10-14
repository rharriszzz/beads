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


camera {orthographic location <35.05455589,-0,71.9109039809> direction <-0.438181948626,0,-0.898886299761> right <26.9595459738,-11.156614852,-13.1420251838> up <-7.01996976952,-20.9945153093,3.42203906514> }
background {color rgb <0.65,0.63,0.52>}
light_source {<43.1396465779,15.0984114296,80> color rgb 1.219308503548557 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.73952810564,-1.41983433791>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-3.29279483856,2.27101346344>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-0.00151322636925,3.99999971377>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,3.29107561746,2.27350418521>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.74060130058,-1.41700455544>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,0.958731843412,-3.88340485302>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-2.65135777695,-2.99504623313>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-3.97101761153,0.480644493275>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-1.86023245056,3.54112061781>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.97065281296,0.483648879765>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,2.65362310936,-2.99303932374>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-0.955793333889,-3.88412913056>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.73952810564,-1.41983433791>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.29279483856,2.27101346344>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-0.00151322636925,3.99999971377>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,3.29107561746,2.27350418521>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.74060130058,-1.41700455544>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,0.958731843412,-3.88340485302>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-2.65135777695,-2.99504623313>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-3.97101761153,0.480644493275>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-1.86023245056,3.54112061781>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,1.85755265975,3.54252708053>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.97065281296,0.483648879765>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,2.65362310936,-2.99303932374>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-0.955793333889,-3.88412913056>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.73952810564,-1.41983433791>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-3.29279483856,2.27101346344>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-0.00151322636926,3.99999971377>}
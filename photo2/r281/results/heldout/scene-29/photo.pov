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


camera {orthographic location <9.65640806328,-0,79.4150727716> direction <-0.120705100791,0,-0.992688409645> right <30.786771213,-7.88422424451,-3.74349119643> up <-5.47860461859,-21.709470605,0.666166257464> }
background {color rgb <0.65,0.63,0.52>}
light_source {<-36.1846676606,51.3149886397,80> color rgb 1.1901465748494093 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.96215175389,0.548956718825>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-1.79897620992,3.57262992712>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,1.91828182377,3.5100135106>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,3.97839276667,0.415199944726>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,2.60168753503,-3.03829260771>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-1.02253882536,-3.86709378612>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-3.76342405272,-1.35522669668>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-3.25319823735,2.32738076569>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,0.0673695871918,3.9994326271>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,3.32973881232,2.21649259907>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.71564488301,-1.48121001325>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,0.891714926501,-3.89933898114>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-2.70254125525,-2.94894400823>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.96215175389,0.548956718825>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-1.79897620992,3.57262992712>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,1.91828182377,3.5100135106>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,3.97839276667,0.415199944726>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,2.60168753503,-3.03829260771>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-1.02253882536,-3.86709378612>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-3.76342405272,-1.35522669668>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-3.25319823735,2.32738076569>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,0.0673695871918,3.9994326271>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,3.32973881232,2.21649259907>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.71564488301,-1.48121001325>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,0.891714926501,-3.89933898114>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-2.70254125525,-2.94894400823>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.96215175389,0.548956718825>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-1.79897620992,3.57262992712>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,1.91828182377,3.5100135106>}
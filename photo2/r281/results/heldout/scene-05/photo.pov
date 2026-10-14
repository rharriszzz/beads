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


camera {orthographic location <1.72284631907,-0,79.9814466021> direction <-0.0215355789884,0,-0.999768082526> right <26.251714968,18.2900983314,-0.565477025278> up <12.8000995766,-18.3804632282,-0.275721500125> }
background {color rgb <0.65,0.63,0.52>}
light_source {<-57.9619335026,18.5859419874,80> color rgb 1.2810368046352045 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.82686714979,1.16408239309>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-1.21588729014,3.81072409099>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,2.44546173874,3.16539363814>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,3.99424849665,-0.214427020286>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,2.09252178252,-3.40901050008>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-1.61687278381,-3.65865035238>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-3.92949863939,-0.747690071523>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-2.84754651492,2.80917761015>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,0.694317059785,3.93927960679>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,3.63638060435,1.66635413412>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.43708219427,-2.04608552847>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,0.268589848017,-3.99097224916>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-3.1319293463,-2.48817575139>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.82686714979,1.16408239309>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-1.21588729014,3.81072409099>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,2.44546173874,3.16539363814>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,3.99424849665,-0.214427020286>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,2.09252178252,-3.40901050008>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-1.61687278381,-3.65865035238>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-3.92949863939,-0.747690071523>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-2.84754651492,2.80917761015>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,0.694317059785,3.93927960679>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,3.63638060435,1.66635413412>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.43708219427,-2.04608552847>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,0.268589848017,-3.99097224916>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-3.1319293463,-2.48817575139>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.82686714979,1.16408239309>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-1.21588729014,3.81072409099>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,2.44546173874,3.16539363814>}
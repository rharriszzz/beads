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


camera {orthographic location <-14.3094620039,0,78.7098424415> direction <0.178868275049,-0,-0.983873030518> right <37.522595757,12.0631832837,6.82161393822> up <8.30804848649,-26.696348223,1.51040454988> }
background {color rgb <0.47,0.31,0.43>}
light_source {<6.62697167557,34.0638254613,80> color rgb 1.1618695025425767 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,1.98570354054,3.4723164385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-1.72965222732,3.60670253452>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-3.95081244943,0.625364685116>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-2.75898231962,-2.89620727159>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,0.816251264173,-3.91583118555>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,3.68634945492,-1.55268402973>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,3.37191907477,2.15178106534>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-3.20764922943,2.38976702232>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-3.78889214973,-1.28230116498>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-1.09702288943,-3.84662719536>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,2.54253209005,-3.08796544202>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,3.985668585,0.338298581891>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,1.98570354054,3.4723164385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,-1.72965222732,3.60670253452>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-3.95081244943,0.625364685116>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-2.75898231962,-2.89620727159>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,0.816251264173,-3.91583118555>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,3.68634945492,-1.55268402973>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,3.37191907477,2.15178106534>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,0.144587255496,3.99738596154>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-3.20764922943,2.38976702232>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-3.78889214973,-1.28230116498>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-1.09702288943,-3.84662719536>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,2.54253209005,-3.08796544202>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,3.985668585,0.338298581891>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,1.98570354054,3.4723164385>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-1.72965222732,3.60670253452>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-3.95081244943,0.625364685116>}
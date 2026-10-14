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


camera {orthographic location <33.9858426552,-0,72.4221133288> direction <-0.42482303319,0,-0.90527641661> right <34.4799643334,-12.2197138644,-16.1805640395> up <-7.74355314541,-26.6614423954,3.63385113601> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-18.2942087803,-48.6944260293,80> color rgb 1.0683194680811932 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,1.688265582,-3.62625968797>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,3.943397377,-0.670534955897>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,2.79194448245,2.86444514818>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-0.771386906382,3.92491557115>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-3.66833989766,1.59476719155>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-3.39632224339,-2.11305352962>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-0.190321972361,-3.99546962782>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,3.18009183734,-2.42631735478>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,3.80331810068,1.23885892056>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,1.14097002986,3.83382151266>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-2.5070283986,3.11685877265>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-3.98927893445,-0.2926663341>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-2.02530905649,-3.44936562656>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,1.688265582,-3.62625968797>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,3.943397377,-0.670534955897>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,2.79194448245,2.86444514818>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-0.771386906382,3.92491557115>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-3.66833989766,1.59476719155>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-3.39632224339,-2.11305352962>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-0.190321972361,-3.99546962782>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,3.18009183734,-2.42631735478>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,3.80331810068,1.23885892056>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-2.5070283986,3.11685877265>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-3.98927893445,-0.2926663341>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-2.02530905649,-3.44936562656>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,1.688265582,-3.62625968797>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,3.943397377,-0.670534955897>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,2.79194448245,2.86444514818>}
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


camera {orthographic location <-38.8850838889,0,69.9138773846> direction <0.486063548611,-0,-0.873923467308> right <23.9329259099,16.5538046575,13.3111460346> up <10.1267308544,-19.1699259301,5.63234072439> }
background {color rgb <0.65,0.63,0.52>}
light_source {<61.7721615574,18.3082493919,80> color rgb 1.099416260874988 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-2.44048317112,3.16923364419>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,1.22187570191,3.80880818224>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,3.82869219341,1.15806566659>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,3.12801442041,-2.49309562306>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-0.274862754405,-3.99054513397>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-3.44029410234,-2.04068039864>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-3.63375684145,1.67206794635>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-0.688124217301,3.94036610755>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,2.85195862301,2.80469820349>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,3.92831852304,-0.753865758314>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,1.61111991073,-3.66118732562>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-2.09787767496,-3.40571714341>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-3.99458061092,-0.208148367401>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-2.44048317112,3.16923364419>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,1.22187570191,3.80880818224>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,3.82869219341,1.15806566659>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,3.12801442041,-2.49309562306>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-0.274862754405,-3.99054513397>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-3.44029410234,-2.04068039864>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-3.63375684145,1.67206794635>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,2.85195862301,2.80469820349>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,3.92831852304,-0.753865758314>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,1.61111991073,-3.66118732562>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-2.09787767496,-3.40571714341>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-3.99458061092,-0.208148367401>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-2.44048317112,3.16923364419>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,1.22187570191,3.80880818224>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,3.82869219341,1.15806566659>}
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


camera {orthographic location <-42.3935411387,0,67.8438476925> direction <0.529919264233,-0,-0.848048096156> right <26.6231649804,-6.20085441789,16.6359998471> up <-3.68103594854,-21.9754228219,-2.30016654752> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-48,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-0.744157810267,-3.93016909985>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-3.65719557743,-1.62016064279>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-3.41088994861,2.08945680943>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-0.21801709214,3.9940541493>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.16319430015,2.44830590807>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,3.81181543009,-1.21246159812>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,1.16752163361,-3.82581928939>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-2.48535966789,-3.13416453321>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-3.99121205416,0.265002525844>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-2.04917406151,3.43524171866>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,1.66308496565,3.6378769079>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,3.93865394111,0.697857529989>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,2.81173594139,-2.84502038585>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-0.744157810267,-3.93016909985>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.65719557743,-1.62016064279>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-3.41088994861,2.08945680943>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-0.21801709214,3.9940541493>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.16319430015,2.44830590807>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,3.81181543009,-1.21246159812>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,1.16752163361,-3.82581928939>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-2.48535966789,-3.13416453321>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-3.99121205416,0.265002525844>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-2.04917406151,3.43524171866>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,1.66308496565,3.6378769079>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,3.93865394111,0.697857529989>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,2.81173594139,-2.84502038585>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-0.744157810267,-3.93016909985>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-3.65719557743,-1.62016064279>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-3.41088994861,2.08945680943>}
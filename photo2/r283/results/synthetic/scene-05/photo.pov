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


camera {orthographic location <-2.99794903278,0,79.9438071498> direction <0.0374743629097,-0,-0.999297589372> right <34.9259760514,12.0030956337,1.30974868292> up <8.39626517226,-24.4653679704,0.314865853273> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-13.9344544774,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.0859849188,-0.21764510612,3.99407443694>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.65127171032,3.16342230869,2.44801129427>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.21655850183,3.8117024913,-1.21281660519>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.78184529334,1.16716531198,-3.82592800958>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.34713208486,-2.48565155661,-3.13393304637>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.91241887637,-3.99118735592,0.265374245071>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.47770566789,-2.04885411238,3.435432553>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.0429924594,1.66342377104,3.63772200119>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.60827925092,3.93871891879,0.69749070157>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.17356604243,2.81147095905,-2.84528224372>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.73885283394,-0.744523842199,-3.93009977588>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.30413962546,-3.65734645476,-1.61982002391>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.869426416972,-3.41069533286,2.08977447262>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.434713208486,-0.21764510612,3.99407443694>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,3.16342230869,2.44801129427>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.434713208486,3.8117024913,-1.21281660519>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.869426416972,1.16716531198,-3.82592800958>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.30413962546,-2.48565155661,-3.13393304637>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.73885283394,-3.99118735592,0.265374245071>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.17356604243,-2.04885411238,3.435432553>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.60827925092,1.66342377104,3.63772200119>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.0429924594,3.93871891879,0.69749070157>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.47770566789,2.81147095905,-2.84528224372>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.91241887637,-0.744523842199,-3.93009977588>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.34713208486,-3.65734645476,-1.61982002391>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.78184529334,-3.41069533286,2.08977447262>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.21655850183,-0.21764510612,3.99407443694>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.65127171032,3.16342230869,2.44801129427>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.0859849188,3.8117024913,-1.21281660519>}
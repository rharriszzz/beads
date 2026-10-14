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


camera {orthographic location <14.0713159406,-0,78.7527654607> direction <-0.175891449257,0,-0.984409568258> right <38.6890353486,-7.44117742782,-6.91284473176> up <-5.12761638134,-27.5112368035,0.916187637373> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-61.7067181048,26.2397861022,80> color rgb 1.2555280473270263 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,3.5722825582,1.79966589244>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,0.548191793197,3.9622576592>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-2.94946569387,2.70197189487>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-3.89916675796,-0.892467698927>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-1.48049265977,-3.71593076959>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,2.21713538233,-3.32931084406>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,3.99944555864,-0.0665974732588>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,2.32675267434,3.2536474905>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-1.35595322134,3.76316234855>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-3.86729112085,1.02179224237>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-3.03779028087,-2.6022740458>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,0.415967987804,-3.97831253588>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,3.51038378015,-1.91760416042>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,3.5722825582,1.79966589244>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,0.548191793197,3.9622576592>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-2.94946569387,2.70197189487>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-3.89916675796,-0.892467698927>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-1.48049265977,-3.71593076959>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,2.21713538233,-3.32931084406>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,3.99944555864,-0.0665974732588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,2.32675267434,3.2536474905>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-3.86729112085,1.02179224237>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-3.03779028087,-2.6022740458>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,0.415967987804,-3.97831253588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,3.51038378015,-1.91760416042>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,3.5722825582,1.79966589244>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,0.548191793197,3.9622576592>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-2.94946569387,2.70197189487>}
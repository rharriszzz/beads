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


camera {orthographic location <-12.3641176214,0,79.0387790609> direction <0.154551470267,-0,-0.987984738262> right <33.7416777042,-20.824008049,5.27824539844> up <-14.4016614993,-23.9064162413,-2.25286674257> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-1.54645108528,28.5276596621,80> color rgb 1.2533736504537905 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,2.73302689587,2.92071292434>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-0.851163382229,3.908391088>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-3.70005871818,1.51972546272>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-3.35258245504,-2.18178616784>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-0.108909088252,-3.99851707643>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,3.22884762777,-2.3610470128>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,3.77729810805,1.31606192973>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,1.06265215839,3.8562637864>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-2.56998764961,3.06515309256>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-3.98249092495,-0.373852955959>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-1.95463774767,-3.48989846204>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,1.76176933079,-3.59112361596>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,3.95623584506,-0.590082992715>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,2.73302689587,2.92071292434>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,-0.851163382229,3.908391088>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-3.70005871818,1.51972546272>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-3.35258245504,-2.18178616784>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-0.108909088252,-3.99851707643>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,3.22884762777,-2.3610470128>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,3.77729810805,1.31606192973>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,1.06265215839,3.8562637864>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-2.56998764961,3.06515309256>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-3.98249092495,-0.373852955959>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-1.95463774767,-3.48989846204>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,1.76176933079,-3.59112361596>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,3.95623584506,-0.590082992715>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,2.73302689587,2.92071292434>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-0.851163382229,3.908391088>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-3.70005871818,1.51972546272>}
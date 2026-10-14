#version 3.7;
global_settings { assumed_gamma 1.0 }
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


camera { orthographic location <40,-0,69.2820323> direction <-0.5,0,-0.8660254038> right <23.07340426,-1.126261736,-13.32143616> up <-0.6827598922,-18.65001063,0.3941916076> }
background { color rgb <.47,.31,.43> }
light_source { <48,32,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.771192595,0.4826664815,-3.970772352> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.358964553,3.542067393,-1.858429063> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651,3.541580752,1.859356281> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.534508468,0.4816269523,3.970898573> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,-2.994390166,2.652098703> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.710052383,-3.883641935,-0.9577710167> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.29782434,-1.417929978,-3.740250603> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.885596298,2.272689867,-3.291638007> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.473368255,3.999999966,0.0005235820727> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.061140213,2.271828068,3.292232864> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.64891217,-1.418909094,3.739879274> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.236684128,-3.883892538,0.9567542812> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.8244560851,-2.993695768,-2.652882517> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.4122280425,0.4826664815,-3.970772352> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,3.542067393,-1.858429063> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.4122280425,3.541580752,1.859356281> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.8244560851,0.4816269523,3.970898573> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.236684128,-2.994390166,2.652098703> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.64891217,-3.883641935,-0.9577710167> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.061140213,-1.417929978,-3.740250603> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.473368255,2.272689867,-3.291638007> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.885596298,3.999999966,0.0005235820727> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.29782434,2.271828068,3.292232864> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.710052383,-1.418909094,3.739879274> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,-3.883892538,0.9567542812> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.534508468,-2.993695768,-2.652882517> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651,0.4826664815,-3.970772352> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.358964553,3.542067393,-1.858429063> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.771192595,3.541580752,1.859356281> }
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


camera { orthographic location <40,-0,69.2820323> direction <-0.5,0,-0.8660254038> right <21.65989801,-9.250740617,-12.50534795> up <-5.607963465,-17.50748713,3.237759216> }
background { color rgb <.47,.31,.43> }
light_source { <48,32,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.771192595,-3.865288308,-1.029342651> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.358964553,-1.348601629,-3.765803187> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651,2.333102222,-3.249097416> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.534508468,3.999307875,0.0744077854> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,2.210629408,3.333634296> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.710052383,-1.487746605,3.713032459> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.29782434,-3.900902205,0.8848513905> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.885596298,-2.944183441,-2.707726697> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.473368255,0.5559285635,-3.961179551> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.061140213,3.575790279,-1.79268622> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.64891217,3.506632235,1.924455864> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.236684128,0.4081980257,3.979117286> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.8244560851,-3.042866418,2.596336642> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.4122280425,-3.865288308,-1.029342651> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,-1.348601629,-3.765803187> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.4122280425,2.333102222,-3.249097416> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.8244560851,3.999307875,0.0744077854> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.236684128,2.210629408,3.333634296> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.64891217,-1.487746605,3.713032459> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.061140213,-3.900902205,0.8848513905> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.473368255,-2.944183441,-2.707726697> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.885596298,0.5559285635,-3.961179551> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.29782434,3.575790279,-1.79268622> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.710052383,3.506632235,1.924455864> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,0.4081980257,3.979117286> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.534508468,-3.042866418,2.596336642> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651,-3.865288308,-1.029342651> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.358964553,-1.348601629,-3.765803187> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.771192595,2.333102222,-3.249097416> }
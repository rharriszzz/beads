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


camera { orthographic location <40,-0,69.2820323> direction <-0.5,0,-0.8660254038> right <22.97165104,-2.741430695,-13.26268891> up <-1.661904037,-18.56776448,0.9595007431> }
background { color rgb <.47,.31,.43> }
light_source { <48,32,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.771192595,3.350074935,-2.185634446> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.358964553,0.1043175832,-3.998639499> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651,-3.231556652,-2.357337822> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.534508468,-3.775784405,1.320398473> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,-1.058223372,3.857481471> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.710052383,2.573505622,3.062199996> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.29782434,3.98205901,-0.3784257402> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.885596298,1.950629064,-3.492140641> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.473368255,-1.765891799,-3.589098237> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.061140213,-3.95691082,-0.5855397213> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.64891217,-2.729671286,2.92384929> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.236684128,0.8556507641,3.907411134> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.8244560851,3.701801355,1.515475742> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.4122280425,3.350074935,-2.185634446> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,0.1043175832,-3.998639499> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.4122280425,-3.231556652,-2.357337822> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.8244560851,-3.775784405,1.320398473> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.236684128,-1.058223372,3.857481471> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.64891217,2.573505622,3.062199996> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.061140213,3.98205901,-0.3784257402> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.473368255,1.950629064,-3.492140641> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.885596298,-1.765891799,-3.589098237> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.29782434,-3.95691082,-0.5855397213> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.710052383,-2.729671286,2.92384929> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,0.8556507641,3.907411134> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.534508468,3.701801355,1.515475742> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651,3.350074935,-2.185634446> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.358964553,0.1043175832,-3.998639499> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.771192595,-3.231556652,-2.357337822> }
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


camera { orthographic location <0,-0,80> direction <-0,0,-1> right <24.44947581,10.64585571,0> up <7.452098997,-17.11463307,-0> }
background { color rgb <.47,.31,.43> }
light_source { <-40,-56,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.246538723,-2.933542727,2.719251196> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.871785957,0.5714576551,3.958969076> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.497033191,3.582792624,1.778650336> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,3.499058714,-1.938191972> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.747527659,0.3925911802,-3.980687399> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.372774893,-3.053024295,-2.584384386> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.998022127,-3.861222126,1.044492075> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.623269362,-1.333824043,3.771062638> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.248516596,2.345825291,3.23992341> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376383,3.998985343,-0.09009009564> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.499011064,2.197539901,-3.342277425> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.124258298,-1.502295449,-3.707169862> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.7495055319,-3.904342068,-0.8695475927> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.3747527659,-2.933542727,2.719251196> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,0.5714576551,3.958969076> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.3747527659,3.582792624,1.778650336> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.7495055319,3.499058714,-1.938191972> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.124258298,0.3925911802,-3.980687399> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.499011064,-3.053024295,-2.584384386> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.87376383,-3.861222126,1.044492075> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.248516596,-1.333824043,3.771062638> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.623269362,2.345825291,3.23992341> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.998022127,3.998985343,-0.09009009564> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.372774893,2.197539901,-3.342277425> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.747527659,-1.502295449,-3.707169862> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,-3.904342068,-0.8695475927> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.497033191,-2.933542727,2.719251196> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.871785957,0.5714576551,3.958969076> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.246538723,3.582792624,1.778650336> }
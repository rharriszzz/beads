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


camera { orthographic location <40,-0,69.2820323> direction <-0.5,0,-0.8660254038> right <22.58449083,-5.570650125,-13.03916186> up <-3.377027166,-18.25482661,1.949727544> }
background { color rgb <.47,.31,.43> }
light_source { <-40,-56,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.246538723,-1.985134774,3.472641635> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.871785957,-3.985613121,0.3389514004> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.497033191,-2.543037842,-3.087548953> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,1.096392826,-3.846806828> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.747527659,3.788682067,-1.28292174> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.372774893,3.208040613,2.389241601> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.998022127,-0.1439325113,3.99740959> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.623269362,-3.371566584,2.152333332> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.248516596,-3.686603724,-1.552080212> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376383,-0.8168926375,-3.915697437> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.499011064,2.758507905,-2.896659134> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.124258298,3.950914827,0.6247175628> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.7495055319,1.730242955,3.606419182> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.3747527659,-1.985134774,3.472641635> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.985613121,0.3389514004> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.3747527659,-2.543037842,-3.087548953> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.7495055319,1.096392826,-3.846806828> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.124258298,3.788682067,-1.28292174> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.499011064,3.208040613,2.389241601> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.87376383,-0.1439325113,3.99740959> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.248516596,-3.371566584,2.152333332> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.623269362,-3.686603724,-1.552080212> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.998022127,-0.8168926375,-3.915697437> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.372774893,2.758507905,-2.896659134> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.747527659,3.950914827,0.6247175628> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,1.730242955,3.606419182> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.497033191,-1.985134774,3.472641635> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.871785957,-3.985613121,0.3389514004> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.246538723,-2.543037842,-3.087548953> }
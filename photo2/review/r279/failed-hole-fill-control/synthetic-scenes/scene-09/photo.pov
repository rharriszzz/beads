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


camera { orthographic location <40,-0,69.2820323> direction <-0.5,0,-0.8660254038> right <21.41874069,9.971351014,-12.3661157> up <6.044810302,-17.31256198,-3.489972855> }
background { color rgb <.47,.31,.43> }
light_source { <-40,-56,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.246538723,3.364269214,2.163721946> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.871785957,3.69183099,-1.539605124> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.497033191,0.8301288593,-3.912912736> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,-2.74869711,-2.90597044> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.747527659,-3.953004714,0.6113540117> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.372774893,-1.742428134,3.600547764> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.998022127,1.973380721,3.479334495> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.623269362,3.984444173,0.352426774> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.248516596,2.553463819,-3.078932043> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376383,-1.083378618,-3.850492276> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.499011064,-3.784322219,-1.295725797> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.124258298,-3.216101468,2.378379983> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.7495055319,0.1304144873,3.997873442> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.3747527659,3.364269214,2.163721946> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,3.69183099,-1.539605124> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.3747527659,0.8301288593,-3.912912736> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.7495055319,-2.74869711,-2.90597044> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.124258298,-3.953004714,0.6113540117> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.499011064,-1.742428134,3.600547764> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.87376383,1.973380721,3.479334495> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.248516596,3.984444173,0.352426774> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.623269362,2.553463819,-3.078932043> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.998022127,-1.083378618,-3.850492276> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.372774893,-3.784322219,-1.295725797> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.747527659,-3.216101468,2.378379983> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,0.1304144873,3.997873442> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.497033191,3.364269214,2.163721946> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.871785957,3.69183099,-1.539605124> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.246538723,0.8301288593,-3.912912736> }
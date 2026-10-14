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


camera { orthographic location <40,-0,69.2820323> direction <-0.5,0,-0.8660254038> right <20.22317093,-12.87668129,-11.67585318> up <-7.806073181,-16.34619445,4.506838452> }
background { color rgb <.47,.31,.43> }
light_source { <-40,-56,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.246538723,-3.566818722,1.810470713> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.871785957,-0.5361957881,3.963898848> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.497033191,2.957630873,2.693031678> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,3.896447454,-0.9042661321> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.747527659,1.469237999,-3.7203951> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.372774893,-2.227202831,-3.322584469> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.998022127,-3.999628823,-0.05449110905> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.623269362,-2.316893438,3.260675513> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.248516596,1.367337855,3.759040727> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376383,3.870366302,1.010081525> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.499011064,3.029899452,-2.611457316> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.124258298,-0.428008173,-3.977035203> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.7495055319,-3.51617216,-1.906969674> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.3747527659,-3.566818722,1.810470713> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,-0.5361957881,3.963898848> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.3747527659,2.957630873,2.693031678> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.7495055319,3.896447454,-0.9042661321> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.124258298,1.469237999,-3.7203951> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.499011064,-2.227202831,-3.322584469> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.87376383,-3.999628823,-0.05449110905> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.248516596,-2.316893438,3.260675513> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.623269362,1.367337855,3.759040727> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.998022127,3.870366302,1.010081525> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.372774893,3.029899452,-2.611457316> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.747527659,-0.428008173,-3.977035203> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,-3.51617216,-1.906969674> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.497033191,-3.566818722,1.810470713> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.871785957,-0.5361957881,3.963898848> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.246538723,2.957630873,2.693031678> }
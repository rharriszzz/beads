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


camera {orthographic location <-5.35498243011,0,79.8205748111> direction <0.0669372803764,-0,-0.997757185139> right <36.2603420149,14.6456774552,2.43262460662> up <10.2289809385,-25.4392950394,0.686239272686> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-43.7593374144,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.15768911362,-2.45540209777>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,0.226984444162,-3.99355456481>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,3.41557283519,-2.08179302706>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,3.65354859096,1.62836810748>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,0.735331474803,3.93183006018>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-2.81811681497,2.83869998718>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-3.93707710431,-0.706699281663>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-1.65491260127,-3.64160188408>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,2.0568820889,-3.43063202229>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,3.99179700705,-0.256040337658>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,2.47831622272,3.13973704316>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-1.17610885229,3.82318819411>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-3.81452817733,1.20389982322>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.15768911362,-2.45540209777>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,0.226984444162,-3.99355456481>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,3.41557283519,-2.08179302706>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,3.65354859096,1.62836810748>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,0.735331474803,3.93183006018>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-2.81811681497,2.83869998718>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-3.93707710431,-0.706699281663>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-1.65491260127,-3.64160188408>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,2.0568820889,-3.43063202229>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,3.99179700705,-0.256040337658>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,2.47831622272,3.13973704316>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-1.17610885229,3.82318819411>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-3.81452817733,1.20389982322>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.15768911362,-2.45540209777>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,0.226984444162,-3.99355456481>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,3.41557283519,-2.08179302706>}
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


camera {orthographic location <-28.9431131782,0,74.5808031571> direction <0.361788914728,-0,-0.932260039463> right <29.2974611893,6.0323448591,11.3696782435> up <3.93659983948,-21.9983931139,1.52770484989> }
background {color rgb <0.65,0.63,0.52>}
light_source {<26.4537877783,-2.29225029356,80> color rgb 1.0077564288390521 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-1.13456979987,3.83572044983>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,2.51222693828,3.11267020588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,3.98878491871,-0.299324025502>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,2.01954925095,-3.45274105936>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-1.69431545121,-3.62343692532>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-3.9445110063,-0.663952499202>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-2.78715984033,2.86910090872>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,0.7779365087,3.92362266132>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,3.67099645191,1.58864251802>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,3.39279083071,-2.11871904203>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,0.183653276008,-3.99578171003>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-3.18413692727,-2.42100640817>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-3.8012451503,1.24520492584>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-1.13456979987,3.83572044983>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,2.51222693828,3.11267020588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,3.98878491871,-0.299324025502>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,2.01954925095,-3.45274105936>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-1.69431545121,-3.62343692532>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-3.9445110063,-0.663952499202>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-2.78715984033,2.86910090872>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,0.7779365087,3.92362266132>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,3.67099645191,1.58864251802>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,3.39279083071,-2.11871904203>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,0.183653276008,-3.99578171003>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-3.18413692727,-2.42100640817>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-3.8012451503,1.24520492584>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-1.13456979987,3.83572044983>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,2.51222693828,3.11267020588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,3.98878491871,-0.299324025502>}
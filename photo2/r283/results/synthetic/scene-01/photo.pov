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


camera {orthographic location <-6.84823738228,0,79.7063463267> direction <0.0856029672785,-0,-0.996329329084> right <36.2004532441,-11.0988428196,3.11028304002> up <-7.74067183403,-25.4336759254,-0.665065715099> }
background {color rgb <0.47,0.31,0.43>}
light_source {<43.118520673,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.0859849188,2.91058168216,2.74381381866>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.65127171032,3.91151334989,-0.836697862809>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.21655850183,1.53340399872,-3.69441093771>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.78184529334,-2.16936784155,-3.3606313645>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.34713208486,-3.99808678567,-0.123701472146>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.91241887637,-2.37297647308,3.22009047361>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.47770566789,1.30207822732,3.78214123083>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.0429924594,3.85230594993,1.07691172718>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.60827925092,3.07464018024,-2.55863005573>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.17356604243,-0.35911655938,-3.98384679635>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.73885283394,-3.48264309494,-1.96753578704>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.30413962546,-3.59761697598,1.74847135925>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.869426416972,-0.604715657656,3.95402566676>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.434713208486,2.91058168216,2.74381381866>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,3.91151334989,-0.836697862809>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.434713208486,1.53340399872,-3.69441093771>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.869426416972,-2.16936784155,-3.3606313645>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.30413962546,-3.99808678567,-0.123701472146>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.73885283394,-2.37297647308,3.22009047361>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.17356604243,1.30207822732,3.78214123083>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.60827925092,3.85230594993,1.07691172718>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.0429924594,3.07464018024,-2.55863005573>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.47770566789,-0.35911655938,-3.98384679635>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.91241887637,-3.48264309494,-1.96753578704>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.34713208486,-3.59761697598,1.74847135925>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.78184529334,-0.604715657656,3.95402566676>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.21655850183,2.91058168216,2.74381381866>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.65127171032,3.91151334989,-0.836697862809>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.0859849188,1.53340399872,-3.69441093771>}
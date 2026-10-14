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


camera {orthographic location <-11.5424922211,0,79.1629387613> direction <0.144281152763,-0,-0.989536734516> right <33.7993285029,2.03319251742,4.92817083886> up <1.40834307903,-23.9097035277,0.205345952142> }
background {color rgb <0.47,0.31,0.43>}
light_source {<4.23256366557,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.0859849188,1.39048192004,-3.75054129827>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.65127171032,-2.2967512171,-3.27489447872>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.21655850183,-3.99988871694,0.029837093021>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.78184529334,-2.24764032478,3.3087932801>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.34713208486,1.44627825326,3.72938054027>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.91241887637,3.89079970406,0.928265944046>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.47770566789,2.97417404368,-2.67475022346>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.0429924594,-0.51175285435,-3.96712856057>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.60827925092,-3.55559155487,-1.83242153855>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.17356604243,-3.52785957784,1.88526040616>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.73885283394,-0.452513760311,3.97432148885>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.30413962546,3.01374534855,2.63008345382>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.869426416972,3.87651873659,-0.986206106695>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.434713208486,1.39048192004,-3.75054129827>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.2967512171,-3.27489447872>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.434713208486,-3.99988871694,0.029837093021>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.869426416972,-2.24764032478,3.3087932801>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.30413962546,1.44627825326,3.72938054027>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.73885283394,3.89079970406,0.928265944046>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.17356604243,2.97417404368,-2.67475022346>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.60827925092,-0.51175285435,-3.96712856057>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.0429924594,-3.55559155487,-1.83242153855>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.47770566789,-3.52785957784,1.88526040616>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.91241887637,-0.452513760311,3.97432148885>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.34713208486,3.01374534855,2.63008345382>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.78184529334,3.87651873659,-0.986206106695>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.21655850183,1.39048192004,-3.75054129827>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.65127171032,-2.2967512171,-3.27489447872>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.0859849188,-3.99988871694,0.029837093021>}
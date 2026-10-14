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


camera {orthographic location <8.64810460461,-0,79.5311906534> direction <-0.108101307558,0,-0.994139883168> right <27.5654162041,-15.9738312923,-2.99742278274> up <-11.1161559423,-19.4095334767,1.20875443458> }
background {color rgb <0.46,0.38,0.31>}
light_source {<52.1337650776,24.9461564627,80> color rgb 1.261849111741836 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.46,0.38,0.31>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-2.99089492976,-2.65603981882>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.88489988883,0.95265568479>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-1.42285441309,3.73838003942>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,2.26835302522,3.29462813577>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,3.99999718662,0.00474415561536>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,2.27616175227,-3.28923816065>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-1.41398268797,-3.74174464095>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-3.88262918733,-0.96186828294>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-2.99718684392,2.64893771588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,0.477436816527,3.9714045483>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,3.53961689244,1.86309212191>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,3.54402633054,-1.85469063956>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,0.486855947286,-3.97026085876>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-2.99089492976,-2.65603981882>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.88489988883,0.95265568479>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-1.42285441309,3.73838003942>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,2.26835302522,3.29462813577>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,3.99999718662,0.00474415561536>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,2.27616175227,-3.28923816065>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-1.41398268797,-3.74174464095>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-3.88262918733,-0.96186828294>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-2.99718684392,2.64893771588>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,3.53961689244,1.86309212191>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,3.54402633054,-1.85469063956>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,0.486855947286,-3.97026085876>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-2.99089492976,-2.65603981882>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.88489988883,0.95265568479>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-1.42285441309,3.73838003942>}
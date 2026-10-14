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


camera {orthographic location <17.0790316671,-0,78.1556567199> direction <-0.213487895839,0,-0.976945708998> right <28.1172689018,-27.7788795666,-6.14435021238> up <-18.9969200353,-20.1465527203,4.1513181832> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-20.9045500957,48.0963996841,80> color rgb 1.2060230294709635 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-2.50509353603,3.11841408022>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-3.98945980028,-0.290190458026>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-2.02744940605,-3.44810801831>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,1.68601473357,-3.62730675822>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.94298047127,-0.672982171538>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,2.79372167199,2.86271186456>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-0.768950883199,3.92539355215>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-3.66734944941,1.59704352348>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-3.39763298911,-2.11094530277>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-0.192801597477,-3.99535074105>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.17858540783,-2.42829051086>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,3.8040862268,1.23649827297>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,1.14334915011,3.83311266739>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-2.50509353603,3.11841408022>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.98945980028,-0.290190458026>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-2.02744940605,-3.44810801831>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,1.68601473357,-3.62730675822>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.94298047127,-0.672982171538>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,2.79372167199,2.86271186456>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-3.66734944941,1.59704352348>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-3.39763298911,-2.11094530277>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-0.192801597477,-3.99535074105>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.17858540783,-2.42829051086>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,3.8040862268,1.23649827297>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,1.14334915011,3.83311266739>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-2.50509353603,3.11841408022>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-3.98945980028,-0.290190458026>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-2.02744940605,-3.44810801831>}
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


camera {orthographic location <-26.9104649172,0,75.3380838483> direction <0.336380811466,-0,-0.941726048104> right <26.8594560106,14.5094119973,9.59409121851> up <9.56472385437,-19.9650622867,3.41648144708> }
background {color rgb <0.46,0.38,0.31>}
light_source {<-40.0622956091,48.2420521916,80> color rgb 1.277894570096544 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.46,0.38,0.31>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-3.85707450009,-1.0597057614>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.06318879325,2.57232859816>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,0.37689536804,3.98220414865>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,3.49139073683,1.95197098411>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,3.58977662127,-1.76451234322>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,0.587060357539,-3.95668549882>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-2.92280003463,-2.73079474834>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-3.90773968037,0.854149044637>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-1.51689826902,3.70121866977>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,2.18434681836,3.35091464784>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,3.99859911331,0.105854291718>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,2.3585795668,-3.23065046501>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-1.31894730479,-3.77629156809>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-3.85707450009,-1.0597057614>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.06318879325,2.57232859816>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,0.37689536804,3.98220414865>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,3.49139073683,1.95197098411>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,3.58977662127,-1.76451234322>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,0.587060357539,-3.95668549882>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-2.92280003463,-2.73079474835>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-3.90773968037,0.854149044637>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-1.51689826902,3.70121866977>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,3.99859911331,0.105854291718>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,2.3585795668,-3.23065046501>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-1.31894730479,-3.77629156809>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-3.85707450009,-1.0597057614>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.06318879325,2.57232859816>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,0.37689536804,3.98220414865>}
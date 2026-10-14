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


camera {orthographic location <0,-0,80> direction <-0,0,-1> right <35.5347716065,1.21554010132,0> up <0.850878070923,-24.8743401246,-0> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-48,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-3.99338335137,0.229976975001>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-2.07923296214,3.41713188056>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,1.6311054593,3.65232733755>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,3.9323799814,0.732384927413>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,2.83658741707,-2.82024322095>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-0.709649356083,-3.93654642947>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-3.64284098053,-1.65218327996>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-3.42908972189,2.05945227651>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-0.253048988239,3.99198775168>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,3.14159330306,2.47596274571>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,3.82230579631,-1.17897345156>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,1.20104104516,-3.81542925604>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-2.45776764205,-3.15584825644>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-3.99338335137,0.229976975001>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.07923296214,3.41713188056>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,1.6311054593,3.65232733755>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,3.9323799814,0.732384927413>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,2.83658741707,-2.82024322095>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-0.709649356083,-3.93654642947>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-3.64284098053,-1.65218327996>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-3.42908972189,2.05945227651>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-0.253048988239,3.99198775168>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,3.14159330306,2.47596274571>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,3.82230579631,-1.17897345156>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,1.20104104516,-3.81542925604>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-2.45776764205,-3.15584825644>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-3.99338335137,0.229976975001>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-2.07923296214,3.41713188056>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.5 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,1.6311054593,3.65232733755>}

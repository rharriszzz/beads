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


camera {orthographic location <-32.5389314461,0,73.0836366114> direction <0.406736643076,-0,-0.913545457643> right <31.3671877744,9.23362696883,13.9655717746> up <5.90473658246,-24.0349631848,2.6289581057> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-48,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-0.194205557051,3.99528274364>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.39837456828,2.10975123976>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-3.6667880198,-1.59833213627>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-0.767571447293,-3.92566352013>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,2.79472746019,-2.86172997036>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,3.94274374101,0.674367698483>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,1.68473998913,3.62789900204>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-2.02866095054,3.44739535704>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-3.98956152727,0.288788538716>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-2.50399756658,-3.11929418083>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,1.14469604033,-3.83271065634>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,3.80452049904,-1.23516143575>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,3.17773190712,2.42940732>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-0.194205557051,3.99528274364>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.39837456828,2.10975123976>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-3.6667880198,-1.59833213627>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-0.767571447293,-3.92566352013>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,2.79472746019,-2.86172997036>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,3.94274374101,0.674367698483>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,1.68473998913,3.62789900204>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-2.02866095054,3.44739535704>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-3.98956152727,0.288788538716>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-2.50399756658,-3.11929418083>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,1.14469604033,-3.83271065634>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,3.80452049904,-1.23516143575>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,3.17773190712,2.42940732>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-0.194205557051,3.99528274364>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.39837456828,2.10975123976>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-3.6667880198,-1.59833213627>}

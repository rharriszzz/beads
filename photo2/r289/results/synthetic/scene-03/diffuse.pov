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


camera {orthographic location <-33.8094609393,0,72.5046229629> direction <0.422618261741,-0,-0.906307787037> right <31.5145921223,-7.42094480655,14.6954956503> up <-4.70796204574,-24.340753551,-2.19535875623> }
background {color rgb <0.47,0.31,0.43>}
light_source {<56,-32,80> color rgb 0.55 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-0.0824478529378,3.99915020367>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.24440037621,2.33962950034>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,3.76850680895,-1.34102812457>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,1.03711135575,-3.86321110422>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-2.59021400968,-3.04807995041>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-3.97992988653,0.400197574132>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-1.93150171632,3.50275621759>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,1.78549381994,3.57938707308>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,3.96005390555,0.563891004655>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,2.71364021785,-2.93873387159>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-0.877007219404,-3.90267322961>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-3.7100339858,-1.49520828791>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-3.33807181361,2.20392299484>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-0.0824478529378,3.99915020367>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,3.24440037621,2.33962950034>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,3.76850680895,-1.34102812457>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,1.03711135575,-3.86321110422>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-2.59021400968,-3.04807995041>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-3.97992988653,0.400197574132>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-1.93150171632,3.50275621759>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,1.78549381994,3.57938707308>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,3.96005390555,0.563891004655>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,2.71364021785,-2.93873387159>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-0.877007219404,-3.90267322961>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-3.7100339858,-1.49520828791>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-3.33807181361,2.20392299484>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-0.0824478529378,3.99915020367>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.24440037621,2.33962950034>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,3.76850680895,-1.34102812457>}

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


camera {orthographic location <23.5469613601,-0,76.4561352064> direction <-0.294337017001,0,-0.955701690081> right <28.2021789301,-12.9278226104,-8.68570737646> up <-8.64859934248,-20.656576687,2.66359572043> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-34.8221894877,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.50570801665,3.9216866866,0.787637944816>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.04101458689,2.87598527513,-2.78005552053>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.57632115713,-0.654194992761,-3.94614101515>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.11162772737,-3.61923550089,-1.70327167215>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.64693429761,-3.45772520358,2.01100383305>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.18224086785,-0.30918808319,3.98803243834>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.71754743809,3.10644750324,2.51991744103>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.25285400833,3.83851471151,-1.12507991249>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.78816057856,1.2546022716,-3.79815391211>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.3234671488,-2.41312406818,-3.19011476777>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.85877371904,-3.99622369685,0.173770436919>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.39408028928,-2.12710353628,3.38754048625>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.929386859522,1.57955863364,3.6749142198>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.464693429761,3.9216866866,0.787637944816>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,2.87598527513,-2.78005552053>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.464693429761,-0.654194992761,-3.94614101515>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.929386859522,-3.61923550089,-1.70327167215>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.39408028928,-3.45772520358,2.01100383305>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.85877371904,-0.30918808319,3.98803243834>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.3234671488,3.10644750324,2.51991744103>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.78816057856,3.83851471151,-1.12507991249>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.25285400833,1.2546022716,-3.79815391211>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.71754743809,-2.41312406818,-3.19011476777>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.18224086785,-3.99622369685,0.173770436919>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.64693429761,-2.12710353628,3.38754048625>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.11162772737,1.57955863364,3.6749142198>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.57632115713,3.9216866866,0.787637944816>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.04101458689,2.87598527513,-2.78005552053>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.50570801665,-0.654194992761,-3.94614101515>}
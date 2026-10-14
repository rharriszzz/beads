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


camera {orthographic location <49.2529180261,-0,63.0408602885> direction <-0.615661475326,0,-0.788010753607> right <24.5752766737,-7.16964822738,-19.2003104326> up <-3.95483193193,-21.8305316176,3.08985334366> }
background {color rgb <0.46,0.38,0.31>}
light_source {<24,-80,24> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.46,0.38,0.31>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.76155372964,1.36040932776>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.2564009945,-2.32289744996>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-0.0618605172472,-3.99952163095>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-3.32668255262,-2.2210770347>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.71768164618,1.47609050457>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-0.897085212899,3.89810699196>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,2.69847667765,2.95266381767>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.9629041538,-0.543498544431>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,1.80389561124,-3.57014854365>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-1.91344514674,-3.51265251205>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.97781707658,-0.420679575576>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-2.60587015356,3.03470603894>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,1.01721113899,3.86849861041>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.76155372964,1.36040932776>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,3.2564009945,-2.32289744996>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-0.0618605172472,-3.99952163095>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-3.32668255262,-2.2210770347>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.71768164618,1.47609050457>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-0.897085212899,3.89810699196>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,2.69847667765,2.95266381767>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.9629041538,-0.543498544431>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,1.80389561124,-3.57014854365>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-1.91344514674,-3.51265251205>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.97781707658,-0.420679575576>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-2.60587015356,3.03470603894>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,1.01721113899,3.86849861041>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.76155372964,1.36040932776>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.2564009945,-2.32289744996>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 0.6 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-0.0618605172472,-3.99952163095>}
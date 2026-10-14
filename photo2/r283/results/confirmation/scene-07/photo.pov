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


camera {orthographic location <-26.6877561199,0,75.4172637616> direction <0.333596951499,-0,-0.94271579702> right <31.2861896503,-8.30875274859,11.0711812875> up <-5.48295472874,-23.2311082772,-1.94024221138> }
background {color rgb <0.47,0.31,0.43>}
light_source {<14.1741140252,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.50570801665,-1.67595683063,3.63196485416>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.04101458689,2.03699648394,3.44247662656>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.57632115713,3.99024861412,0.279134371829>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.11162772737,2.4964426528,-3.12534383409>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.64693429761,-1.15396648753,-3.82992967894>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.18224086785,-3.80749801375,-1.22595223205>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.71754743809,-3.1718443022,2.43708919054>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.25285400833,0.203872153359,3.99480113962>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.78816057856,3.40346946852,2.1015222047>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.3234671488,3.66290988993,-1.60719978169>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.85877371904,0.75807048932,-3.92750927857>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.39408028928,-2.80164364889,-2.85495934553>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.929386859522,-3.94110046899,0.68390576347>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.464693429761,-1.67595683063,3.63196485416>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,2.03699648394,3.44247662656>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.464693429761,3.99024861412,0.279134371829>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.929386859522,2.4964426528,-3.12534383409>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.39408028928,-1.15396648753,-3.82992967894>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.85877371904,-3.80749801375,-1.22595223205>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.3234671488,-3.1718443022,2.43708919054>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.78816057856,0.203872153359,3.99480113962>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.25285400833,3.40346946852,2.1015222047>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.71754743809,3.66290988993,-1.60719978169>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.18224086785,0.75807048932,-3.92750927857>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.64693429761,-2.80164364889,-2.85495934553>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.11162772737,-3.94110046899,0.68390576347>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.57632115713,-1.67595683063,3.63196485416>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.04101458689,2.03699648394,3.44247662656>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.50570801665,3.99024861412,0.279134371829>}
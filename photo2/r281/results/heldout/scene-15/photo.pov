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


camera {orthographic location <-6.75804079709,0,79.7140444626> direction <0.0844755099637,-0,-0.996425555782> right <31.5948446564,-4.3117375501,2.67856499573> up <-3.00742783933,-22.1957286534,-0.254965359862> }
background {color rgb <0.46,0.38,0.31>}
light_source {<35.7727153898,11.1987164676,80> color rgb 0.9695791424007284 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.46,0.38,0.31>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-0.718806988185,-3.93488456168>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.64667541811,-1.64370264798>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-3.42428850741,2.06742550483>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-0.243759749286,3.99256573955>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,3.14734586693,2.46864618646>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,3.81955221483,-1.18786399819>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,1.19216005616,-3.81821350902>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-2.4651040141,-3.15012098175>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-3.99283743103,0.239268153682>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-2.07127635389,3.421960588>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,1.63959927626,3.64852219581>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,3.93407344911,0.723233086211>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,2.83001759872,-2.82683575591>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-0.718806988185,-3.93488456168>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.64667541811,-1.64370264798>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-3.42428850741,2.06742550483>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-0.243759749286,3.99256573955>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,3.14734586693,2.46864618646>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,3.81955221483,-1.18786399819>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,1.19216005616,-3.81821350902>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-2.4651040141,-3.15012098175>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-3.99283743103,0.239268153682>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-2.07127635389,3.421960588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,1.63959927626,3.64852219581>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,3.93407344911,0.723233086211>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,2.83001759872,-2.82683575591>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-0.718806988185,-3.93488456168>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.64667541811,-1.64370264798>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-3.42428850741,2.06742550483>}
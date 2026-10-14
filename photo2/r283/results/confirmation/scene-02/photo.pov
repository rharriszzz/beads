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


camera {orthographic location <-6.69097172288,0,79.7197020654> direction <0.083637146536,-0,-0.996496275818> right <32.605952365,-16.9685024316,2.73665730829> up <-11.8363346355,-22.9044174167,-0.993437987058> }
background {color rgb <0.47,0.31,0.43>}
light_source {<24.4872348131,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.51443944043,-1.91016109781>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.56846091538,1.80723177689>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,0.539794251807,3.96341042105>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-2.9551847455,2.69571569717>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.8972667998,-0.900728311513>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-1.47261500964,-3.71905969747>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,2.22418545483,-3.32460509873>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.99957770381,-0.0581222093131>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,2.31985273586,3.25857074251>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-1.36392459011,3.76028053641>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.86944768954,1.0135948786>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-3.03226905339,-2.60870550041>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,0.424397385873,-3.97742213737>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.51443944043,-1.91016109781>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0,3.56846091538,1.80723177689>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,0.539794251807,3.96341042105>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-2.9551847455,2.69571569717>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.8972667998,-0.900728311513>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-1.47261500964,-3.71905969747>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,2.22418545483,-3.32460509873>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.99957770381,-0.0581222093131>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,2.31985273586,3.25857074251>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-1.36392459011,3.76028053641>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.86944768954,1.0135948786>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-3.03226905339,-2.60870550041>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,0.424397385873,-3.97742213737>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.51443944043,-1.91016109781>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.56846091538,1.80723177689>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,0.539794251807,3.96341042105>}
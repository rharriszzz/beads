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


camera {orthographic location <31.866547043,-0,73.3793102963> direction <-0.398331838038,0,-0.917241378703> right <19.4311888106,-23.983788174,-8.4384125421> up <-15.3992460519,-14.8290651547,6.68745449853> }
background {color rgb <0.46,0.38,0.31>}
light_source {<8.55835341906,-25.943131994,80> color rgb 0.9139196134336228 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.46,0.38,0.31>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.93276334064,0.730323562875>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,2.83510872018,-2.82172970795>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-0.71171270647,-3.93617390666>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-3.64370651688,-1.6502735588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.42800973287,2.06124944422>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,3.14289071468,2.47431565399>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.8216872802,-1.18097685514>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,1.19904091914,-3.8160582902>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-2.4594215281,-3.15455951713>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.99326225407,0.232070183905>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-2.07744149388,3.41822129762>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,1.63301970193,3.6514718475>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.93276334064,0.730323562875>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,2.83510872018,-2.82172970795>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-0.71171270647,-3.93617390666>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-3.64370651688,-1.6502735588>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.42800973287,2.06124944422>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-0.250956444518,3.99211984577>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,3.14289071468,2.47431565399>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.8216872802,-1.18097685514>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,1.19904091914,-3.8160582902>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-2.4594215281,-3.15455951713>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.99326225407,0.232070183905>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-2.07744149388,3.41822129762>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,1.63301970193,3.6514718475>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.93276334064,0.730323562875>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,2.83510872018,-2.82172970795>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-0.71171270647,-3.93617390666>}
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


camera {orthographic location <0,-0,80> direction <-0,0,-1> right <29.4463479923,19.9276220554,0> up <13.9493354388,-20.6124435946,-0> }
background {color rgb <0.47,0.31,0.43>}
light_source {<56,-32,80> color rgb 0.55 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-2.23709044722,3.31593521212>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.99977339824,0.0425765518449>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-2.30717007768,-3.26756273584>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,1.37852942654,-3.75495094777>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,3.87335801679,-0.998547782427>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,3.02210685507,2.62047136152>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-0.439853286352,3.97574258303>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-3.52183714649,1.89648704547>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-3.56140976694,-1.8210877167>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-0.524385528042,-3.96547851059>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,2.96563990259,-2.68420937487>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,3.89373648836,0.91586907317>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,1.45814896161,3.72475524105>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-2.23709044722,3.31593521212>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.99977339824,0.0425765518449>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-2.30717007768,-3.26756273584>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,1.37852942654,-3.75495094777>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,3.87335801679,-0.998547782427>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,3.02210685507,2.62047136152>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-0.439853286352,3.97574258303>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-3.52183714649,1.89648704547>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-3.56140976694,-1.8210877167>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-0.524385528042,-3.96547851059>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,2.96563990259,-2.68420937487>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,3.89373648836,0.91586907317>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,1.45814896161,3.72475524105>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-2.23709044722,3.31593521212>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.99977339824,0.0425765518449>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-2.30717007768,-3.26756273584>}

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


camera {orthographic location <0,-0,80> direction <-0,0,-1> right <34.1462351901,-9.91121350815,-0> up <-6.93784945571,-23.9023646331,-0> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-48,-64,80> color rgb 0.55 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-1.5979821017,-3.66694057801>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.92559023078,-0.767946183034>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-2.86199673873,2.79445427007>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,0.673991325715,3.94280809739>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,3.62773816221,1.68508629644>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,3.44758899493,-2.02833185698>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,0.289169376267,-3.98953394168>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-3.11905513795,-2.50429531933>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-3.83281991022,1.14433016905>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-1.23552460519,3.80440257465>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,2.42910396637,3.17796380101>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,3.99530126407,-0.193824171159>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,2.110075635,-3.39817315841>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-1.5979821017,-3.66694057801>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.92559023078,-0.767946183034>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-2.86199673873,2.79445427007>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,0.673991325715,3.94280809739>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,3.62773816221,1.68508629644>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,3.44758899493,-2.02833185698>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,0.289169376267,-3.98953394168>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-3.11905513795,-2.50429531933>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-3.83281991022,1.14433016905>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-1.23552460519,3.80440257465>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,2.42910396637,3.17796380101>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,3.99530126407,-0.193824171159>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,2.110075635,-3.39817315841>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-1.5979821017,-3.66694057801>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.92559023078,-0.767946183034>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-2.86199673873,2.79445427007>}

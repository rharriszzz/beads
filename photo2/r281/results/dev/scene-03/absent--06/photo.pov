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


camera {orthographic location <36.3737631427,-0,71.2527147191> direction <-0.454672039284,0,-0.890658933988> right <20.0385867672,-22.7554962655,-10.229488261> up <-14.1871702323,-15.7490260321,7.24240152436> }
background {color rgb <0.46,0.38,0.31>}
light_source {<-39.0836037485,21.666886432,80> color rgb 1.0827989904493251 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.46,0.38,0.31>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-3.66553812834,-1.6011964994>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.40002187364,2.10709545554>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-0.197327000722,3.99512979198>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,3.17583284826,2.43188933134>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,3.80548436594,-1.23218859781>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,1.14769017679,-3.83181513882>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-2.50155970673,-3.1212495949>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-3.98978593927,0.285671417599>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,1.68190500784,3.62921417728>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,3.94221565608,0.67744794703>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,2.79696246862,-2.85954558438>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-0.764504103375,-3.92626202334>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-3.66553812834,-1.6011964994>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.40002187364,2.10709545554>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-0.197327000722,3.99512979198>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,3.17583284826,2.43188933134>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,3.80548436594,-1.23218859781>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,1.14769017679,-3.83181513882>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-2.50155970673,-3.1212495949>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-3.98978593927,0.285671417599>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-2.03135377147,3.44580931787>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,1.68190500784,3.62921417728>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,3.94221565608,0.67744794703>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,2.79696246862,-2.85954558438>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-0.764504103375,-3.92626202334>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-3.66553812834,-1.6011964994>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.40002187364,2.10709545554>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-0.197327000722,3.99512979198>}
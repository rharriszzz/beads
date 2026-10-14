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


camera {orthographic location <-7.74007554778,0,79.6246898299> direction <0.0967509443472,-0,-0.995308622874> right <30.875001724,7.85663242638,3.00126564251> up <5.47384180051,-21.7143715126,0.532095624649> }
background {color rgb <0.46,0.38,0.31>}
light_source {<53.1821473085,6.89251452921,80> color rgb 0.996107099507844 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.46,0.38,0.31>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-3.72589751951,1.45522770524>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-0.918922108155,3.89301710234>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,2.68188301024,2.96774384329>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,3.96588849411,-0.521275792944>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,1.8238798757,-3.55998064588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-1.8937247748,-3.52332321499>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-3.97539644484,-0.442970773677>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-2.62284037439,3.02005105428>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,0.99551013885,3.8741398482>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,3.75386880418,1.38147348906>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,3.26937092417,-2.30460707284>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-0.0394400721652,-3.99980555536>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-3.31417995338,-2.23968998672>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-3.72589751951,1.45522770524>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-0.918922108155,3.89301710234>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,2.68188301024,2.96774384329>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,3.96588849411,-0.521275792944>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,1.8238798757,-3.55998064588>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-1.8937247748,-3.52332321499>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-3.97539644484,-0.442970773677>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-2.62284037439,3.02005105428>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,0.99551013885,3.8741398482>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,3.75386880418,1.38147348906>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,3.26937092417,-2.30460707284>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-0.0394400721652,-3.99980555536>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-3.31417995338,-2.23968998672>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-3.72589751951,1.45522770524>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-0.918922108155,3.89301710234>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,2.68188301024,2.96774384329>}
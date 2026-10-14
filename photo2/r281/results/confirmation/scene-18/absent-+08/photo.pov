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


camera {orthographic location <-30.0755420066,0,74.1313818366> direction <0.375944275083,-0,-0.926642272958> right <33.6210225976,-16.839550397,13.6402486017> up <-10.9229674788,-25.3978439201,-4.43151279671> }
background {color rgb <0.23,0.29,0.34>}
light_source {<53.1402739354,18.8275193641,80> color rgb 0.9277750295091648 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.23,0.29,0.34>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,2.87221764428,-2.78394788095>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.92274977817,0.782326132672>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,1.58453407417,3.67277167379>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-2.12251388311,3.39041808867>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.99598469705,0.17918231192>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-2.41744218664,-3.18684377939>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,1.24945733008,-3.79984952075>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.83698751016,-1.13027733184>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,3.10985734626,2.51570810825>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-0.30378685861,3.98844751057>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.45499855606,2.01568474163>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-3.62153890079,-1.69836862607>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-0.659538600858,-3.94525142849>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,2.87221764428,-2.78394788095>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,3.92274977817,0.782326132672>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,1.58453407417,3.67277167379>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-2.12251388311,3.39041808867>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.99598469705,0.17918231192>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-2.41744218664,-3.18684377939>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,1.24945733008,-3.79984952075>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.83698751016,-1.13027733184>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,3.10985734626,2.51570810825>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.45499855606,2.01568474163>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-3.62153890079,-1.69836862607>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-0.659538600858,-3.94525142849>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,2.87221764428,-2.78394788095>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.92274977817,0.782326132672>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,1.58453407417,3.67277167379>}
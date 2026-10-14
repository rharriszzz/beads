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


camera {orthographic location <-6.8008440303,0,79.7104040918> direction <0.0850105503787,-0,-0.996380051147> right <39.2384709199,7.0096088132,3.34780288413> up <4.88896407147,-27.5667197595,0.417123492205> }
background {color rgb <0.47,0.31,0.43>}
light_source {<38.1807393856,6.76498289188,80> color rgb 0.9156741290755392 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,0.544526652682,-3.96276301645>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,3.57061642194,-1.80296931959>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,3.51215597413,1.91435639666>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,0.419647565903,3.97792608283>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-3.03538199764,2.60508274886>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-3.86823457735,-1.01821473894>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-1.35943339332,-3.76190654445>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,2.32374220481,-3.25579823785>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,3.9995054474,0.0628981416589>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,2.22021389325,3.32725867167>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-1.47705496149,3.71729856761>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-3.89833959846,0.896073866991>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-2.95196363185,-2.699242619>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,0.544526652682,-3.96276301645>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,3.57061642194,-1.80296931959>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,3.51215597413,1.91435639666>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,0.419647565903,3.97792608283>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-3.03538199764,2.60508274886>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-3.86823457735,-1.01821473894>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-1.35943339332,-3.76190654445>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,2.32374220481,-3.25579823785>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,3.9995054474,0.0628981416589>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,2.22021389325,3.32725867167>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-1.47705496149,3.71729856761>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-3.89833959846,0.896073866991>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-2.95196363185,-2.699242619>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,0.544526652682,-3.96276301645>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,3.57061642194,-1.80296931959>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,3.51215597413,1.91435639666>}
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


camera {orthographic location <18.268394058,-0,77.8862361303> direction <-0.228354925725,0,-0.973577951629> right <32.3508348644,-22.2676068852,-7.58796199138> up <-15.1754757692,-23.2601656264,3.55944240143> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-61.1394254396,47.5376427195,80> color rgb 1.2234015301051682 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-1.1124885323,-3.84218287767>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,2.53008900179,-3.09816875638>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,3.98699726833,0.322261977829>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,1.99965618511,3.46430009401>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-1.71512889964,3.61363153318>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-3.94826471308,0.641253269342>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-2.77061108888,-2.8850847811>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,0.800491740086,-3.91908318029>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,3.68007336407,-1.56750120736>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,3.38054814694,2.13819882757>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-3.19800952766,2.40265167284>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-3.79402003448,-1.26704853022>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-1.1124885323,-3.84218287767>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,2.53008900179,-3.09816875638>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,3.98699726833,0.322261977829>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,1.99965618511,3.46430009401>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-1.71512889964,3.61363153318>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-3.94826471308,0.641253269342>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-2.77061108888,-2.8850847811>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,0.800491740086,-3.91908318029>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,3.68007336407,-1.56750120736>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,3.38054814694,2.13819882757>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,0.160667089736,3.99677195825>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-3.19800952766,2.40265167284>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-3.79402003448,-1.26704853022>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-1.1124885323,-3.84218287767>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,2.53008900179,-3.09816875638>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,3.98699726833,0.322261977829>}
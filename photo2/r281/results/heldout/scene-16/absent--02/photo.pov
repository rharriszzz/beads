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


camera {orthographic location <-26.9863643632,0,75.310929741> direction <0.33732955454,-0,-0.941386621763> right <32.2090792243,20.7211849583,11.5415644282> up <13.6546524148,-23.9501549478,4.89290766407> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-41.696401824,41.8414777753,80> color rgb 1.2851716717504913 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.93531886366,0.716425461123>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-2.82512250921,-2.83172788381>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,0.7256138583,-3.93363502738>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,3.64951381449,-1.63739088731>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.42070642314,2.07334694798>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,0.236851641315,3.99298150509>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-3.15161228787,2.4631971068>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-3.81749131352,-1.19447062384>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-1.18555218446,-3.82027041162>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,2.47055051072,-3.14585126381>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.99241748477,0.246176008767>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,2.06535274395,3.42553908795>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.93531886366,0.716425461123>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.82512250921,-2.83172788381>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,0.7256138583,-3.93363502738>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,3.64951381449,-1.63739088731>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.42070642314,2.07334694798>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,0.236851641315,3.99298150509>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-3.15161228787,2.4631971068>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-3.81749131352,-1.19447062384>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-1.18555218446,-3.82027041162>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,2.47055051072,-3.14585126381>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.99241748477,0.246176008767>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,2.06535274395,3.42553908795>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-1.64590931797,3.64567998006>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.93531886366,0.716425461123>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-2.82512250921,-2.83172788381>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,0.7256138583,-3.93363502738>}
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


camera {orthographic location <-35.9319259832,0,71.476546469> direction <0.449149074789,-0,-0.893456830863> right <25.4267839958,15.9910467216,12.7822812609> up <10.0011169482,-19.921218555,5.02765468795> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-43.7797590797,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-1.34202484029,3.76815197783>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-3.863485283,1.03608950774>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-3.04739473728,-2.59102013022>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,0.401250243755,-3.97982389584>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.50326697347,-1.93057517663>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,3.57891468827,1.78644049833>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,0.562843558465,3.96020291509>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-2.9394515213,2.7128628336>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-3.90244112641,-0.878039438115>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-1.49422693892,-3.71042933567>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,2.20480583118,-3.33748876355>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,3.99917187108,-0.0813900826951>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,2.33877128098,3.24501909012>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-1.34202484029,3.76815197783>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.863485283,1.03608950774>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-3.04739473728,-2.59102013022>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,0.401250243755,-3.97982389584>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.50326697347,-1.93057517663>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,3.57891468827,1.78644049833>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,0.562843558465,3.96020291509>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-2.9394515213,2.7128628336>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-3.90244112641,-0.878039438115>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-1.49422693892,-3.71042933567>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,2.20480583118,-3.33748876355>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,3.99917187108,-0.0813900826951>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,2.33877128098,3.24501909012>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-1.34202484029,3.76815197783>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-3.863485283,1.03608950774>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-3.04739473728,-2.59102013022>}
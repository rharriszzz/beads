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


camera {orthographic location <24.72135955,-0,76.0845213036> direction <-0.309016994375,0,-0.951056516295> right <29.0524741608,-9.53128590924,-9.43972107914> up <-6.34535410086,-21.3833053705,2.06173052694> }
background {color rgb <0.23,0.29,0.34>}
light_source {<-16,72,48> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.23,0.29,0.34>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,1.97878315497,-3.47626483825>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-1.73683292369,-3.60325011555>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-3.95205026478,-0.61749389035>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-2.75320794178,2.90169709469>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,0.824049520494,3.91419754072>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,3.68943490609,1.54533817456>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,3.36762629052,-2.15849326323>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,0.136624645533,-3.99766603235>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-3.2124030012,-2.38337302114>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-3.78633044008,1.28984564911>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-1.08935868377,3.84880470511>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,2.54867791049,3.08289489094>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,3.98498682721,-0.346236894268>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,1.97878315497,-3.47626483825>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-1.73683292369,-3.60325011555>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-3.95205026478,-0.61749389035>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-2.75320794178,2.90169709469>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,0.824049520494,3.91419754072>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,3.68943490609,1.54533817456>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,3.36762629052,-2.15849326323>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,0.136624645533,-3.99766603235>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-3.2124030012,-2.38337302114>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-3.78633044008,1.28984564911>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,2.54867791049,3.08289489094>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,3.98498682721,-0.346236894268>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,1.97878315497,-3.47626483825>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-1.73683292369,-3.60325011555>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-3.95205026478,-0.61749389035>}
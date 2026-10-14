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


camera {orthographic location <24.72135955,-0,76.0845213036> direction <-0.309016994375,0,-0.951056516295> right <30.393419032,1.64807460381,-9.87542047936> up <1.09718846391,-22.3702723843,-0.356498142403> }
background {color rgb <0.23,0.29,0.34>}
light_source {<-16,72,48> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.23,0.29,0.34>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,1.62689912035,-3.65420295717>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-2.08316603969,-3.41473560486>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-3.99364549783,-0.225378875884>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-2.45413239682,3.15867601676>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,1.20543330094,3.81404385882>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,3.82366072242,1.1745717006>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,3.1387404188,-2.47957830758>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-0.257645160301,-3.99169374719>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-3.43145868426,-2.05550268747>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-3.64093625649,1.65637652006>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-0.705116380549,3.93736090419>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,2.83983274022,2.8169753296>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,3.93153411321,-0.736912149881>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,1.62689912035,-3.65420295717>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.08316603969,-3.41473560486>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-3.99364549783,-0.225378875884>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-2.45413239682,3.15867601676>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,1.20543330094,3.81404385882>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,3.82366072242,1.1745717006>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,3.1387404188,-2.47957830758>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-0.257645160301,-3.99169374719>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-3.43145868426,-2.05550268747>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-3.64093625649,1.65637652006>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-0.705116380549,3.93736090419>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,2.83983274022,2.8169753296>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,3.93153411321,-0.736912149881>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,1.62689912035,-3.65420295717>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-2.08316603969,-3.41473560486>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-3.99364549783,-0.225378875884>}
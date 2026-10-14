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


camera {orthographic location <24.72135955,-0,76.0845213036> direction <-0.309016994375,0,-0.951056516295> right <37.0415513434,9.11424714761,-12.0355296105> up <6.0677148986,-27.2634543754,-1.97152008168> }
background {color rgb <0.23,0.29,0.34>}
light_source {<-16,72,48> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.23,0.29,0.34>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.13290648728,2.48694530337>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-3.82640959026,-1.1655855385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-1.21439030228,-3.81120141081>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,2.44670495127,-3.16443278985>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.99416395921,0.215995988182>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,2.09118252452,3.40983220249>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-1.61830981689,3.65801494482>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-3.92979203705,0.74614646385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-2.84644281958,-2.8102959408>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,0.695864398277,-3.93900656755>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.63703488591,-1.66492559554>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,3.43627820436,2.04743549404>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,0.267022129801,3.99107744628>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.13290648728,2.48694530337>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.82640959026,-1.1655855385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-1.21439030228,-3.81120141081>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,2.44670495127,-3.16443278985>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.99416395921,0.215995988182>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,2.09118252452,3.40983220249>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-1.61830981689,3.65801494482>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-3.92979203705,0.74614646385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-2.84644281958,-2.8102959408>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,0.695864398277,-3.93900656755>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.63703488591,-1.66492559554>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,3.43627820436,2.04743549404>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,0.267022129801,3.99107744628>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.13290648728,2.48694530337>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-3.82640959026,-1.1655855385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-1.21439030228,-3.81120141081>}
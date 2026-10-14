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


camera {orthographic location <24.72135955,-0,76.0845213036> direction <-0.309016994375,0,-0.951056516295> right <37.5348692114,6.51119107545,-12.1958183023> up <4.3347574908,-27.6265479473,-1.40844808715> }
background {color rgb <0.23,0.29,0.34>}
light_source {<-16,72,48> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.23,0.29,0.34>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,3.95981134559,0.565591820402>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,1.78395628627,3.58015362362>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-1.93300599372,3.50192630251>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-3.98010140677,0.398488132602>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-2.58890460148,-3.04919218227>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,1.03877053327,-3.86276530211>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,3.76908244127,-1.33940940378>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,3.24339519155,2.34102277465>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-0.0841655051946,3.99911442294>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-3.33901810433,2.20248906897>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-3.70939144234,-1.49680163265>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-0.875330916109,-3.90304954969>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,2.71490217201,-2.9375680752>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,3.95981134559,0.565591820402>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,1.78395628627,3.58015362362>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-1.93300599372,3.50192630251>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-3.98010140677,0.398488132602>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-2.58890460148,-3.04919218227>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,1.03877053327,-3.86276530211>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,3.76908244127,-1.33940940378>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,3.24339519155,2.34102277465>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-0.0841655051946,3.99911442294>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-3.33901810433,2.20248906897>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-3.70939144234,-1.49680163265>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-0.875330916109,-3.90304954969>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,2.71490217201,-2.9375680752>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,3.95981134559,0.565591820402>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,1.78395628627,3.58015362362>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-1.93300599372,3.50192630251>}
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


camera {orthographic location <18.3024832435,-0,77.8782325629> direction <-0.228781040543,0,-0.973477907036> right <27.9143816427,-14.2038765703,-6.56027346094> up <-9.67901202482,-20.0724300045,2.27470436305> }
background {color rgb <0.65,0.63,0.52>}
light_source {<-2.17902196645,4.08002922307,80> color rgb 0.9336966641030404 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,3.06928029533,2.56505720574>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,3.85455062903,-1.06884959103>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,1.30998835836,-3.77940875018>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-2.36623421901,-3.22504815791>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-3.99833684301,0.115336420151>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-2.17639419314,3.35608526651>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,1.52567121079,3.6976110337>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,3.90975425304,0.844879684234>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,2.91631590828,-2.73771830602>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-0.59644173739,-3.95528219649>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-3.59395095726,-1.75599445238>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-3.48675194321,1.96024510878>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-0.367450761809,3.98308673489>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,3.06928029533,2.56505720574>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,3.85455062903,-1.06884959103>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,1.30998835836,-3.77940875018>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-2.36623421901,-3.22504815791>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-3.99833684301,0.115336420151>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-2.17639419314,3.35608526651>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,1.52567121079,3.6976110337>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,3.90975425304,0.844879684234>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,2.91631590828,-2.73771830602>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-0.59644173739,-3.95528219649>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-3.59395095726,-1.75599445238>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-3.48675194321,1.96024510878>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-0.367450761809,3.98308673489>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,3.06928029533,2.56505720574>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,3.85455062903,-1.06884959103>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,1.30998835836,-3.77940875018>}
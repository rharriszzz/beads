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


camera {orthographic location <40.1324828253,-0,69.2053742297> direction <-0.501656035317,0,-0.865067177871> right <31.7268918031,-9.48458437601,-18.3985558139> up <-5.74336184761,-25.672947524,3.33059929629> }
background {color rgb <0.47,0.31,0.43>}
light_source {<2.77724208165,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,2.96328679416,2.68680691073>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-0.52785997609,3.96501750887>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-3.56300408141,1.81796642319>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-3.52017404613,-1.89957223736>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-0.436369474516,-3.97612646702>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,3.02440181609,-2.61782231155>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,3.87248157785,1.00194133022>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,1.3752387174,3.75615740753>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-2.31003231046,3.26553988257>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-3.99973455617,-0.0460812348721>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-2.23418408482,-3.3178941326>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,1.46141212358,-3.72347614536>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,3.89453750052,-0.912456934347>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,2.96328679416,2.68680691073>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-0.52785997609,3.96501750887>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-3.56300408141,1.81796642319>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-3.52017404613,-1.89957223736>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-0.436369474516,-3.97612646702>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,3.02440181609,-2.61782231155>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,3.87248157785,1.00194133022>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,1.3752387174,3.75615740753>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-2.31003231046,3.26553988257>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-3.99973455617,-0.0460812348721>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-2.23418408482,-3.3178941326>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,1.46141212358,-3.72347614536>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,3.89453750052,-0.912456934347>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,2.96328679416,2.68680691073>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-0.52785997609,3.96501750887>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-3.56300408141,1.81796642319>}
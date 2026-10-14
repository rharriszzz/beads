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


camera {orthographic location <-7.52143468595,0,79.6456403092> direction <0.0940179335744,-0,-0.995570503865> right <30.3887432624,-9.60669240106,2.86979860729> up <-6.69489771594,-21.3667642835,-0.632240957623> }
background {color rgb <0.65,0.63,0.52>}
light_source {<-53.2566483605,-8.15435014612,80> color rgb 0.9651545776749176 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,3.95880333735,0.572604694513>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,2.72010104031,-2.93275473412>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-0.868416320258,-3.90459384504>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-3.70673443436,-1.50336949322>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,-3.34291399505,2.19657142422>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-0.0912487495249,3.99895907277>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,3.23924359947,2.3467639215>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,3.77144893939,-1.33273136736>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,1.04561077366,-3.86091933482>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-2.58349970076,-3.05377296081>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,-3.98080098004,0.391437807705>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-1.93920570027,3.498496999>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,1.77761219007,3.58330781565>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,3.95880333735,0.572604694513>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,2.72010104031,-2.93275473412>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-0.868416320258,-3.90459384504>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-3.70673443436,-1.50336949322>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,-3.34291399505,2.19657142422>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-0.0912487495249,3.99895907277>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,3.23924359947,2.3467639215>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,3.77144893939,-1.33273136736>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,1.04561077366,-3.86091933482>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-2.58349970076,-3.05377296081>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,-3.98080098004,0.391437807705>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-1.93920570027,3.498496999>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,1.77761219007,3.58330781565>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,3.95880333735,0.572604694513>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,2.72010104031,-2.93275473412>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-0.868416320258,-3.90459384504>}
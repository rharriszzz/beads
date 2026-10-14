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


camera {orthographic location <-21.1514030927,0,77.1532121639> direction <0.264392538659,-0,-0.964415152049> right <27.9191780717,-27.6031874549,7.65398838039> up <-18.6346525585,-20.2645350487,-5.1086537644> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-3.15607328406,17.5544597276,80> color rgb 0.974274512191 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.36942828777,-2.15567924644>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-0.139964187057,-3.99755050329>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,3.21041084683,-2.38605578195>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,3.78740663627,1.28668215637>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,1.09257353637,3.84789332851>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,-2.54610161782,3.08502294185>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-3.98527467773,-0.342907776271>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-1.9816864831,-3.47461058001>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,1.73382221749,-3.60469978197>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,3.95153304081,-0.620795157367>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,2.75563101456,2.89939609429>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,-0.820779372061,3.91488457332>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-3.68814266679,1.54841973296>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.36942828777,-2.15567924644>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,-0.139964187057,-3.99755050329>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,3.21041084683,-2.38605578195>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,3.78740663627,1.28668215637>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,1.09257353637,3.84789332851>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,-2.54610161782,3.08502294185>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-3.98527467773,-0.342907776271>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-1.9816864831,-3.47461058001>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,1.73382221749,-3.60469978197>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,3.95153304081,-0.620795157367>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,2.75563101456,2.89939609429>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,-0.820779372061,3.91488457332>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-3.68814266679,1.54841973296>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.36942828777,-2.15567924644>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-0.139964187057,-3.99755050329>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,3.21041084683,-2.38605578195>}
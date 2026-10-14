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


camera {orthographic location <-9.47231710049,0,79.4372406919> direction <0.118403963756,-0,-0.992965508649> right <23.4118423106,-21.6354359658,2.79169306916> up <-15.0382691751,-16.5043896033,-1.79320496316> }
background {color rgb <0.65,0.63,0.52>}
light_source {<21.900624935,-27.1422130012,80> color rgb 1.1156877806249583 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.65,0.63,0.52>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,0.905932111479,-3.89606044735>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-2.69176679325,-2.95878210261>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-3.96412775481,0.534500835839>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,-1.81199566485,3.56604426649>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,1.90546603796,3.51698723031>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,3.97685182936,0.429708653998>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,2.61275261651,-3.02878255491>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-1.00842652262,-3.87079784392>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-3.75845573085,-1.36894503879>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,-3.26166588307,2.31549901041>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,0.0527809232774,3.99965175661>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,3.3216318467,2.22862331385>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,3.72102298418,-1.46764707993>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,0.905932111479,-3.89606044735>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.69176679325,-2.95878210261>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-3.96412775481,0.534500835839>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,-1.81199566485,3.56604426649>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,1.90546603796,3.51698723031>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,3.97685182936,0.429708653998>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,2.61275261651,-3.02878255491>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-1.00842652262,-3.87079784392>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-3.75845573085,-1.36894503879>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,-3.26166588307,2.31549901041>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,0.0527809232774,3.99965175661>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,3.3216318467,2.22862331385>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,3.72102298418,-1.46764707993>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,0.905932111479,-3.89606044735>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-2.69176679325,-2.95878210261>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-3.96412775481,0.534500835839>}
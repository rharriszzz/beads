#version 3.7;
global_settings { assumed_gamma 1.0 }
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


camera { orthographic location <0,-0,80> look_at <0,0,0> right <23.12803974,-13.27421896,-0> up <-9.291953272,-16.18962782,-0> }
background { color rgb <.47,.31,.43> }
light_source { <48,32,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.771192595,-0.4962964635,-3.969091813> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.358964553,-3.548427049,-1.846257153> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651,-3.535176163,1.871504609> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.534508468,-0.4679908536,3.972528736> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,3.003477951,2.641802452> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.710052383,3.880330737,-0.9710990543> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.29782434,1.405080243,-3.745096729> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.885596298,-2.283977632,-3.283815795> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.473368255,-3.999974593,0.01425675273> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.061140213,-2.260511477,3.300013313> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.64891217,1.431740834,3.734985701> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.236684128,3.887154465,0.9434140995> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.8244560851,2.98457,-2.663145118> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.4122280425,-0.4962964635,-3.969091813> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.548427049,-1.846257153> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.4122280425,-3.535176163,1.871504609> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.8244560851,-0.4679908536,3.972528736> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.236684128,3.003477951,2.641802452> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.64891217,3.880330737,-0.9710990543> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.061140213,1.405080243,-3.745096729> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.473368255,-2.283977632,-3.283815795> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.885596298,-3.999974593,0.01425675273> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.29782434,-2.260511477,3.300013313> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.710052383,1.431740834,3.734985701> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,3.887154465,0.9434140995> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.534508468,2.98457,-2.663145118> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651,-0.4962964635,-3.969091813> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.358964553,-3.548427049,-1.846257153> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.771192595,-3.535176163,1.871504609> }
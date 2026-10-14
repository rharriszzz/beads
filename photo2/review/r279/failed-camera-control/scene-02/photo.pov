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


camera { orthographic location <-40,0,69.2820323> look_at <0,0,0> right <23.08300762,0.8230774287,13.32698067> up <0.4989641738,-18.65777293,0.2880771> }
background { color rgb <.47,.31,.43> }
light_source { <48,32,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.771192595,3.903350378,0.8739884586> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.358964553,1.498077344,3.708876416> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651,-2.201340525,3.339775426> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.534508468,-3.999085239,0.08554094629> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,-2.342138162,-3.242589834> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.710052383,1.338112995,-3.769542892> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.29782434,3.862407801,-1.040099022> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.885596298,3.050082424,2.587855716> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.473368255,-0.3971192023,3.980238226> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.061140213,-3.501261262,1.934210324> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.64891217,-3.580766982,-1.782724831> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.236684128,-0.5669537152,-3.959616583> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.8244560851,2.936634144,-2.715912352> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.4122280425,3.903350378,0.8739884586> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,1.498077344,3.708876416> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.4122280425,-2.201340525,3.339775426> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.8244560851,-3.999085239,0.08554094629> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.236684128,-2.342138162,-3.242589834> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.64891217,1.338112995,-3.769542892> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.061140213,3.862407801,-1.040099022> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.473368255,3.050082424,2.587855716> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.885596298,-0.3971192023,3.980238226> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.29782434,-3.501261262,1.934210324> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.710052383,-3.580766982,-1.782724831> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,-0.5669537152,-3.959616583> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.534508468,2.936634144,-2.715912352> }
object { bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651,3.903350378,0.8739884586> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.358964553,1.498077344,3.708876416> }
object { bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .10 diffuse .75 specular 1.4 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.771192595,-2.201340525,3.339775426> }
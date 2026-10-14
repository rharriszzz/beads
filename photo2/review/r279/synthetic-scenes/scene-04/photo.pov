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


camera { orthographic location <0,-0,80> direction <-0,0,-1> right <26.58550124,-2.078998499,-0> up <-1.455298949,-18.60985087,-0> }
background { color rgb <.47,.31,.43> }
light_source { <-40,-56,80> color rgb 1.1 parallel point_at <0,0,0> }
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-5.246538723,-3.530875789,1.879605321> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.871785957,-3.552650914,-1.838116286> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.497033191,-0.5053956951,-3.967943446> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,2.978455959,-2.669981292> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.747527659,3.889307356,0.9344989536> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-3.372774893,1.440300836,3.731693114> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.998022127,-2.252939096,3.305187654> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.623269362,-3.99993139,0.02342806105> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-2.248516596,-2.291500928,-3.278570343> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376383,1.396489601,-3.748308524> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.499011064,3.878093952,-0.9799935219> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-1.124258298,3.009527316,2.634908981> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.7495055319,-0.4588812069,3.973591327> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <-0.3747527659,-3.530875789,1.879605321> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.552650914,-1.838116286> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.3747527659,-0.5053956951,-3.967943446> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <0.7495055319,2.978455959,-2.669981292> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.124258298,3.889307356,0.9344989536> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.499011064,1.440300836,3.731693114> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <1.87376383,-2.252939096,3.305187654> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.248516596,-3.99993139,0.02342806105> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.623269362,-2.291500928,-3.278570343> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <2.998022127,1.396489601,-3.748308524> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.372774893,3.878093952,-0.9799935219> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <3.747527659,3.009527316,2.634908981> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,-0.4588812069,3.973591327> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.497033191,-3.530875789,1.879605321> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <4.871785957,-3.552650914,-1.838116286> }
object { bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .10 diffuse .75 specular 0.5 roughness .025}}},.8,.7,1) rotate <0,0,-90> translate <5.246538723,-0.5053956951,-3.967943446> }
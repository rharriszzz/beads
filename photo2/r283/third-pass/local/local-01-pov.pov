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


camera {orthographic location <59.1594819068,-2.7188771401,80.7118565029> direction <-0.621175767507,0,-0.783671274108> right <-19.7230423899,-7.82345195462,15.6334376401> up <-4.81722572665,19.774459873,3.81836617836> }
background {color rgb <.47,.31,.43>}
light_source {<949.093853759,-230.410009477,214.783808257> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .12 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-16.788938904,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-16.3692154314,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-15.9494919588,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-15.5297684862,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-15.1100450136,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-14.690321541,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-14.2705980684,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.8508745958,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.4311511232,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.0114276506,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-12.591704178,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-12.1719807054,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-11.7522572328,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-11.3325337602,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-10.9128102876,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-10.493086815,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-10.0733633424,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-9.65363986983,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-9.23391639723,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-8.81419292463,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-8.39446945202,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-7.97474597942,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-7.55502250682,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-7.13529903422,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-6.71557556162,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-6.29585208902,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612861642,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640514382,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-5.03668167121,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695819861,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723472601,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-3.77751125341,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778778081,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806430821,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-2.51834083561,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861736301,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-1.6788938904,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-1.2591704178,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446945202,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723472601,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0.419723472601,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0.839446945202,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <1.2591704178,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <1.6788938904,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <2.09861736301,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <2.51834083561,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <2.93806430821,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <3.35778778081,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <3.77751125341,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <4.19723472601,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <4.61695819861,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <5.03668167121,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <5.45640514382,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <5.87612861642,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <6.29585208902,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <6.71557556162,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <7.13529903422,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <7.55502250682,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <7.97474597942,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <8.39446945202,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <8.81419292463,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <9.23391639723,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <9.65363986983,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <10.0733633424,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <10.493086815,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <10.9128102876,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <11.3325337602,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <11.7522572328,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <12.1719807054,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <12.591704178,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.0114276506,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.4311511232,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.8508745958,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <14.2705980684,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <14.690321541,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <15.1100450136,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <15.5297684862,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <15.9494919588,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <16.3692154314,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <16.788938904,0.908655708809,-3.8954261388>}
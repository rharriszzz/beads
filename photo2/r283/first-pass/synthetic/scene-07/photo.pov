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


camera {orthographic location <-24.2575210108,0,76.2336715265> direction <0.303219012635,-0,-0.952920894081> right <33.8150769836,6.55940507089,10.759942739> up <4.37541590136,-24.8399988242,1.39225543035> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-23.248407335,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.50570801665,1.60031315562,-3.66592386772>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.04101458689,-2.10791470929,-3.39951402091>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.57632115713,-3.99517722655,-0.196364274872>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.11162772737,-2.4311239694,3.17641877677>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.64693429761,1.23310558265,3.80518733074>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.18224086785,3.8320915904,1.14676677784>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.71754743809,3.12064669486,-2.50231177232>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.25285400833,-0.286632841699,-3.98971698421>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.78816057856,-3.44629872011,-2.03052336401>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.3234671488,-3.6288087775,1.68277950319>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.85877371904,-0.676497958142,3.94237878858>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.39408028928,2.86021949499,2.79627331291>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.929386859522,3.92607768417,-0.765450205997>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.464693429761,1.60031315562,-3.66592386772>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.10791470929,-3.39951402091>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.464693429761,-3.99517722655,-0.196364274872>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.929386859522,-2.4311239694,3.17641877677>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.39408028928,1.23310558265,3.80518733074>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.85877371904,3.8320915904,1.14676677784>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.3234671488,3.12064669486,-2.50231177232>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.78816057856,-0.286632841699,-3.98971698421>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.25285400833,-3.44629872011,-2.03052336401>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.71754743809,-3.6288087775,1.68277950319>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.18224086785,-0.676497958142,3.94237878858>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.64693429761,2.86021949499,2.79627331291>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.11162772737,3.92607768417,-0.765450205997>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.57632115713,1.60031315562,-3.66592386772>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.04101458689,-2.10791470929,-3.39951402091>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.50570801665,-3.99517722655,-0.196364274872>}
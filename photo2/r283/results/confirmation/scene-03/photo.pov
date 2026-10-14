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


camera {orthographic location <-28.2492072502,0,74.846391294> direction <0.353115090628,-0,-0.935579891175> right <30.6807203268,-14.2338672391,11.57979713> up <-9.32184397377,-22.9552862683,-3.51833532408> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-56.7268917778,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.50570801665,3.75199825618,1.38654573874>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.04101458689,3.27248271144,-2.30018627579>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.57632115713,-0.0340341308719,-3.99985520712>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.11162772737,-3.31114989131,-2.2441671946>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.64693429761,-3.72786091791,1.45019066908>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.18224086785,-0.924182845063,3.89177158488>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.71754743809,2.67786953029,2.97136581032>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.25285400833,3.96658939807,-0.515915251907>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.78816057856,1.82868967331,-3.55751234414>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.3234671488,-1.88896112583,-3.52587944563>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.85877371904,-3.97479412037,-0.44834328443>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.39408028928,-2.62691970476,3.01650341699>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.929386859522,0.99027316683,3.87548178361>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.464693429761,3.75199825618,1.38654573874>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,3.27248271144,-2.30018627579>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.464693429761,-0.0340341308719,-3.99985520712>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.929386859522,-3.31114989131,-2.2441671946>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.39408028928,-3.72786091791,1.45019066908>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.85877371904,-0.924182845063,3.89177158488>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.3234671488,2.67786953029,2.97136581032>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.78816057856,3.96658939807,-0.515915251907>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.25285400833,1.82868967331,-3.55751234414>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.71754743809,-1.88896112583,-3.52587944563>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.18224086785,-3.97479412037,-0.44834328443>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.64693429761,-2.62691970476,3.01650341699>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.11162772737,0.99027316683,3.87548178361>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.57632115713,3.75199825618,1.38654573874>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.04101458689,3.27248271144,-2.30018627579>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.50570801665,-0.0340341308719,-3.99985520712>}
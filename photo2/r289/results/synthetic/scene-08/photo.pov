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


camera {orthographic location <33.8094609393,-0,72.5046229629> direction <-0.422618261741,0,-0.906307787037> right <29.9404783346,-13.1469586719,-13.9614743362> up <-8.34063371411,-23.1249638743,3.88930137475> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-32,40,80> color rgb 0.55 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.49073365996,-1.95314579979>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.59037021341,1.76330420819>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,0.588391831948,3.95648771666>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-2.92188089943,2.73177817723>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.90802689817,-0.852833959917>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-1.51814372083,-3.70070799212>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,2.18321904162,-3.35164953662>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.9985632647,-0.107199898184>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,2.35966661488,3.22985657059>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-1.3176764288,3.77673520769>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.85671766848,1.06100368786>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-3.06405426232,-2.57129762524>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,0.375555251488,-3.98233075636>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.49073365996,-1.95314579979>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,3.59037021341,1.76330420819>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,0.588391831948,3.95648771666>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-2.92188089943,2.73177817723>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.90802689817,-0.852833959917>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-1.51814372083,-3.70070799212>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,2.18321904162,-3.35164953662>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.9985632647,-0.107199898184>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,2.35966661488,3.22985657059>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-1.3176764288,3.77673520769>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.85671766848,1.06100368786>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-3.06405426232,-2.57129762524>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,0.375555251488,-3.98233075636>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.49073365996,-1.95314579979>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.59037021341,1.76330420819>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,0.588391831948,3.95648771666>}

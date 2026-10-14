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


camera {orthographic location <33.0165540126,-0,72.8691097869> direction <-0.412706925157,0,-0.910863872336> right <28.4447422485,9.34029168406,-12.8881411008> up <5.95541397646,-21.8598192097,-2.6983621427> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-2.31512087765,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.0859849188,-0.630382163483,3.95001497819>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.65127171032,2.89270071305,2.76265860807>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.21655850183,3.91686475934,-0.811277053203>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.78184529334,1.55736486194,-3.68437439558>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.34713208486,-2.14749660761,-3.37464936257>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.91241887637,-3.99719909495,-0.149664275332>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.47770566789,-2.39383917541,3.20461136525>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.0429924594,1.27748780517,3.79051776248>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.60827925092,3.8452307484,1.10190766019>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.17356604243,3.09119225725,-2.53860797066>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.73885283394,-0.333236054967,-3.986095048>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.30413962546,-3.46979156759,-1.99011217711>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.869426416972,-3.60889648114,1.72506990828>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.434713208486,-0.630382163483,3.95001497819>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,2.89270071305,2.76265860807>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.434713208486,3.91686475934,-0.811277053203>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.869426416972,1.55736486194,-3.68437439558>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.30413962546,-2.14749660761,-3.37464936257>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.73885283394,-3.99719909495,-0.149664275332>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.17356604243,-2.39383917541,3.20461136525>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.60827925092,1.27748780517,3.79051776248>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.0429924594,3.8452307484,1.10190766019>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.47770566789,3.09119225725,-2.53860797066>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.91241887637,-0.333236054967,-3.986095048>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.34713208486,-3.46979156759,-1.99011217711>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.78184529334,-3.60889648114,1.72506990828>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.21655850183,-0.630382163483,3.95001497819>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.65127171032,2.89270071305,2.76265860807>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.0859849188,3.91686475934,-0.811277053203>}
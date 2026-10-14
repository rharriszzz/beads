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


camera {orthographic location <-16.4959775222,0,78.2807941042> direction <0.206199719028,-0,-0.978509926303> right <33.8612387018,-0.319334694949,7.13552077355> up <-0.218730518174,-24.2234303957,-0.0460927070621> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-58.8606501466,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.0859849188,2.21136028798,3.33314951311>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.65127171032,3.99932409382,0.073530895293>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.21655850183,2.33238976892,-3.24960889429>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.78184529334,-1.3494272871,-3.76550740231>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.34713208486,-3.86551390908,-1.02849512333>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.91241887637,-3.0422970724,2.59700375881>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.47770566789,0.409070477257,3.97902768835>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.0429924594,3.50705410651,1.92368695322>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.60827925092,3.57539712832,-1.7934702046>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.17356604243,0.555060021812,-3.96130134832>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.73885283394,-2.9447770669,-2.70708108971>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.30413962546,-3.90070809919,0.885706681102>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.869426416972,-1.48693244997,3.71335857267>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.434713208486,2.21136028798,3.33314951311>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,3.99932409382,0.073530895293>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.434713208486,2.33238976892,-3.24960889429>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.869426416972,-1.3494272871,-3.76550740231>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.30413962546,-3.86551390908,-1.02849512333>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.73885283394,-3.0422970724,2.59700375881>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.17356604243,0.409070477257,3.97902768835>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.60827925092,3.50705410651,1.92368695322>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.0429924594,3.57539712832,-1.7934702046>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.47770566789,0.555060021812,-3.96130134832>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.91241887637,-2.9447770669,-2.70708108971>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.34713208486,-3.90070809919,0.885706681102>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.78184529334,-1.48693244997,3.71335857267>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.21655850183,2.21136028798,3.33314951311>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.65127171032,3.99932409382,0.073530895293>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.06 diffuse .75 specular 0.5 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.0859849188,2.33238976892,-3.24960889429>}
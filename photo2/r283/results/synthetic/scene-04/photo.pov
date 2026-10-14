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


camera {orthographic location <5.3690331278,-0,79.8196309392> direction <-0.0671129140976,0,-0.99774538674> right <37.9636900367,-10.6974846121,-2.5536112741> up <-7.47135614504,-26.6346338243,0.502557556084> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-1.73380238035,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.38560365355,2.13018494527>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-3.67634992331,-1.57621421176>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-0.791205922615,-3.92096839926>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,2.77743753923,-2.87851362958>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.94673462718,0.650604167364>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,1.70656407358,3.61768421269>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-2.0078568507,3.45955356471>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-3.98774946032,0.312816626385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-2.5227429237,-3.10415336943>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,1.12158682028,-3.83953682162>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.7970107897,-1.25805765485>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,3.19230912489,2.41022041547>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-0.170134240658,3.99638015461>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.38560365355,2.13018494527>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.67634992331,-1.57621421176>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-0.791205922615,-3.92096839926>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,2.77743753923,-2.87851362958>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.94673462718,0.650604167364>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,1.70656407358,3.61768421269>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-2.0078568507,3.45955356471>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-3.98774946032,0.312816626385>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-2.5227429237,-3.10415336943>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,1.12158682028,-3.83953682162>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.7970107897,-1.25805765485>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,3.19230912489,2.41022041547>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-0.170134240658,3.99638015461>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.38560365355,2.13018494527>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-3.67634992331,-1.57621421176>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-0.791205922615,-3.92096839926>}
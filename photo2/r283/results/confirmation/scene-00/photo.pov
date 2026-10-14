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


camera {orthographic location <-13.1399462569,0,78.9135084277> direction <0.164249328211,-0,-0.986418855346> right <34.2867765734,13.5024935687,5.70911635374> up <9.32337997528,-24.3311889988,1.55244284849> }
background {color rgb <0.47,0.31,0.43>}
light_source {<3.20656480371,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612336988,-3.5967251739,1.75030512295>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640027203,-3.48364565155,-1.9657601518>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.03667717418,-0.361147395601,-3.98366320849>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695407633,3.07333544392,-2.56019711138>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723097848,3.85285443675,1.07494776117>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.77750788064,1.30400611568,3.78147696678>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778478279,-2.37133462907,3.22129974963>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806168494,-3.99814932663,-0.121663313936>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.51833858709,-2.17108074019,-3.35952502887>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861548924,1.53152046502,-3.69519215539>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.67889239139,3.91108631033,-0.838691762877>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.25916929355,2.91198004363,2.74232970766>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446195697,-0.602699898394,3.95433342455>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723097848,-3.5967251739,1.75030512295>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.48364565155,-1.9657601518>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.419723097848,-0.361147395601,-3.98366320849>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.839446195697,3.07333544392,-2.56019711138>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.25916929355,3.85285443675,1.07494776117>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.67889239139,1.30400611568,3.78147696678>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.09861548924,-2.37133462907,3.22129974963>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.51833858709,-3.99814932663,-0.121663313936>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.93806168494,-2.17108074019,-3.35952502887>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.35778478279,1.53152046502,-3.69519215539>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.77750788064,3.91108631033,-0.838691762877>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.19723097848,2.91198004363,2.74232970766>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.61695407633,-0.602699898394,3.95433342455>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.03667717418,-3.5967251739,1.75030512295>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.45640027203,-3.48364565155,-1.9657601518>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.2 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.87612336988,-0.361147395601,-3.98366320849>}
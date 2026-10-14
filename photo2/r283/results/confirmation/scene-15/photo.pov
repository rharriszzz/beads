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


camera {orthographic location <33.064604394,-0,72.8473193485> direction <-0.413307554925,0,-0.910591491857> right <28.645921251,15.5892577596,-13.0020714851> up <9.93681183618,-22.0210105794,-4.5102106054> }
background {color rgb <0.47,0.31,0.43>}
light_source {<11.7197410627,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.50570801665,3.08596874293,2.54495518971>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.04101458689,3.84748711293,-1.0940031608>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.57632115713,1.28527484178,-3.78788444664>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.11162772737,-2.38724845798,-3.20952407685>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.64693429761,-3.99749822311,0.141449482951>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.18224086785,-2.15442717336,3.37022900627>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.71754743809,1.54978996994,3.68756709079>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.25285400833,3.91518926688,0.819324724702>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.78816057856,2.89837202865,-2.75670810633>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.3234671488,-0.622263322102,-3.95130210917>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.85877371904,-3.60534374159,-1.73248275748>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.39408028928,-3.47387403679,1.98297735149>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.929386859522,-0.341427008178,3.98540181137>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.464693429761,3.08596874293,2.54495518971>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,3.84748711293,-1.0940031608>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.464693429761,1.28527484178,-3.78788444664>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.929386859522,-2.38724845798,-3.20952407685>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.39408028928,-3.99749822311,0.141449482951>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.85877371904,-2.15442717336,3.37022900627>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.3234671488,1.54978996994,3.68756709079>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.78816057856,3.91518926688,0.819324724702>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.25285400833,2.89837202865,-2.75670810633>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.71754743809,-0.622263322102,-3.95130210917>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.18224086785,-3.60534374159,-1.73248275748>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.64693429761,-3.47387403679,1.98297735149>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.11162772737,-0.341427008178,3.98540181137>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.57632115713,3.08596874293,2.54495518971>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.04101458689,3.84748711293,-1.0940031608>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.13 diffuse .75 specular 1.8 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.50570801665,1.28527484178,-3.78788444664>}
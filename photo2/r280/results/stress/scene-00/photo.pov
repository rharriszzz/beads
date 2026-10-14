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


camera {orthographic location <-42.3935411387,0,67.8438476925> direction <0.529919264233,-0,-0.848048096156> right <30.1180287883,-18.4042990325,18.8198331297> up <-10.9254115289,-24.8601703693,-6.82695482143> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-48,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.24653872311,-3.18753018936,2.41653704543>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.87178595717,-3.79949452944,-1.25053641321>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-1.12918760578,-3.83730834713>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.1222804253,2.51659118685,-3.10914277547>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.74752765936,3.98836107616,0.304919540533>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.37277489342,2.01470346234,3.4555708586>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.99802212749,-1.69939705201,3.62105642867>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.62326936155,-3.94543857423,0.658418147505>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-2.78313207682,-2.87300815226>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376382968,0.783440137553,-3.92252744425>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.49901106374,3.67322152346,-1.58349096606>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.12425829781,3.38981517127,2.12347665507>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.749505531872,0.178047470006,3.99603542257>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.374752765936,-3.18753018936,2.41653704543>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.79949452944,-1.25053641321>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.374752765936,-1.12918760578,-3.83730834713>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.749505531872,2.51659118685,-3.10914277547>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.12425829781,3.98836107616,0.304919540533>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.49901106374,2.01470346234,3.4555708586>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.87376382968,-1.69939705201,3.62105642867>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-3.94543857423,0.658418147505>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.62326936155,-2.78313207682,-2.87300815226>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.99802212749,0.783440137553,-3.92252744425>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.37277489342,3.67322152346,-1.58349096606>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.74752765936,3.38981517127,2.12347665507>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.1222804253,0.178047470006,3.99603542257>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-3.18753018936,2.41653704543>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.87178595717,-3.79949452944,-1.25053641321>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 1.4 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.24653872311,-1.12918760578,-3.83730834713>}
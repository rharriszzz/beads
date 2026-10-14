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


camera {orthographic location <19.4759912668,-0,77.5930780687> direction <-0.243449890835,0,-0.969913475859> right <18.2528430542,25.8813375681,-4.58149387505> up <17.5718606564,-13.1733298443,-4.41056616393> }
background {color rgb <0.46,0.38,0.31>}
light_source {<-38.107234888,-27.2133058531,80> color rgb 1.0193024521621186 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.46,0.38,0.31>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.28584908726,2.28105146276>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.74384358067,-1.40841586311>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,0.967642023651,-3.88119426389>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-2.64447693849,-3.00112340996>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.97211026825,0.471529444319>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-1.86835468855,3.53684191868>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,1.84941740234,3.54678097321>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.96953234507,0.492760551833>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,2.66048537015,-2.98694117706>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-0.946876449117,-3.88631251833>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.73625963066,-1.42841309582>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-3.29799831251,2.26345027131>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-0.0106935215689,3.99998570605>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.28584908726,2.28105146276>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,3.74384358067,-1.40841586311>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,0.967642023651,-3.88119426389>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-2.64447693849,-3.00112340996>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.97211026825,0.471529444319>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-1.86835468855,3.53684191868>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,1.84941740234,3.54678097321>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.96953234507,0.492760551833>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,2.66048537015,-2.98694117706>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-0.946876449117,-3.88631251833>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.73625963066,-1.42841309582>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-3.29799831251,2.26345027131>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-0.0106935215689,3.99998570605>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.28584908726,2.28105146276>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.74384358067,-1.40841586311>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,0.967642023651,-3.88119426389>}
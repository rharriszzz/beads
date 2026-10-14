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


camera {orthographic location <-36.6398597708,0,71.116247623> direction <0.457998247135,-0,-0.888953095288> right <34.1655501047,-11.0846090568,17.6024608535> up <-6.89758827178,-26.9034274138,-3.55371206274> }
background {color rgb <0.23,0.29,0.34>}
light_source {<-34.3421514228,-42.7498847378,80> color rgb 1.0557244448326613 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.23,0.29,0.34>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.19038117368,-2.41277184305>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.79801537232,1.25502160605>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,1.12465610743,3.83863890461>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-2.52026039866,3.10616926824>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.98799827756,-0.309628387283>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-2.01062206435,-3.45794721104>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,1.70367125004,-3.61904742602>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.94621321869,-0.653759307896>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,2.7797379752,2.87629219469>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-0.788070920969,3.9215997021>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.67508859145,1.57915288842>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-3.38730561886,-2.12747753088>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-0.173329225512,-3.99624285793>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.19038117368,-2.41277184305>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,3.79801537232,1.25502160605>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,1.12465610743,3.83863890461>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-2.52026039866,3.10616926824>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.98799827756,-0.309628387283>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-2.01062206435,-3.45794721104>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,1.70367125004,-3.61904742602>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.94621321869,-0.653759307896>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,2.7797379752,2.87629219469>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-0.788070920969,3.9215997021>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.67508859145,1.57915288842>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-3.38730561886,-2.12747753088>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-0.173329225512,-3.99624285793>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.19038117368,-2.41277184305>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.79801537232,1.25502160605>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 1.2 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,1.12465610743,3.83863890461>}
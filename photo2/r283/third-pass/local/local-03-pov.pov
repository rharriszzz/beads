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


camera {orthographic location <30.0094677247,2.42785793057,95.5127214599> direction <-0.25345274914,0,-0.967347767844> right <21.88784277,11.5779938407,-5.73478753682> up <8.79995796264,-17.7780849034,-2.30565843235> }
background {color rgb <.47,.31,.43>}
light_source {<-609.234625122,82.9551647247,788.639088682> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .12 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-17.9881177748,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-17.5384148305,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-17.0887118861,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-16.6390089417,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-16.1893059973,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-15.739603053,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-15.2899001086,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-14.8401971642,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-14.3904942199,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.9407912755,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.4910883311,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.0413853867,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-12.5916824424,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-12.141979498,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-11.6922765536,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-11.2425736093,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-10.7928706649,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-10.3431677205,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-9.89346477615,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-9.44376183178,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-8.99405888741,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-8.54435594304,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-8.09465299867,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-7.6449500543,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-7.19524710993,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-6.74554416556,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584122119,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-5.84613827682,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643533245,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673238808,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-4.49702944371,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732649933,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762355496,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792061059,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821766622,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851472185,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881177748,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910883311,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-0.899405888741,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-0.449702944371,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0.449702944371,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0.899405888741,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <1.34910883311,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <1.79881177748,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <2.24851472185,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <2.69821766622,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <3.14792061059,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <3.59762355496,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <4.04732649933,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <4.49702944371,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <4.94673238808,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <5.39643533245,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <5.84613827682,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <6.29584122119,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <6.74554416556,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <7.19524710993,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <7.6449500543,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <8.09465299867,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <8.54435594304,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <8.99405888741,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <9.44376183178,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <9.89346477615,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <10.3431677205,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <10.7928706649,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <11.2425736093,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <11.6922765536,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <12.141979498,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <12.5916824424,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.0413853867,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.4910883311,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.9407912755,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <14.3904942199,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <14.8401971642,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <15.2899001086,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <15.739603053,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <16.1893059973,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <16.6390089417,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <17.0887118861,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <17.5384148305,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <17.9881177748,3.78435940101,1.2956171981>}
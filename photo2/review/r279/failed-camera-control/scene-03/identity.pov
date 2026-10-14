#version 3.7;
global_settings { assumed_gamma 1.0 }
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


camera { orthographic location <-40,0,69.2820323> look_at <0,0,0> right <22.14620317,-7.561218458,12.78611636> up <-4.583745088,-17.90056291,-2.64642646> }
background {color rgb 0}
object { bead(material {texture {pigment {color rgb <0.003921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.771192595,0.4049002207,3.97945421> }
object { bead(material {texture {pigment {color rgb <0.007843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.358964553,3.505036151,1.927361299> }
object { bead(material {texture {pigment {color rgb <0.01176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651,3.577274727,-1.789722194> }
object { bead(material {texture {pigment {color rgb <0.01568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.534508468,0.5592111717,-3.960717469> }
object { bead(material {texture {pigment {color rgb <0.01960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,-2.941938421,-2.710165738> }
object { bead(material {texture {pigment {color rgb <0.02352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.710052383,-3.90163418,0.8816182419> }
object { bead(material {texture {pigment {color rgb <0.02745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.29782434,-1.490823243,3.711798224> }
object { bead(material {texture {pigment {color rgb <0.03137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.885596298,2.207865924,3.335465194> }
object { bead(material {texture {pigment {color rgb <0.03529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.473368255,3.999244837,0.07772215756> }
object { bead(material {texture {pigment {color rgb <0.03921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.061140213,2.335794087,-3.247162759> }
object { bead(material {texture {pigment {color rgb <0.0431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.64891217,-1.345480284,-3.766919538> }
object { bead(material {texture {pigment {color rgb <0.04705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.236684128,-3.864433921,-1.032545628> }
object { bead(material {texture {pigment {color rgb <0.05098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.8244560851,-3.045017069,2.593813997> }
object { bead(material {texture {pigment {color rgb <0.05490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.4122280425,0.4049002207,3.97945421> }
object { bead(material {texture {pigment {color rgb <0.05882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,3.505036151,1.927361299> }
object { bead(material {texture {pigment {color rgb <0.06274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.4122280425,3.577274727,-1.789722194> }
object { bead(material {texture {pigment {color rgb <0.06666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.8244560851,0.5592111717,-3.960717469> }
object { bead(material {texture {pigment {color rgb <0.07058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.236684128,-2.941938421,-2.710165738> }
object { bead(material {texture {pigment {color rgb <0.07450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.64891217,-3.90163418,0.8816182419> }
object { bead(material {texture {pigment {color rgb <0.07843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.061140213,-1.490823243,3.711798224> }
object { bead(material {texture {pigment {color rgb <0.08235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.473368255,2.207865924,3.335465194> }
object { bead(material {texture {pigment {color rgb <0.0862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.885596298,3.999244837,0.07772215756> }
object { bead(material {texture {pigment {color rgb <0.09019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.29782434,2.335794087,-3.247162759> }
object { bead(material {texture {pigment {color rgb <0.09411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.710052383,-1.345480284,-3.766919538> }
object { bead(material {texture {pigment {color rgb <0.09803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,-3.864433921,-1.032545628> }
object { bead(material {texture {pigment {color rgb <0.1019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.534508468,-3.045017069,2.593813997> }
object { bead(material {texture {pigment {color rgb <0.1058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651,0.4049002207,3.97945421> }
object { bead(material {texture {pigment {color rgb <0.1098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.358964553,3.505036151,1.927361299> }
object { bead(material {texture {pigment {color rgb <0.1137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.771192595,3.577274727,-1.789722194> }
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


camera { orthographic location <0,-0,80> direction <-0,0,-1> right <25.96566937,6.074135759,0> up <4.251895031,-18.17596856,-0> }
background {color rgb 0}
object { bead(material {texture {pigment {color rgb <0.003921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.246538723,-3.985274444,0.3429104985> }
object { bead(material {texture {pigment {color rgb <0.007843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.871785957,-1.98168411,3.474611934> }
object { bead(material {texture {pigment {color rgb <0.01176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.497033191,1.73382468,3.604698598> }
object { bead(material {texture {pigment {color rgb <0.01568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,3.951533465,0.6207924582> }
object { bead(material {texture {pigment {color rgb <0.01960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.747527659,2.755629034,-2.899397977> }
object { bead(material {texture {pigment {color rgb <0.02352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.372774893,-0.8207820462,-3.914884013> }
object { bead(material {texture {pigment {color rgb <0.02745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.998022127,-3.688143724,-1.548417214> }
object { bead(material {texture {pigment {color rgb <0.03137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.623269362,-3.369426815,2.155681548> }
object { bead(material {texture {pigment {color rgb <0.03529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.248516596,-0.1399614564,3.997550599> }
object { bead(material {texture {pigment {color rgb <0.03921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376383,3.210412477,2.386053589> }
object { bead(material {texture {pigment {color rgb <0.0431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.499011064,3.787405757,-1.286684743> }
object { bead(material {texture {pigment {color rgb <0.04705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.124258298,1.092570908,-3.847894075> }
object { bead(material {texture {pigment {color rgb <0.05098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.7495055319,-2.546103725,-3.085021203> }
object { bead(material {texture {pigment {color rgb <0.05490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.3747527659,-3.985274444,0.3429104985> }
object { bead(material {texture {pigment {color rgb <0.05882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,-1.98168411,3.474611934> }
object { bead(material {texture {pigment {color rgb <0.06274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.3747527659,1.73382468,3.604698598> }
object { bead(material {texture {pigment {color rgb <0.06666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.7495055319,3.951533465,0.6207924582> }
object { bead(material {texture {pigment {color rgb <0.07058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.124258298,2.755629034,-2.899397977> }
object { bead(material {texture {pigment {color rgb <0.07450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.499011064,-0.8207820462,-3.914884013> }
object { bead(material {texture {pigment {color rgb <0.07843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.87376383,-3.688143724,-1.548417214> }
object { bead(material {texture {pigment {color rgb <0.08235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.248516596,-3.369426815,2.155681548> }
object { bead(material {texture {pigment {color rgb <0.0862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.623269362,-0.1399614564,3.997550599> }
object { bead(material {texture {pigment {color rgb <0.09019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.998022127,3.210412477,2.386053589> }
object { bead(material {texture {pigment {color rgb <0.09411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.372774893,3.787405757,-1.286684743> }
object { bead(material {texture {pigment {color rgb <0.09803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.747527659,1.092570908,-3.847894075> }
object { bead(material {texture {pigment {color rgb <0.1019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,-2.546103725,-3.085021203> }
object { bead(material {texture {pigment {color rgb <0.1058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.497033191,-3.985274444,0.3429104985> }
object { bead(material {texture {pigment {color rgb <0.1098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.871785957,-1.98168411,3.474611934> }
object { bead(material {texture {pigment {color rgb <0.1137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.246538723,1.73382468,3.604698598> }
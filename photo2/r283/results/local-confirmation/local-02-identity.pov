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


camera {orthographic location <-47.8108226797,-1.92481553993,88.0132799661> direction <0.526365334293,-0,-0.850258510604> right <24.690715583,-0.807599542737,15.2851592777> up <-0.539525159149,-22.8164113809,-0.334001174011> }
background {color rgb 0}
object {bead(material {texture {pigment {color rgb <0.00392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-28.7810364081,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.0078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-28.3313327142,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.0117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-27.8816290203,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.0156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-27.4319253264,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.0196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.9822216326,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.0235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.5325179387,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.0274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.0828142448,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.0313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-25.6331105509,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.0352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-25.1834068571,-0.34933472103,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.0392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-24.7337031632,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.043137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-24.2839994693,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.0470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.8342957754,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.0509803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.3845920816,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.0549019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.9348883877,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.0588235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.4851846938,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.0627450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.0354809999,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.0666666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-21.5857773061,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.0705882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-21.1360736122,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.0745098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.6863699183,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.2366662244,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.0823529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-19.7869625305,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.0862745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-19.3372588367,-0.34933472103,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.0901960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.8875551428,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.0941176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.4378514489,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.0980392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.988147755,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.101960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.5384440612,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.105882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.0887403673,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.109803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.6390366734,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.113725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.1893329795,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.7396292857,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.121568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.2899255918,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.125490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.8402218979,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.129411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.390518204,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.133333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.9408145102,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.137254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.4911108163,-0.34933472103,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.141176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.0414071224,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.145098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.5917034285,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.149019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.1419997347,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.152941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.6922960408,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.2425923469,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.160784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.792888653,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.164705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.3431849591,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.16862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.89348126527,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.172549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.4437775714,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.176470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.99407387752,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.180392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.54437018365,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.18431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.09466648977,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.188235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.64496279589,-0.34933472103,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.192156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.19525910202,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.74555540814,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.2,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.29585171426,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.203921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.84614802039,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.207843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.39644432651,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.211764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.94674063264,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.21568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703693876,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.219607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.04733324488,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.223529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762955101,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.227450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792585713,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.23137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.69822216326,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851846938,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.239215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.7988147755,-0.34933472103,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.243137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.34911108163,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.247058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.899407387752,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.250980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703693876,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.254901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.258823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.449703693876,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.262745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.899407387752,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.266666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.34911108163,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.270588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.7988147755,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.24851846938,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.278431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.69822216326,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.282352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.14792585713,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.286274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.59762955101,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.290196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.04733324488,-0.34933472103,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.294117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.49703693876,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.298039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.94674063264,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.301960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.39644432651,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.305882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.84614802039,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.309803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.29585171426,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.74555540814,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.317647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.19525910202,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.321568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.64496279589,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.325490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.09466648977,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.329411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.54437018365,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.333333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.99407387752,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.337254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.4437775714,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.341176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.89348126527,-0.349334721031,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.345098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.3431849591,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.349019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.792888653,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.2425923469,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.356862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.6922960408,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.360784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.1419997347,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.364705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.5917034285,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.36862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.0414071224,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.372549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.4911108163,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.376470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.9408145102,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.380392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.390518204,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.38431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.8402218979,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.388235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.2899255918,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.7396292857,-0.349334721031,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.396078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.1893329795,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.4,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.6390366734,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.403921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.0887403673,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.407843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.5384440612,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.411764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.988147755,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.41568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.4378514489,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.419607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.8875551428,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.423529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <19.3372588367,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.427450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <19.7869625305,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.43137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.2366662244,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.435294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.6863699183,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.439215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <21.1360736122,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.443137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <21.5857773061,-0.34933472103,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.447058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.0354809999,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.450980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.4851846938,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.454901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.9348883877,1.29278875513,-3.78532656908>}
object {bead(material {texture {pigment {color rgb <0.458823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.3845920816,-2.38087497673,-3.21425486624>}
object {bead(material {texture {pigment {color rgb <0.462745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.8342957754,-3.99777103644,0.133516816039>}
object {bead(material {texture {pigment {color rgb <0.466666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <24.2839994693,-2.16111060588,3.36594725882>}
object {bead(material {texture {pigment {color rgb <0.470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <24.7337031632,1.54246953847,3.69063513814>}
object {bead(material {texture {pigment {color rgb <0.474509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <25.1834068571,3.9135557413,0.827092171234>}
object {bead(material {texture {pigment {color rgb <0.478431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <25.6331105509,2.90383656353,-2.75095132859>}
object {bead(material {texture {pigment {color rgb <0.482352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.0828142448,-0.614421377277,-3.95252911073>}
object {bead(material {texture {pigment {color rgb <0.486274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.5325179387,-3.60189881167,-1.73963356787>}
object {bead(material {texture {pigment {color rgb <0.490196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.9822216326,-3.47780209513,1.97608010645>}
object {bead(material {texture {pigment {color rgb <0.494117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <27.4319253264,-0.34933472103,3.98471645825>}
object {bead(material {texture {pigment {color rgb <0.498039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <27.8816290203,3.08091261548,2.55107378486>}
object {bead(material {texture {pigment {color rgb <0.501960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <28.3313327142,3.84965041025,-1.08636629128>}
object {bead(material {texture {pigment {color rgb <0.505882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <28.7810364081,1.29278875513,-3.78532656908>}
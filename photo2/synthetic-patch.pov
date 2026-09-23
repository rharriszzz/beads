// Instrumented synthetic benchmark; geometry and transforms come from Python.
#version 3.7;
global_settings { assumed_gamma 1.0 }
#include "patch-data.inc"
#include "bead-shape.inc"
#ifndef (Beauty) #declare Beauty=0; #end
#ifndef (Only) #declare Only=-1; #end
camera { orthographic location <0,0,1000> direction -z
         right x*ViewWidth up y*ViewHeight }
background { color rgb 0 }
#if (Beauty)
  light_source { <-70,80,150> color rgb 1 }
  light_source { <60,-40,100> color rgb 0.25 shadowless }
  plane { z,-35 pigment { color srgb <0.85,0.41,0.75> }
          finish { ambient 0 diffuse 0.8 } }
#end
#for (I,0,BeadCount-1)
  #if ((Only<0) | (Only=I))
    #if (Beauty)
      #declare M=material { texture {
        pigment { color srgb <0.8,0.13,0.035> }
        finish { ambient 0 diffuse 0.7 specular 0.6 roughness 0.06 }
      } }
    #else
      // Exact IDs: no lights, shading, antialiasing, gamma or dithering.
      #declare M=material { texture { pigment { color rgb IDColors[I] }
                           finish { ambient 0 emission 1 diffuse 0 } } }
    #end
    object { bead(M,0.8,HeightRatio,1.0)
      matrix <BasisX[I].x,BasisX[I].y,BasisX[I].z,
              Axes[I].x,Axes[I].y,Axes[I].z,
              BasisZ[I].x,BasisZ[I].y,BasisZ[I].z,0,0,0>
      translate Positions[I]
    }
  #end
#end

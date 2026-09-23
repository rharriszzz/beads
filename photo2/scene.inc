// Photo-2 mode: numerical geometry belongs to Python, appearance belongs here.
#version 3.7;
global_settings { assumed_gamma 1.0 max_trace_level 10 }
#include "scene-data.inc"
#include "bead-shape.inc"

camera {
  orthographic
  location <0,0,10000>
  direction -z
  right x*PhotoWidth
  up y*PhotoHeight
}
// Input light coordinates use image x/y, relative to the image center.
light_source {
  <PhotoLight.x,-PhotoLight.y,PhotoLight.z> color rgb PhotoLightStrength
  area_light <PhotoLightSize,0,0>, <0,PhotoLightSize,0>, 5,5
  adaptive 1 circular orient
}
light_source { <0,0,6000> color rgb PhotoFill shadowless }
plane { z,0
  texture {
    pigment { color srgb PhotoPaper }
    normal { bumps PhotoPaperBump scale 4 }
    finish { ambient 0 diffuse 0.9 roughness 0.2 }
  }
}
#declare PhotoBeads = array[3];
#for (C,0,2)
  #declare PhotoMaterial = material {
    texture {
      pigment { color srgb PhotoPalette[C] }
      finish { ambient 0 diffuse 0.7 specular PhotoSpecular
               roughness PhotoRoughness reflection {0.025,0.12 fresnel on} conserve_energy }
    }
    interior { ior 1.5 }
  }
  #declare PhotoBeads[C] = bead(PhotoMaterial,0.8,PhotoHeightRatio,1.0);
#end
#for (I,0,PhotoCount-1)
  object { PhotoBeads[PhotoColors[I]] rotate z*PhotoAngles[I] translate PhotoPositions[I] }
#end

// Conservative rounded-annulus ray marcher, literal R295 stopping semantics.
#include <cmath>
#include <algorithm>
extern "C" void march(long n, const double* q, const double* v, const double* begin,
 const double* end, const double* dims, double radius, int direction,
 double* depth, int* state) {
 const double scale=std::min(dims[0],std::min(dims[1],dims[2]));
 for(long i=0;i<n;++i){
  double t=begin[i]; int status=2;
  for(int it=0;it<450;++it){
   const double x=(q[3*i]+t*v[3*i])/dims[0];
   const double y=(q[3*i+1]+t*v[3*i+1])/dims[1];
   const double z=(q[3*i+2]+t*v[3*i+2])/dims[2];
   const double a=std::abs(std::hypot(y,z)-.57*radius)-.086*radius;
   const double b=std::abs(x)/(.7/.43)-.086*radius;
   const double sd=(std::hypot(std::max(a,0.),std::max(b,0.))+std::min(std::max(a,b),0.)-.344*radius)*scale;
   if(sd<1e-5){status=1;break;}
   t+=direction*std::max(sd,1e-5);
   if(direction*(t-end[i])>0){status=0;break;}
  }
  depth[i]=t;state[i]=status;
 }
}

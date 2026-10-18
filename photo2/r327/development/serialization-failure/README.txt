Initial practice export failed because edge keys contained NumPy int64 values.
The partial gzip and original runner source are preserved. The serializer was
changed to explicitly convert NumPy scalar/array values; subsequent practice and
full inference outputs use strict finite JSON. No photographic criterion changed.

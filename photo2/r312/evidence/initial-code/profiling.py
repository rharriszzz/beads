"""In-process statistical stack sampler plus exclusive subsystem instrumentation."""
import sys, threading, time, collections, resource
from contextlib import contextmanager

class Sampler:
    def __init__(self,interval=.005):
        self.interval=interval;self.samples=collections.Counter();self.stop=threading.Event()
    def __enter__(self):
        self.target=threading.get_ident();self.started=time.perf_counter()
        def sample():
            while not self.stop.wait(self.interval):
                frame=sys._current_frames().get(self.target);stack=[]
                while frame:
                    stack.append(f'{frame.f_code.co_filename}:{frame.f_code.co_name}:{frame.f_lineno}');frame=frame.f_back
                self.samples[';'.join(reversed(stack))]+=1
        self.thread=threading.Thread(target=sample,daemon=True);self.thread.start();return self
    def __exit__(self,*args):self.stop.set();self.thread.join();self.seconds=time.perf_counter()-self.started
    def result(self):
        inclusive=collections.Counter()
        for stack,n in self.samples.items():
            for frame in set(stack.split(';')):inclusive[frame]+=n
        return dict(interval_seconds=self.interval,sample_count=sum(self.samples.values()),wall_seconds=self.seconds,stacks=dict(self.samples),inclusive_frames=dict(inclusive.most_common()),limitation='Python stack sampling includes the Python call site while native NumPy/SciPy/C++ executes; sampling can be delayed by the GIL. Subsystem wall timers provide independent timings.')

class Timers:
    def __init__(self):self.values=collections.Counter();self.calls=collections.Counter();self.stack=[]
    @contextmanager
    def span(self,name):
        began=time.perf_counter();item=[name,0.];self.stack.append(item)
        try:yield
        finally:
            dt=time.perf_counter()-began;self.stack.pop();self.values[name]+=dt-item[1];self.calls[name]+=1
            if self.stack:self.stack[-1][1]+=dt
    def bind(self,scene):
        # camera normal calculation is separate from camera visibility tracing.
        for method,label in [('trace','camera_ray_tracing'),('blocked','light_occlusion'),('camera','surface_normals')]:
            original=getattr(scene,method)
            def wrapped(*args,_original=original,_label=label,**kwargs):
                with self.span(_label):return _original(*args,**kwargs)
            setattr(scene,method,wrapped)
    def result(self):return dict(exclusive_seconds=dict(self.values),calls=dict(self.calls),peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)

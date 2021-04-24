import psutil                   # pip3 install psutil
import subprocess
import time

class ProcessTimer:

  def __init__(self, args):
    self.args = args

    self.max_vms_mu = 0     # maximum VMS memory usage
    self.max_rss_mu = 0     # maximum RSS memory usage

    self.t1 = None
    self.t0 = time.time()
    self.comp_proc = subprocess.Popen(self.args,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)


  def poll(self):
    if not self.check_execution_state():
      return False

    self.t1 = time.time()

    try:
      pp = psutil.Process(self.comp_proc.pid)
      pps = [pp] + pp.children(recursive=True)

      # calculate and sum memory usage
      rss_mu = 0
      vms_mu = 0
      for p in pps:
        try:
          rss_mu += p.memory_info().rss
          vms_mu += p.memory_info().vms
        except psutil.error.NoSuchProcess:
          #sometimes a subprocess p will have terminated between the time
          # we obtain a list of pps, and the time we actually poll this
          # p's memory usage.
          pass
      self.max_vms_mu = max(self.max_vms_mu, vms_mu)
      self.max_rss_mu = max(self.max_rss_mu, rss_mu)

    except psutil.error.NoSuchProcess:
      return self.check_execution_state()

    return self.check_execution_state()


  def is_running(self):
    return psutil.pid_exists(self.comp_proc.pid) and self.comp_proc.poll() == None

  def check_execution_state(self):
    if self.is_running():
      return True
    self.executation_state = False
    self.t1 = time.time()
    return False


  def assertClosed(self, kill=False):
    try:
      pp = psutil.Process(self.comp_proc.pid)
      if kill:
        pp.kill()
      else:
        pp.terminate()
    except psutil.error.NoSuchProcess:
      pass

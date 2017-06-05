#!/usr/bin/env python

#############################################
#
# Patcher script to place shells in a layout by rack
#
# Ingests a CSV of shells
#
#############################################

def list_init(count, value=0):
  _list = list()
  for i in range(count):
    _list.append(value)
  return _list

class Device:
  def __init__(self, name, cal, cue, shell_count=1):
    self.name = name
    self.cal = cal
    self.cue = cue
    self.shell_count = shell_count

class RackAssn:
  def __init__(self, device, strip, term):
    self.device = device
    self.strip = strip
    self.term = term

class Rack:
  def __init__(self, cal, tube_count):
    self.cal = cal
    self.tube_count = tube_count
    # a rack has tubes which will be assigned
    self.tubes = list_init(tube_count, None)

  # how many tubes are unassigned on this rack?
  def open_tubes(self):
    open = 0
    for tube in self.tubes:
      if tube is None:
        open += 1
    return open

  # assign a device
  def assign(self, device, strip, term):
    # device needs to be a Device
    if type(device) is not Device:
      raise ValueError("Can't assign a %s, need a Device" % type(device))
    # make sure we can assign here
    if device.cal != self.cal:
      raise ValueError("Can't assign a %f\" device to a %f\" rack!" %\
        (device.cal, self.cal)) 
    if self.open_tubes() < device.shell_count:
      raise ValueError("Can't assign a %d-shell device, only %d tubes left" %\
        (device.shell_count, self.tube_count)
    # can be assigned here.
    rack_assn = RackAssn(device, strip, term)
    # ffw to first empty tube
    tube_offset = 0
    while self.tubes[tube_offset] is not None:
      self.tube_offset += 1
    # assign to as many tubes as it needs
    for i in range(device.shell_count):
      self.tubes[tube_offset + i] = rack_assn

class Strip:
  def __init__(self, strip_id, term_count):
    self.strip_id = strip_id
    self.count = term_count
    self.terms = list_init(term_count, None)

  def open_terms(self):
    open = 0
    for term in self.terms:
      if term is None:
        open += 1
    return open

  def assign(self, device):

# how many strips can the board assign?
STRIP_COUNT = 12
# how many terms on a strip?
STRIP_TERMS = 48
# how many cue prefixes are there?
CUE_PREFIX_COUNT = 12
# how many cues per prefix?
PREFIX_CUES = 48
# how much physical space is there between the sockets for strip N and N+1?
STRIP_WIDTH = 4.0
# how much physical space is there between the sockets for strip N, term M and M+1?
TERM_DIST = 0.25
# what % of wire length do we add in for slack?
SLACK_RATIO = 0.3

# headers for the csv file, may change year to year
NAME_KEY = "Effect Name"
CAL_KEY = "Caliber"
CAT_KEY = "Category"
QTY_KEY = "Number Of Devices"
# getting shell counts off chains
CHAIN_PATTERN = re.compile(r'^.*[cC]hain\s+[oO]f\s+(\d+).*$')

# this is the master class! this calculates and optimizes patch wire lengths for us
class Board:
  def __init__(self, cue_file):
    # create all the strips
    self.strips = list()
    for i in range(STRIP_COUNT):
      self.strips.append(Strip(i, STRIP_TERMS))

    # these are splitters for multi-device cues
    self.multicues = list_init(multicue_count, None)

    # set up a list of lists for cues
    self.cues = list()
    for i in range(CUE_PREFIX_COUNT):
      self.cues.append(list_init(PREFIX_CUES, None))  

    # read the cues in from the cue file
    for device in read_devices(cue_file):
      # initially, place them wherever they go.
  
  def _get_cue_indices(self, cue_number):
    cue_prefix = int(cue_number) / int(100) # if cue is 735, cue prefix is 7
    cue_offset = cue_number - cue_prefix # if cue is 735, cue offset is 35
    # obi-wan error! use the source, luke!
    # 735 is cue[6][34]
    return (cue_prefix - 1, cue_offset - 1)

  def _get_cue_number(self, cue_column, cue_row):
    # obi-wan error! use the source, luke!
    cue_prefix = cue_column + 1
    cue_offset = cue_row + 1
    return (cue_prefix * 100) + cue_offset

  def assign_cue(self, cue_number, device):
    (cue_column, cue_row) = _get_cue_indices(cue_number)
    self.cues[cue_column][cue_row] = device

  def get_cue(self, cue_number):
    (cue_column, cue_row) = _get_cue_indices(cue_number)
    return self.cues[cue_column][cue_row]

  def read_devices(self, cue_filename):
    for device_hash in self.read_csv(cue_filename):
      device_name = device_hash[NAME_KEY]
      device_cal = device_hash[CAL_KEY]
      device_cue = device_hash[CUE_KEY]
      # how many devices are on this cue? 1 by default
      device_count = 1
      # usually 1, but how many shells on this cue?
      total_shells = device_hash[QTY_KEY]
      if total_shells = 1:
        pass
      else: # looks like a chain.
        device_shells = self._get_shell_count(device_name)
        device_count = total_shells / device_shells
      for i in range(device_count):
        # make a device from this hash
        yield Device(device_name, device_cal, device_cue, device_shells)

  def read_csv(self, filename):
    header_row = None
    with open(filename, 'rb') as csvfile:
      rows = csv.reader(csvfile)
      for row in rows:
        if header_row is None:
          header_row = row
        else:
          # a real row! 
          row_dict = {}
          for i in range(len(header_row)):
            if i < len(row):
              header = header_row[i]
              row_dict[header] = row[i]
          yield row_dict

  def _get_shell_count(self, device_name):
    m = re.match(CHAIN_PATTERN, device_name)
    if not m:
      return 1 # not a chain
    else:
      return int(m.group(1))





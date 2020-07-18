import sys

def get_atom_head(f):
    "Get the next atom from the file"
    data = f.read(4)                    # read the first bytes 0..3
    atom_size = int.from_bytes(data,"big") # convert to integer
    atom_type = f.read(4)                   # read bytes 4..7

    atom_size -= 8
    
    # todo: handle special size cases, 0 and 1
    print("get_atom_head() data = ", data,
          "atom_size = ", atom_size,
          "atom_type = ", atom_type)

    assert (atom_size >= 0)

    return atom_size, atom_type


def process_ftyp(f, atom_size):
    "process the body of an ftyp atom"
    magic2 = f.read(4)                   # read bytes 8..11
    atom_size -= 4
    print ("magic2 = ", magic2)

    if (magic2 == b'isom'):
        print('It is an ISO Base Media file (MPEG-4) v1')
    elif (magic2 == b'MSNV'):
        print('It is a MPEG-4 video file')
    elif (magic2 == b'mp42'):
        print('It is an MPEG-4 video|QuickTime file')
    elif (magic2 == b'qt  '):
        print('It is a QuickTime movie file')
    elif (magic2 == b'M4V '):
        print('It is an ISO Media, MPEG v4 system, or iTunes AVC-LC file')
    else:
        print('Unknown ftyp', magic2)

    print("seeking by", atom_size)
    f.seek(atom_size, 1) # skip the rest of the atom body
        
    return atom_size


def process_mdat(f, atom_size):
    "process the body of an ftyp atom"

    print("mdat atom, seeking by", atom_size)
    f.seek(atom_size, 1) # skip the rest of the atom body
        
    return atom_size


def process_moov(f, atom_size):
    "process the body of an ftyp atom"

    print("moov atom, seeking by", atom_size)
    f.seek(atom_size, 1) # skip the rest of the atom body
        
    return atom_size


def process_next_atom(f):
    "read the next atom from file f and process it"
    
    atom_size, atom_type = get_atom_head(f)

    if (atom_type == b'wide'):
        print("ignoring wide atom, atom body size = ", atom_size)
        assert(0 == atom_size)
    elif (atom_type == b'skip'):
        print("skip atom, seeking by ", atom_size)
        f.seek(atom_size, 1) # skip to the atom_size (wrt. file head)
    elif (atom_type == b'free'):
        print("free atom, seeking by ", atom_size)
        f.seek(atom_size, 1) # skip to the atom_size (wrt. file head)
    elif (atom_type == b'ftyp'):
        atom_size = process_ftyp(f, atom_size)
    elif (atom_type == b'mdat'):
        atom_size = process_mdat(f, atom_size)
    elif (atom_type == b'moov'):
        atom_size = process_moov(f, atom_size)
    else:
        print('Unrecognised atom type', atom_type)


fileList = sys.argv        # get the argument list
progName = fileList.pop(0) # pop the script name off the head of the list

print("progname = ", progName)
print("fileList = ", fileList)

for pathname in fileList:
    print("pathname = ", pathname)
    with open(pathname, 'rb') as f:
        # Read the header
        process_next_atom(f)
        process_next_atom(f)
        process_next_atom(f)
        process_next_atom(f)
        print("file offset = ", f.tell())
        




    
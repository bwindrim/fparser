import sys
import os

def get_atom_head(f):
    "Get the next atom from the file"
    data = f.read(4)                    # read the first bytes 0..3
    atom_size = int.from_bytes(data,"big") # convert 32 bits to integer
    atom_type = f.read(4)                   # read bytes 4..7

    if (1 == atom_size):
        # using extended size field
        print("using extended atom size")
        data = f.read(8)
        atom_size = int.from_bytes(data,"big") # convert 64 bits to integer
    
    # todo: handle special size cases, 0 and 1
    print("get_atom_head() data = ", data,
          "atom_size = ", atom_size,
          "atom_type = ", atom_type)

    print ("atom_size =", atom_size)
    assert (atom_size >= 0)

    return atom_size, atom_type


def process_ftyp(f, body_end):
    "process the body of an ftyp atom"
    type_list = []

    while (f.tell() < body_end):
        magic2 = f.read(4)                   # read bytes 8..11
        print ("magic2 = ", magic2)
        type_list.append(magic2)

    magic2 = type_list[0]
    
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

    print("seeking to", body_end)
    f.seek(body_end, 0) # skip the rest of the atom body
        
    return type_list


def process_mdat(f, body_end):
    "process the body of an ftyp atom"

    print("mdat atom, seeking to", body_end)
    body_start = f.tell()
    f.seek(body_end, 0) # skip the rest of the atom body
        
    return [body_start, body_end]


def process_moov(f, body_end):
    "process the body of an ftyp atom"

    print("moov atom, seeking to", body_end)
    f.seek(body_end, 0) # skip the rest of the atom body
        
    return []


def process_wide(f, body_end):
    "process the body of a wide atom"
    print("ignoring wide atom")
    assert(body_end == f.tell())


def process_skip(f, body_end):
    "process the body of an skip atom"
    print("skip atom, seeking to ", body_end)
    f.seek(body_end, 0) # skip to the atom_size (wrt. file head)


def process_free(f, body_end):
    "process the body of a free atom"
    print("free atom, seeking to ", body_end)
    f.seek(body_end, 0) # skip to the atom_size (wrt. file head)


def process_next_atom(f, end_pos):
    "read the next atom from file f and process it"

    pos = f.tell()

    if (pos + 8 > end_pos):
        # not enough remaining bytes for an atom header
        return None

    atom_size, atom_type = get_atom_head(f)

    body_end = pos + atom_size

    if (body_end > end_pos):
        # not enough remaining bytes for the atom body
        return None
    
    atom_body = None

    if (atom_type == b'wide'):
        atom_body = process_wide(f, body_end)
    elif (atom_type == b'skip'):
        atom_body = process_wide(f, body_end)
    elif (atom_type == b'free'):
        atom_body = process_wide(f, body_end)
    elif (atom_type == b'ftyp'):
        atom_body = process_ftyp(f, body_end)
    elif (atom_type == b'mdat'):
        atom_body = process_mdat(f, body_end)
    elif (atom_type == b'moov'):
        atom_body = process_moov(f, body_end)
    else:
        print('Unrecognised atom type', atom_type)

    return [atom_type, atom_size, atom_body]
    

file_list = sys.argv        # get the argument list
prog_name = file_list.pop(0) # pop the script name off the head of the list

print("prog_name = ", prog_name)
print("file_list = ", file_list)

for pathname in file_list:
    atom_list = []
    file_length = os.stat(pathname).st_size
    print("pathname = ", pathname)
    with open(pathname, 'rb') as f:
        while (f.tell() < file_length):
            atom_list.append (process_next_atom(f, file_length))
            print("file offset = ", f.tell())

    print("Atom_list = ", atom_list)
    
        




    

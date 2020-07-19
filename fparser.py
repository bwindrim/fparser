import sys
import os

def get_ftyp(f, body_end):
    "process the body of an ftyp atom"
    type_list = []

    while (f.tell() < body_end):
        magic2 = f.read(4)                   # read bytes 8..11
        print ("magic2 = ", magic2)
        type_list.append(magic2)

    print("seeking to", body_end)
    f.seek(body_end, 0) # skip the rest of the atom body
        
    return type_list


def get_mdat(f, body_end):
    "process the body of an mdat atom"

    body_start = f.tell()
    print("mdat atom, seeking to", body_end)
    f.seek(body_end, 0) # skip the rest of the atom body
        
    return [body_start, body_end]


def get_moov(f, body_end):
    "process the body of a moov atom"

    print("moov atom, seeking to", body_end)
    f.seek(body_end, 0) # skip the rest of the atom body
        
    return []


def get_wide(f, body_end):
    "process the body of a wide atom"
    print("ignoring wide atom")
    assert(body_end == f.tell())

    return None


def get_skip(f, body_end):
    "process the body of an skip atom"
    print("skip atom, seeking to ", body_end)
    f.seek(body_end, 0) # skip to the atom_size (wrt. file head)

    return body_end

def get_free(f, body_end):
    "process the body of a free atom"
    print("free atom, seeking to ", body_end)
    f.seek(body_end, 0) # skip to the atom_size (wrt. file head)
    # todo: check body for consisten value at return [value, byte_count]
    return body_end


def get_unknown(f, body_end):
    "process the body of an unknown atom"
    body_start = f.tell()
    print("unknown atom, seeking to ", body_end)
    f.seek(body_end, 0) # skip to the atom_size (wrt. file head)

    return [body_start, body_end]


# Mapping dict from atom type code to handler function
type_mapping = {
    b'wide':get_wide,
    b'skip':get_skip,
    b'free':get_free,
    b'ftyp':get_ftyp,
    b'mdat':get_mdat,
    b'moov':get_moov
    }


def get_next_atom(f, end_pos):
    "read the next atom from file f and process it"

    pos = f.tell() # pos is the very start of the atom

    # Check if enough remaining bytes for an atom header
    if (pos + 8 > end_pos):
        return None

    # Read the atom header
    data = f.read(4)                    # read the first 4 bytes of the atom
    atom_size = int.from_bytes(data,"big") # convert 32 bits to integer
    atom_type = f.read(4)                   # read bytes 4..7

    if (1 == atom_size):
        # using extended size field
        if (pos + 8 > end_pos):
            # not enough remaining bytes for a 64-bit atom size field
            return None

        print("using extended atom size")
        data = f.read(8)
        atom_size = int.from_bytes(data,"big") # convert 64 bits to integer
    
    # todo: handle special size cases, atom_size == 0
    print("get_next_atom() data = ", data,
          "atom_size = ", atom_size,
          "atom_type = ", atom_type)

    assert (atom_size >= 8)

    body_end = pos + atom_size

    if (body_end > end_pos):
        # not enough remaining bytes for the atom body
        return None

    atom_handler = type_mapping.get(atom_type, get_unknown)
    atom_body = atom_handler(f, body_end)

    return [atom_type, atom_size, atom_body]


def is_valid_file(atom):
    "check whether atom represents a valid QuickTime file"

    if (None == atom):
        print("No atom found")
        return False

    if (atom[0] != b'ftyp'):
        print("No ftyp atom found, first atom = ", atom)
        return False

    type_list = atom[2]
    major_brand = type_list[0]
    
    if (major_brand == b'isom'):
        print('It is an ISO Base Media file (MPEG-4) v1')
    elif (major_brand == b'MSNV'):
        print('It is a MPEG-4 video file')
    elif (major_brand == b'mp42'):
        print('It is an MPEG-4 video|QuickTime file')
    elif (major_brand == b'qt  '):
        print('It is a QuickTime movie file')
    elif (major_brand == b'M4V '):
        print('It is an ISO Media, MPEG v4 system, or iTunes AVC-LC file')
    else:
        print('Unknown ftyp', major_brand)
        return False

    return True


file_list = sys.argv        # get the argument list
prog_name = file_list.pop(0) # pop the script name off the head of the list

print("prog_name = ", prog_name)
print("file_list = ", file_list)

# Loop over the files from the command line
for pathname in file_list:
    print("pathname = ", pathname)
    file_length = os.stat(pathname).st_size
    
    with open(pathname, 'rb') as f:
        # Get the first atom in the file
        atom_list = get_next_atom(f, file_length)

        # check if the first atom is a valid ftyp
        if (is_valid_file(atom_list)):
            # Loop over the remaining atoms in the file
            while (f.tell() < file_length):
                atom_list.append (get_next_atom(f, file_length))
                print("file offset = ", f.tell())
        else:
            print("Invalid QuickTime file")
            
        # We've been through the file, now print the list of atoms
        print("atom_list = ", atom_list)
    
        




    

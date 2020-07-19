import sys
import os

def get_ftyp(f, atom_type, body_end):
    "process the body of an ftyp atom"
    type_list = []

    # Loop reading 4-byte type fields
    while ((body_end - f.tell()) >= 4):
        magic2 = f.read(4)
#        print ("magic2 = ", magic2)
        type_list.append(magic2)

    assert(f.tell() == body_end)

    # Unpack the first two fields in the list
    major_brand = type_list.pop(0)
    minor_version = type_list.pop(0)
    print("major, minor = ", major_brand, minor_version)
    
    return [major_brand, minor_version, type_list]


def get_mdat(f, atom_type, body_end):
    "process the body of an mdat atom"

    body_start = f.tell()
    print("mdat atom, seeking to", body_end)
    f.seek(body_end, 0) # skip the rest of the atom body
        
    return [body_start, body_end]


def get_container_atom(f, atom_type, body_end):
    "process the body of a container atom"
    atom_list = []
    
    # Loop over the nested atoms in this atom
    while (f.tell() < body_end):
        atom_list.append (get_next_atom(f, file_length))
#        print("file offset = ", f.tell())
    
    assert(f.tell() == body_end)
        
    return atom_list


def get_wide(f, atom_type, body_end):
    "process the body of a wide atom"
    print("ignoring wide atom")
    assert(f.tell() == body_end)

    return None


def get_skip(f, atom_type, body_end):
    "process the body of a skip atom"
#    print("skip atom, seeking to ", body_end)
    f.seek(body_end, 0) # skip to the atom_size (wrt. file head)

    return body_end

def get_free(f, atom_type, body_end):
    "process the body of a free atom"
#    print("free atom, seeking to ", body_end)
    f.seek(body_end, 0) # skip to the atom_size (wrt. file head)
    # todo: check body for consistent value, and return [value, byte_count]
    return body_end

unknown_types = set()

def get_unknown(f, atom_type, body_end):
    "process the body of an unknown atom"
    unknown_types.add(atom_type)
    body_start = f.tell()
#    print("unknown atom, ", atom_type, " seeking to ", body_end)
    f.seek(body_end, 0) # skip to the atom_size (wrt. file head)

    return [body_start, body_end]


# Mapping dict from atom type code to handler function
type_mapping = {
    b'wide':get_wide,
    b'skip':get_skip,
    b'free':get_free,
    b'ftyp':get_ftyp,
    b'mdat':get_mdat,
    b'moov':get_container_atom,
    b'mdia':get_container_atom,
    b'trak':get_container_atom,
    b'clip':get_container_atom,
    b'udta':get_container_atom,
    b'ctab':get_container_atom,
    b'tapt':get_container_atom,
    b'matt':get_container_atom,
    b'edts':get_container_atom,
    b'tref':get_container_atom,
    b'txas':get_container_atom,
    b'load':get_container_atom,
    b'imap':get_container_atom,
#    b'':get_container_atom,
    b'minf':get_container_atom,
    b'rmra':get_container_atom
    }

types_seen = set()

def get_next_atom(f, end_pos):
    "read the next atom from file f, stopping at end_pos, and return it as a list"

    pos = f.tell() # pos is the very start of the atom

    # Check if enough remaining bytes for an atom header
    if (pos + 8 > end_pos):
        print("File integrity error: atom header exceeds remaining bytes")
        return None

    # Read the atom header
    data     = f.read(4)                   # read first 4 bytes of the atom
    atom_size = int.from_bytes(data,"big") # & convert to unsigned (size)
    atom_type = f.read(4)                  # read next 4 bytes (type)

    # Check for special atom size cases, 0 and 1
    if (0 == atom_size): # atom extends to end of file
        atom_size = end_pos - pos # or end of enclosing atom if not top-level
        print("atom extends to end of file or parent, atom_size = ", atom_size)
    elif (1 == atom_size): # using extended size field
        if (pos + 8 > end_pos): # not enough bytes for extended size field
            return None

        print("using extended atom size")
        data = f.read(8)                       # read next 8 bytes of the atom
        atom_size = int.from_bytes(data,"big") # & convert to unsigned (size)
        assert(atom_size >= 16)

    # We've successfully read the atom header
#    print("get_next_atom() size = ", atom_size, "type = ", atom_type)

    assert (atom_size >= 8)

    body_end = pos + atom_size

    if (body_end > end_pos): # not enough remaining bytes for the atom body
        print("File integrity error: atom size exceeds remaining bytes")
        return None

    types_seen.add(atom_type) # add the atom type to the set of seen types
    atom_handler = type_mapping.get(atom_type, get_unknown)
    atom_body = atom_handler(f, atom_type, body_end)

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
        print('ISO Base Media file (MPEG-4) v1')
    elif (major_brand == b'MSNV'):
        print('MPEG-4 video file')
    elif (major_brand == b'mp42'):
        print('MPEG-4 video|QuickTime file')
    elif (major_brand == b'qt  '):
        print('QuickTime movie file')
    elif (major_brand == b'M4V '):
        print('ISO Media, MPEG v4 system, or iTunes AVC-LC file')
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
        types_seen.clear()
        unknown_types.clear()
        # Get the first atom in the file
        atom_list = get_next_atom(f, file_length)

        # check if the first atom is a valid ftyp
        if (is_valid_file(atom_list)):
            # Loop over the remaining atoms in the file
            while (f.tell() < file_length):
                atom_list.append (get_next_atom(f, file_length))
#                print("file offset = ", f.tell())
        else:
            print("Invalid QuickTime file")
            
        # We've been through the file, now print the list of atoms
        print("atom_list = ", atom_list)
        print("types_seen = ", types_seen)
        print("unknown_types = ", unknown_types)
        print("handled types = ", types_seen - unknown_types)
        




    

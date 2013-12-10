# net_ecc.py
# Part of the "Better UDP" project
# CSE 5344 - Computer Networking
# Fall, 2013
#
# Modified from code by Emin Martinian.  See below for license terms.

__doc__ = """
This package implements an erasure correction code for network
packets.  Specifically it lets you take a data buffer meant
for network transmission and break it into N pieces such that
the original can be recovered from any K pieces.  This is done
using Reed-Soloman coding on the original data.

With the Reed-Solomon code used in this package, if you use n=8, k=4
you divide the data into 8 pieces such that as long as at least 4 pieces
are available recovery can occur.

The docstrings for the functions EncodePackets and DecodePackets
provide detailed information on usage and the docstring
license_doc describes the license and lack of warranty.

The following is an example of how to use this file:

>>> import math
>>> import net_ecc
>>> data = ''
>>> for i in range(10000): data += chr(i % 256)
>>> k = int(math.ceil(float(len(data)) / 256))
>>> n = int(math.ceil(k * 1.1))
>>> packets = net_ecc.EncodePackets (data, n, k)
>>> goodPackets = packets[0:1] + packets[2:10] + packets[12:]
>>> recoveredData = net_ecc.DecodePackets(goodPackets)
>>> recoveredData == data
True
"""



from rs_code import RSCode
from array import array

from random import randint
import os, struct, string

headerSep = '|'

def MakeHeader(n,k,size,seq):
    return string.join(['RS_PARITY_PIECE_HEADER',
                        'n',`n`,'k',`k`,'size',`size`,'seq',`seq`,'piece'],
                       headerSep) + headerSep

def ParseHeader(header):
    return string.split(header,headerSep)

def ReadEncodeAndWriteBlock(readSize, data, packetList, code):
    buffer = array('B')
    buffer.fromstring(data)
    for i in range(readSize, code.k):
        buffer.append(0)
    codeVec = code.Encode(buffer)
    for j in range(code.n):
        packetList[j] += struct.pack('B', codeVec[j])

def EncodePackets(data, n, k):
    """
    Function:     EncodePackets(data, n, k)
    Description:  Encodes the data passed in, splitting it into n
                  chunks. At least k of the chunks must be present
                  to recover the original data.

                  Returns a list of n chunks to send.
                
                  Note n and k must satisfy 0 < k < n < 257.
                  Use the DecodePackets function for decoding.
    """
    packetList = []
    if (n > 256 or k >= n or k <= 0):
        raise Exception, 'Invalid (n,k), need 0 < k < n < 257.'
    inSize = len(data)
    header = MakeHeader(n,k,inSize,randint(0,99999))
    code = RSCode(n,k,8,shouldUseLUT=-(k!=1))
    for i in range(n):
        packetList.append(header + `i` + '\n')

    if (k == 1): # just doing repetition coding
        for packet in range(len(packetList)):
            packetList[packet] += data
    else: # do the full blown RS encodding
        for i in range(0, (inSize/k)*k,k):
            ReadEncodeAndWriteBlock(k, data[i:i+k], packetList, code)

        if ((inSize % k) > 0):
            ReadEncodeAndWriteBlock(inSize % k, data[-(inSize % k):], packetList, code)

    return packetList

def ExtractPieceNums(headers):
    l = range(len(headers))
    pieceNums = range(len(headers))
    for i in range(len(headers)):
        l[i] = ParseHeader(headers[i])
    for i in range(len(headers)):
        if (l[i][0] != 'RS_PARITY_PIECE_HEADER' or
            l[i][2] != l[0][2] or l[i][4] != l[0][4] or
            l[i][6] != l[0][6] or l[i][8] != l[0][8]):
            raise Exception, 'Packet ' + `i` + ' has incorrect header.'
        pieceNums[i] = int(l[i][10])
    (n,k,size) = (int(l[0][2]),int(l[0][4]),long(l[0][6]))
    if (len(pieceNums) < k):
        raise Exception, ('Not enough parity for decoding; needed '
                          + `l[0][4]` + ' got ' + `len(headers)` + '.')
    return (n,k,size,pieceNums)

def ReadDecodeAndWriteBlock(writeSize, packetList, bytesRead, outPacket, code):
    buffer = array('B')
    for j in range(code.k):
        buffer.fromlist([ord(packetList[j][bytesRead[j]:bytesRead[j]+1])])
        bytesRead[j] += 1
    result = code.Decode(buffer.tolist())
    for j in range(writeSize):
        outPacket += struct.pack('B', result[j])
    return outPacket

def DecodePackets(packetList):
    """
    Function:     DecodePackets(packetList)
    Description:  Takes received packets created using EncodePackets and
                  recovers the original data returning it.
                  The argument packetLIst must be a list of at least k
                  received packets.
    """
    headers = range(len(packetList))
    bytesRead = range(len(packetList))
    for i in range(len(packetList)):
        bytesRead[i] = packetList[i].find('\n') + 1
        headers[i] = packetList[i][:bytesRead[i]-1]
    (n,k,inSize,pieceNums) = ExtractPieceNums(headers)
    outPacket = ''
    code = RSCode(n,k,8)
    decList = pieceNums[0:k]
    code.PrepareDecoder(decList)
    for i in range(0, (inSize/k)*k,k):
        outPacket = ReadDecodeAndWriteBlock(k,packetList,bytesRead,outPacket,code)
    if ((inSize%k)>0):
        outPacket = ReadDecodeAndWriteBlock(inSize%k,packetList,bytesRead,outPacket,code)
    return outPacket

license_doc = """
  This code is modified from the file_ecc.py code written by Emin
  Martinian (emin@allegro.mit.edu).  It was modified by Clay Sims and
  Shannon Jones for CSE 5344 (Computer Networking).  The original code
  was for recovering erased blocks from files.  It was modified isntead
  to handle erased blocks from network transmission.  Below is the original
  license from Emin's code.

  This code was originally written by Emin Martinian (emin@allegro.mit.edu).
  You may copy, modify, redistribute in source or binary form as long
  as credit is given to the original author.  Specifically, please
  include some kind of comment or docstring saying that Emin Martinian
  was one of the original authors.  Also, if you publish anything based
  on this work, it would be nice to cite the original author and any
  other contributers.

  There is NO WARRANTY for this software just as there is no warranty
  for GNU software (although this is not GNU software).  Specifically
  we adopt the same policy towards warranties as the GNU project:

  BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
PROVIDE THE PROGRAM 'AS IS' WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
REPAIR OR CORRECTION.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES.
"""

# The following code is used to make the doctest package
# check examples in docstrings.

def _test():
    import doctest, net_ecc
    return doctest.testmod(net_ecc)

if __name__ == "__main__":
    _test()
    print 'Tests passed'

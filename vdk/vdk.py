import os
import sys
import binascii
import time
import zlib
import struct


class VDK(object):
	"""
	Gravity proprietary archive for Ragnarok Online 2 client files

	TODO: Document file format

	:param str path: Path to VDK file
	"""

	_progress = 0
	_timer = 0

	verbose = False

	root = ""
	version = None
	files = None
	dirs = None
	size = None
	flist = None

	def __init__(self, path):
		"""Initialize object and open VDK"""
		self.path = path
		self.root = os.path.split(self.path)[0] 
		self.name = os.path.splitext(os.path.basename(self.path))[0]

	def unpack(self):
		"""Extract VDK file to a subdirectory"""

		self.vdk = open(self.path, "rb")
		self.version, _, self.files, self.dirs, self.size, self.flist = self._header()
		self._timer = time.time()

		def recursive(path="."):
			noffset = 1
			while noffset:
				bit, fname, usize, zsize, doffset, noffset = \
					struct.unpack("<?128sIIII", self.vdk.read(145))
				fname = fname.decode("cp949").rstrip("\0")

				if bit:
					if not os.path.exists(path):
						os.makedirs(path)

					if fname not in (".", ".."):
						recursive("{0}/{1}".format(path, fname))
				else:
					fpath = "{0}/{1}".format(path, fname)

					self._progress += 1
					if self.verbose:
						print("[{0:.2%}] Extracting: {1} ...".format(self._progress/self.files, fpath))

					data = self.vdk.read(zsize)
					self._inflate(fpath, data)

		recursive("{0}/{1}".format(self.root, self.name))
		self.vdk.close()

		if self.verbose:
			print("\nExtraction complete! ({:.2f}s)\n".format(time.time() - self._timer))

	def pack(self, directory):
		"""
		Packs directory into a VDK file.

		:param str directory: directory name to pack
		"""

		print("\nPacking is not implemented yet.\n", file=sys.stderr)

	def _header(self):
		h = list(struct.unpack("<8sIIII", self.vdk.read(24)))
		h[0] = h[0].decode("UTF-8")

		if h[0] == "VDISK1.1":
			h.append(struct.unpack("<I", self.vdk.read(4))[0])
		elif h[0] == "VDISK1.0":
			h.append(0)
		else:
			return

		return tuple(h)

	@staticmethod
	def _inflate(fpath, data):
		"""
		Decompress DEFLATE data and write to file

		:param str fpath: Path of file to write
		:param data: DEFLATE data to decompress to file
		"""

		f = open(fpath, "wb")
		d = zlib.decompressobj()

		try:
			# Write decompressed DEFLATE data
			f.write(d.decompress(data))
			f.write(d.flush())
		except zlib.error:
			# Write data as-is if not DEFLATE
			f.truncate(0)
			f.seek(0)
			f.write(data)

		f.close()

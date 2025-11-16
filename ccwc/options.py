import codecs
import os
import locale
import sys


DEFAULT_PROBES = ['a', '¢', '€', 'あ', '𐍈']

        
class WCMachine:
    
    def __init__(self, options, *args, **kwargs):
        """
        initialize the WCMachine
        """
        self.args = options
        self.files = options.files
    
    def get_raw(self, f):
        """
        Gets the input as raw
        """
        raw = getattr(f, 'buffer', None)
        
        # robust raw detection
        if raw is None:
            # probe to check if f.read(0) is a byte-like object
            try:
                probe = f.read(0)
            except Exception:
                probe = None
    
            if isinstance(probe, (bytes, bytearray)):
                raw = f
            else:
                raw = None
        return raw      

    def get_encoding(self):
        """
        Get the encoding of the locale.
        """
        try:
            enc = locale.nl_langinfo(locale.CODESET)
            if enc:
                return enc
        except Exception:
            pass
        return locale.getpreferredencoding(False) or 'utf-8'

    def enc_is_multibyte(self, enc):
        """
        Return True if encoding `enc` is capable of representing any of the probe
        characters with more than one output byte.
        """
        probes = DEFAULT_PROBES
        # quick heuristic: treat encodings with 'utf' or 'ucs' as multibyte
        if 'utf' in enc or 'ucs' in enc or 'utf-16' in enc or 'utf-32' in enc:
            return True
        for ch in probes:
            try:
                b = ch.encode(enc)
            except Exception:
                # can't encode this probe — skip it (doesn't prove single-byte)
                continue
            if len(b) > 1:
                return True
        return False

    def enc_supports_multibyte_chars(self, enc):
        """
        Checks if locale's encoding supports multibyte characters 
        """
        return self.enc_is_multibyte(enc)

    def get_all_counts(self, f):
        """
        Returns the count of bytes, words and lines 
        """
        line_count = 0
        word_count = 0
        byte_size = 0
                
        enc = self.get_encoding()
        raw = self.get_raw(f)
        
        # If possible, rewind to start so we count from the beginning.
        try:
            if hasattr(f, 'seek') and f.seekable():
                f.seek(0)
        except Exception:
            # continue if seeking fails
            pass
        
        # for streams/byte
        if raw is not None:
            decoder = codecs.getincrementaldecoder(enc)(errors='replace')
            remainder = ''
            for chunk in iter(lambda: raw.read(8192), b''):
                if not chunk:
                    break
                byte_size += len(chunk)
                text = decoder.decode(chunk)
                text = remainder + text
                parts = text.split('\n')
                for part in parts[:-1]:
                    line_count += 1
                    word_count += len(part.split())
                remainder = parts[-1]
            
            # flush decoder
            tail = decoder.decode(b'', final=True)
            remainder += tail
            if remainder:
                line_count += 1
                word_count += len(remainder.split())

        else:
            reader = f.read
            remainder = ''
            while True:
                text_chunk = reader(8192)
                if not text_chunk:
                    break
                byte_size += len(text_chunk.encode(enc, 'replace'))
                text = remainder + text_chunk
                parts = text.split('\n')
                for part in parts[:-1]:
                    line_count += 1
                    word_count += len(part.split())
                remainder = parts[-1]
            if remainder:
                line_count += 1
                word_count += len(remainder.split())

        return line_count, word_count, byte_size
                
    def default(self, f):
        """
        Counts the lines, words and bytes
        """
        line_count, word_count, byte_size = self.get_all_counts(f)        
        print(f"{line_count}  {word_count}  {byte_size}  {self.name}")
   
    def get_bytes(self, f):
        try:
            if f.seekable():
                cur = f.tell()
                f.seek(0, 2)
                size = f.tell()
                f.seek(cur)
                return size
        except Exception:
            pass
        size = 0
        raw = self.get_raw(f)
        if raw is not None:
            for chunk in iter(lambda: raw.read(8192), b''):
                if not chunk:
                    break
                size += len(chunk)
            return size   
        
        # fallback for text streams
        enc = self.get_encoding()
        reader = f.read
        while True:
            text_chunk = reader(8192)
            if not text_chunk:
                break
            size += len(text_chunk.encode(enc, 'replace'))
        return size
        
    def bytes_count(self, f):
        """
        Counts the bytes
        """
        byte_size = self.get_bytes(f)
        print(f"{byte_size}  {self.name}")
        
    def characters_count(self, f):
        """
        Counts the characters or the bytes if locale's encoding 
        does not support multibyte characters 
        """
        count = 0
        enc = self.get_encoding().lower()
        
        if not self.enc_supports_multibyte_chars(enc):
            count = self.get_bytes(f)
        else:
            raw = self.get_raw(f)
            decoder = codecs.getincrementaldecoder(enc)(errors='replace')
            if raw is not None:
                for chunk in iter(lambda: raw.read(8192), b''):
                    if not chunk:
                        break
                    text = decoder.decode(chunk)
                    if text:
                        count += len(text)
                tail = decoder.decode(b'', final=True)
                count += len(tail)
            else:
                for line in f:
                    count += len(line)
        print(f"{count}  {self.name}")

    def words_count(self, f):
        """
        Couns the words
        """
        count = sum(len(line.split()) for line in f)
        print(f"{count}  {self.name}")

    def lines_count(self, f):
        """
        Counts the newlines
        """
        count = sum(1 for _ in f)
        print(f"{count}  {self.name}")

    def process_input(self, f):
        """
        Sends the input to the right handler depending the option passed
        """
        args = self.args
        self.name = getattr(f, 'name', 'stdin')
        
        if args.c:
            self.bytes_count(f)
        elif args.l:
            self.lines_count(f)
        elif args.w:
            self.words_count(f)
        elif args.m:
            self.characters_count(f)
        else:
            self.default(f)   

    def handle_inputs(self):
        """
        Preprocess the input.
        If input is a file, open file before processing content.
        """
        if not self.files:
            self.process_input(sys.stdin)
        for name in self.files:
            if os.path.isfile(name):
                print
            try:
                with open(name, 'rb') as f:
                # with open(name, 'r', encoding='utf-8', newline='') as f:
                    self.process_input(f)
                f.close()
            except FileNotFoundError:
                print(f"Error: File not found - {name}", file=sys.stderr)

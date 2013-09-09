import mailbox
import sys
import os
import warnings
import rfc822
import time
import errno


class MacMaildirMessage(mailbox.Message):
    def __init__(self, message=None):
        if hasattr(message, "read"):
            bytes = int(message.readline().strip())
            message = message.read(bytes)

        mailbox.Message.__init__(self, message)

class MacMaildir(mailbox.Mailbox):
    def __init__(self, dirname, factory=rfc822.Message, create=True):
        mailbox.Mailbox.__init__(self, dirname, factory, create)
        if not os.path.exists(self._path):
            if create:
                raise NotImplemented("Why would we support creation of silly mailboxes?")
            else:
                raise mailbox.NoSuchMailboxError(self._path)

        ds = os.listdir(self._path)
        if not 'Info.plist' in ds:
            raise mailbox.FormatError(self._path)

        ds.remove('Info.plist')

        self._id = ds[0]
        self._mailroot = "%s/%s/Data/" % (self._path, self._id)

        self._toc = {}
        self._last_read = 0

    def remove(self, key):
        """Remove the message or raise error if nonexistent."""
        raise NotImplemented("Mailpile is readonly, for now.")
        # FIXME: Hmm?
        #os.remove(os.path.join(self._mailroot, self._lookup(key)))

    def discard(self, key):
        """If the message exists, remove it."""
        try:
            self.remove(key)
        except KeyError:
            pass
        except OSError, e:
            if e.errno != errno.ENOENT:
                raise

    def __setitem__(self, key, message):
        """Replace a message"""
        raise NotImplemented("Mailpile is readonly, for now.")

    def iterkeys(self):
        self._refresh()
        for key in self._toc:
            try:
                self._lookup(key)
            except KeyError:
                continue
            yield key

    def has_key(self, key):
        self._refresh()
        return key in self._toc

    def __len__(self):
        self._refresh()
        return len(self._toc)

    def _refresh(self):
        self._toc = {}
        paths = [""]

        while not paths == []:
            curpath = paths.pop(0)
            fullpath = os.path.join(self._mailroot, curpath)
            for entry in os.listdir(fullpath):
                p = os.path.join(fullpath, entry)
                if os.path.isdir(p):
                    paths.append(os.path.join(curpath, entry))
                elif entry[-5:] == ".emlx":
                    self._toc[entry[:-5]] = os.path.join(curpath, entry)

    def _lookup(self, key):
        try:
            if os.path.exists(os.path.join(self._mailroot, self._toc[key])):
                return self._toc[key]
        except KeyError:
            pass
        self._refresh()
        try:
            return self._toc[key]
        except KeyError:
            raise KeyError("No message with key %s" % key)

    def get_message(self, key):
        subpath = self._lookup(key)
        f = open(os.path.join(self._mailroot, subpath), 'r')
        msg = MacMaildirMessage(f)
        f.close()
        subdir, name = os.path.split(subpath)
        return msg

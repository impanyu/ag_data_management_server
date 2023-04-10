import pyinotify


# Define the event handler
class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, pid):
        super().__init__()
        self.pid = pid
        self.written_files = set()
        self.accessed_files = set()
        self.created_files = set()

    def process_IN_ACCESS(self, event):
        if not event.dir:
            self.accessed_files.add(event.pathname)

        #print(f"File {event.pathname} was read by PID {event.pid}")

    def process_IN_CREATE(self, event):
        self.created_files.add(event.pathname)
        #print(f"File {event.pathname} was created by PID {event.pid}")

    def process_IN_DELETE(self, event):
        if event.pid == self.pid:
            print(f"File {event.pathname} was deleted by PID {event.pid}")

    def process_IN_MODIFY(self, event):
        if not event.dir:
            self.written_files.add(event.pathname)
            #print(f"File {event.pathname} was modified by PID {event.pid}")







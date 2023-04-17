import pyinotify
import os

# Define the event handler
class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, pid, container_id = ""):
        super().__init__()
        self.pid = pid
        self.written_files = set()
        self.accessed_files = set()
        self.created_files = set()
        self.container_id = container_id

    def process_IN_ACCESS(self, event):
        if self.find_container_id_by_pid(event.pid) == self.container_id:
            self.accessed_files.add(event.pathname)

        #print(f"File {event.pathname} was read by PID {event.pid}")

    def process_IN_CREATE(self, event):
        #if not event.dir:
        if self.find_container_id_by_pid(event.pid) == self.container_id:
            self.created_files.add(event.pathname)
        #print(f"File {event.pathname} was created by PID {event.pid}")

    def process_IN_DELETE(self, event):
        if event.pid == self.pid:
            print(f"File {event.pathname} was deleted by PID {event.pid}")

    def process_IN_MODIFY(self, event):
        #if not event.dir:
        if self.find_container_id_by_pid(event.pid) == self.container_id:
            self.written_files.add(event.pathname)
            #print(f"File {event.pathname} was modified by PID {event.pid}")

    @staticmethod
    def find_container_id_by_pid(pid):
        try:
            with open(f'/proc/{pid}/cgroup', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'docker' in line or 'container' in line:
                        parts = line.strip().split('/')
                        container_id = parts[-1]
                        return container_id
        except FileNotFoundError:
            print(f"Process with PID {pid} not found.")
            return None










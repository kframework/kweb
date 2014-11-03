import subprocess, threading, os, time, shlex
from config import BASE_DIR

# Base unit of tool execution is a command.
class Command(object):
    # Initialize command
    def __init__(self, cmd, tool, action, root, path, current_file, uuid, args, stdin):
        self.uuid = uuid
        self.cmd = cmd
        self.process = None
        self.tool = tool
        self.action = action
        self.root = root
        self.path = path
        self.current_file = current_file
        self.output_file = ''
        self.run_time = time.time()
        self.args = args.strip()
        self.initial_stdin = stdin
        self.done = False

    # Begin command in another thread.
    def run(self):
        def target():
            self.run_time = time.time()
            # Worker thread for code execution of run tool
            print 'Thread started'
            # Get file path for communication results, stdin, etc. to
            # further requests (without redis caching)
            base_file_path = BASE_DIR + 'results/' + self.uuid
            self.output_file = open(base_file_path, 'a')
            self.output_file.write('')
            # Check which tool / action pair is being used, process accordingly.
            if self.tool.lower() == 'k':
                has_file_arg = self.args and (self.args[0] != '-')
                # Use our guess on whether a file arg is present to decide how to display executed command to user
                add_string = (' ' + self.current_file) if (self.args and len(self.args.strip())) else self.current_file
                if has_file_arg:
                    add_string = ''
                if self.action.lower() == 'kompile' and not '.k' in self.current_file and not len(self.args):
                    self.output_file.write('Invalid file type!  File must end in .k to be kompiled!\n')
                else:
                    # @todo : generalize this
                    for user_action in ['krun', 'ktest', 'kompile']:
                        if self.action.lower() == user_action:
                            self.output_file.write('Running command: ' + user_action + ' ' + ' '.join(shlex.split(self.args)) + add_string + '\n')
                            self.output_file.flush()
                            self.process = subprocess.Popen(['/k/bin/' + user_action] + shlex.split(self.args) + [self.current_file], stdout=self.output_file, stderr = self.output_file, stdin=subprocess.PIPE, shell=False, cwd = self.path)
                            self.process.stdin.write(self.initial_stdin + '\n')
                            open(base_file_path + '.in', 'w').write(str(self.process.stdin.fileno()))
                            self.process.wait()
                            empty = (len(open(base_file_path).read().strip().splitlines()) == 1)
                            self.output_file.write('----- End of process output')
                            if empty and user_action == 'kompile':
                                self.output_file.write(' (no output indicates a successful kompile)')
                            self.output_file.write('.\n')
                        elif self.action.lower() == user_action + '-help':
                            self.output_file.write('Running command: '+ user_action +' --help\n')
                            self.output_file.flush()
                            self.process = subprocess.Popen(['/k/bin/' + user_action, '--help'], stdout=self.output_file, stderr = subprocess.PIPE, stdin=subprocess.PIPE, shell=False)
                            open(base_file_path + '.in', 'w').write(str(self.process.stdin.fileno()))
                            self.process.wait()
            # @todo : super messy, clean up!
            elif self.tool.lower() == 'javamop':
                if self.action.lower() == 'run':
                    if len(self.args.split()) < 1:
                        self.output_file.write('Select a java file to compile and run!\n')
                    else:
                        java_file_name = self.args.split('/')[-1]
                        java_file_path = self.root + "/".join(self.args.split('/')[:-1])
                        action = ['javac', java_file_name]
                        self.output_file.write('>>> ' + ' '.join(action) + '\n')
                        self.output_file.flush()
                        self.process = subprocess.Popen(action, stdout=self.output_file, stderr = self.output_file, stdin=subprocess.PIPE, shell=False, cwd=java_file_path)
                        self.process.wait()
                        if self.process.returncode is not 0:
                            self.output_file.write('>>> Error in compilation!\n')
                        else:
                            action = ['java', java_file_name[:-5]]
                            self.output_file.write('>>> ' + ' '.join(action) + '\n')
                            self.output_file.flush()
                            self.process = subprocess.Popen(action, stdout=self.output_file, stderr = self.output_file, stdin=subprocess.PIPE, shell=False, cwd=java_file_path)
                            self.process.stdin.write(self.initial_stdin + '\n')
                            open(base_file_path + '.in', 'w').write(str(self.process.stdin.fileno()))
                            self.process.wait()
                            if self.process.returncode == 0:
                                self.output_file.write('>>> Program executed successfully!\n')
                            else:
                                self.output_file.write('>>> Error in executing the program!\n')
                elif self.action.lower() == 'run-help':
                    self.output_file.write('Select a java file to compile and run without monitoring!\n')
                if self.action.lower() == 'monitor':
                    args = shlex.split(self.args)
                    if len(args) < 2:
                        self.output_file.write('Select a java file and a property (.mop) file to (compile and) run the java file while monitoring the property!\n')
                    else:
                        java_file_name = args[0].split('/')[-1]
                        java_file_path = self.root + "/".join(args[0].split('/')[:-1])
                        mop_file_name = args[1].split('/')[-1]
                        mop_file_path = self.root + "/".join(args[1].split('/')[:-1])

                        action = ['javamop', '-agent', mop_file_path + mop_file_name]
                        self.output_file.write('>>> ' + ' '.join(action[:-1]) + ' ' + args[1] + '\n')
                        self.output_file.flush()
                        self.process = subprocess.Popen(action, stdout=self.output_file, stderr = self.output_file, stdin=subprocess.PIPE, shell=False, cwd=java_file_path)
                        self.process.wait()
                        if self.process.returncode is not 0:
                            self.output_file.write('>>> Error in generating the monitoring agent!\n')
                        else:
                            action = ['javac', java_file_name]
                            self.output_file.write('>>> ' + ' '.join(action) + '\n')
                            self.output_file.flush()
                            self.process = subprocess.Popen(action, stdout=self.output_file, stderr = self.output_file, stdin=subprocess.PIPE, shell=False, cwd=java_file_path)
                            self.process.wait()
                            if self.process.returncode is not 0:
                                self.output_file.write('>>> Error in compilation!\n')
                            else:
                                action = ['java', '-javaagent:' + mop_file_name[:-4] + ".jar", java_file_name[:-5]]
                                self.output_file.write('>>> ' + ' '.join(action) + '\n')
                                self.output_file.flush()
                                self.process = subprocess.Popen(action, stdout=self.output_file, stderr = self.output_file, stdin=subprocess.PIPE, shell=False, cwd=java_file_path)
                                self.process.stdin.write(self.initial_stdin + '\n')
                                open(base_file_path + '.in', 'w').write(str(self.process.stdin.fileno()))
                                self.process.wait()
                                if self.process.returncode == 0:
                                    self.output_file.write('>>> Program executed successfully!\n')
                                else:
                                    self.output_file.write('>>> Error in executing the program!\n')
                elif self.action.lower() == 'monitor-help':
                    self.output_file.write('Select a java file and a property (.mop) file to (compile and) run the java file while monitoring the property!\n')




            # Clean up after process
            self.done = True
            done_file = open(base_file_path + '.done', 'w')
            done_file.write('')
            done_file.close()
            self.output_file.close()
            print 'Thread finished.'

        # Supervisor thread to kill process after sixty seconds
        # of execution with no exit.
        def supervise(thread):
            thread.join(timeout = 60)
            if self.process and not self.done:
                try:
                    print 'Reaping process'
                    self.output_file.write('Error: Process timed out, job exceeded 60 seconds.\n')
                    self.process.terminate()
                except:
                    # This means there was no process, do nothing.
                    pass

        # Start threads using locally defined methods above
        thread = threading.Thread(target = target)
        supervisor_thread = threading.Thread(target = supervise, args = [thread])
        thread.start()
        supervisor_thread.start()

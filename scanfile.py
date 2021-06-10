#!/usr/bin/python
#
#
# MIT License
# Copyright (c) 2021 hb0m4x21 at oncosmos dot com
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# 
#  First version scan file with clamav multi-thread

import concurrent.futures
import logging

import subprocess
import os.path
import sys, getopt

from multiprocessing import Process, Queue


def readFile(queue,name):
   reader = open(name,'r')
   try:
       # Further file processing goes here
       while True:
           # Elimina los blancos y demas
           line = reader.readline().rstrip()
           if not line:
               break
           queue.put(line)
           #logging.info("Archivo: %s\n",line)
           
   finally:
      reader.close()

def copyData(data):
    v = []
    for x in data:
       v.append(x)
    return v

def managerQueue(queue,totalItem, worker,tasks):
   
   total = (totalItem / worker)
   if total==0:
       #only one
       total = totalItem
       logging.info("Total files into queue: %d",totalItem)
   else:
       logging.info("Total files into queue: %d",total)
       
   contador = 0
   vector = []
   queueCont = 0
   totalIter = 0
   
   while (totalIter < totalItem):       
       if contador < total:
           vector.append(str(queue.get()))
           contador = contador + 1
       else:
           if ((queueCont < worker) and (totalIter<totalItem)):
               tasks.append(copyData(vector))
               vector = []
               queueCont = queueCont + 1
           contador = 0
        
       totalIter = totalIter + 1

   
   if queueCont < worker:
       logging.info("Quene cont: %d",queueCont)
       #Last item odd
       if not queue.empty():
           vector.append(str(queue.get()))
           
       tasks.append(copyData(vector))
       
   else:
       logging.info("queue es mayor cont: %d",queueCont)
       
   
    
def done(fn):
    if fn.cancelled():
        print('{}: canceled'.format(fn.arg))
    elif fn.done():
        error = fn.exception()
        if error:
            print('{}: error returned: {}'.format(
                fn.arg, error))
        else:
            result = fn.result()
            print('{}: value returned: {}'.format(
                fn.arg, result))

def consumer(queue, threadid):
    """Pretend we're saving a number in the database."""
    #l = threading.Lock()
    while (len(queue) > 0):

        message = queue.pop(0)
        comando2 = "/tmp/thread_"+str(threadid)+".log"

	if os.path.isfile(message):

            
            p1 = subprocess.Popen(["clamscan",'--tempdir=/tmp/ram/','-i', message], stdout=subprocess.PIPE,)

            p2 = subprocess.Popen(["tee",'-a',  comando2], stdin=p1.stdout, stdout=subprocess.PIPE)

            stdout, stderr = p2.communicate()

            ##Only test
            for line in stdout.split('\n'):
                logging.info("msg : %s", line)

            p0 = subprocess.Popen(["echo","Resultado: "], stdout=subprocess.PIPE,)
            p01 = subprocess.Popen(["tee",'-a',  comando2], stdin=p0.stdout, stdout=subprocess.PIPE)
            p0 = subprocess.Popen(["echo",message], stdout=subprocess.PIPE,)
            p01 = subprocess.Popen(["tee",'-a',  comando2], stdin=p0.stdout, stdout=subprocess.PIPE)

            logging.info(
                "Scan file: %s worker: %s total: (size=%d)", message,threadid,len(queue)
             )
        else:
            logging.info("NO EXISTE : %s", message)
    
    return len(queue)

def main(argv):
    scanfile = ''
    worker = 1;
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    try:
        opts, args = getopt.getopt(argv,"hf:w:",["file=","worker=",])
    except getopt.GetoptError:
        print 'scanfile.py -f <inputfile> -w <thread>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'scanfile.py -f file.ext -w n-thread'
            sys.exit()
        elif opt in ("-f", "--file"):
            scanfile = arg
        elif opt in ("-w", "--worker"):
            worker = int(arg)

    tasks = []
    pipeline = Queue()
    readFile(pipeline,scanfile)
    managerQueue(pipeline,pipeline.qsize(),worker,tasks)

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker) as executor:
        for index in range(worker):
            if (len(tasks)>0):
                executor.submit(consumer,tasks.pop(0), index)    
            

    logging.info("Finished scan")

if __name__ == "__main__":
    main(sys.argv[1:])
    

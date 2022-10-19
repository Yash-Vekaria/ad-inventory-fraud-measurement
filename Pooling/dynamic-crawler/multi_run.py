import subprocess
import os



# Helpful Docker Commands
'''
docker build -t dynamic-crawler .
python3 multi_run.py
docker container ls -a
docker container logs -f e1cbe52763d5
ssh -N -L localhost:20001:localhost:1212 yvekaria@ipaddress

Stop the container(s) using the following command: docker-compose down.
Delete all containers using the following command: docker rm -f $(docker ps -a -q)
Delete docker container(s) based on regex: docker rm -f $(docker container ls -a | grep dynamic | awk '{print $1}')
Show stats of docker container(s) based on regex: docker stats $(docker container ls -a | grep dynamic | awk '{print $1}')

Killing browsermobproxy instances
To kill oldest 300 instances:
ps -eo etimes,pid,args --sort=start_time | grep browsermob | head -n 300 | awk '{print $2}' | sudo xargs kill
To kill all instances except the top/latest 20 instances:
ps -eo etimes,pid,args --sort=-start_time | grep browsermob | tail --lines=+20 | awk '{print $2}' | sudo xargs kill
To get count of total running instances:
ps -aux | grep browsermob | wc -l
'''


# Specify crawl number of label. Same preceded with "crawl_" will be used to name the directory to store output
crawl_number = "sample"
directory = "crawl_" + crawl_number

if not os.path.exists(directory):
    os.makedirs(directory)



def multiprocess_crawls():
    '''
    Function to multi-process dynamic crawls
    '''
    # Read website list under study
    fm = open("study_websites.txt", "r")
    study_domains = sorted(fm.read().split("\n"))
    fm.close()
    
    # Specify the number of threads, number of URLs assigned to each thread
    NUM_THREADS = 3
    NUM_URLS = len(study_domains)
    STEP_SIZE = int(NUM_URLS / NUM_THREADS)

    thread_id = 1
    for start_index in range(0, NUM_URLS, STEP_SIZE):

        # Distribute URLs to different threads
        urls_to_crawl = study_domains[start_index : start_index + STEP_SIZE]
        print("Agent %s will crawl %s URLs" % (thread_id, len(urls_to_crawl)))
        results_dir = os.path.join(os.getcwd(), directory)

        # Define arguments and run docker commands for each thread as a sub process
        args = (['docker', 'run', '-d', '-e', 'PYTHONUNBUFFERED=1', '-v', '%s:/results' % results_dir, '-p', f'{thread_id}:1212', '--shm-size=10g', 'dynamic-crawler', 'python', 'dynamic_crawl.py', str(crawl_number), ','.join(urls_to_crawl), str(thread_id), '/results'])
        print("Port", 1000+thread_id)
        print(args)
        subprocess.run(args)
        thread_id += 1
    
    return



if __name__ == '__main__':

    multiprocess_crawls()
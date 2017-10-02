#!/usr/bin/env python
__doc__ = """{f}

Usage:
    {f} job ls [--max=N]
    {f} job info JOBID [--yaml | --yml]
    {f} job create [-f | --file] JOBCONFIG
    {f} job submit JOBID
    {f} job monitor JOBID [--yaml | --yml]
    {f} job delete JOBID
    {f} job stop JOBID
    {f} job share JOBID --email=ADDRESS [--message=MESSAGE]
    {f} file ls [JOBID [--run=N]][--max N] [--from DATE1 --to DATE2] [ext=EXTENSION]
    {f} file info FILEID
    {f} file update FILEID --type-id=N
    {f} file upload FILENAME [FILENAME...]
    {f} file sync JOBID [-f | --file OUTPUT_FILE [OUTPUT_FILE...]]
    {f} file download FILEID
    {f} application info
    {f} hardware info
    {f} skelton [-o | --output=FILENAME] [--analysis=APPLICATION]
    {f} -h | --help

Options:
    -f --file                   Indicate filename
    --run=N                     Indicate "run number" in DoE.
                                Default is all runs.
                                (e.g.) "--run=1,2,3": you can select multiple runs.
    --items=N                   Display from the latest job to N old jobs.
                                Default is N=256
    --email=ADDRESS             E-mail address with which you want to share
    --message=MESSAGE           this massage is sent by e-mail
    --type-id=N                 N is integer
    -h --help                   Show this screen and exit.
    --analysis APPLICATION      application name
    -o --output FILENAME
""".format(f=__file__)

#    --filter=OUTPUT_FILES       Enable to select files
#                                (e.g) "--filename=1,2,3"

# noinspection PyUnresolvedReferences
from docopt import docopt
import requests
import os
import sys
import json
import re
import subprocess
import shutil
import os.path
import yaml
import re

class RescaleApiResponse(object):
    def __init__(self, exit_code=False, my_text='{"returnVal", "default"}'):
        # if it is necessary to execute multiple-api....
        self.exit_code = exit_code
        self.text = my_text
        self.http_response_code = []
        self.url = []
        self.list = []

    def extract_http_response_code(self, text):
        pattern = r"[0-9]{3}"
        match = re.search(pattern, text)
        val = int(match.group())
        self.http_response_code.append(val)
        if val < 200 or val >= 300:
            self.exit_code = 1
            message1 = '\n\n' + self.url[-1] + '\n'
            message2 = self.text + '\n'
            message3 = '[Error]: http respond code: ' + match.group() + '\n\n'
            sys.stderr.write(message1)
            sys.stderr.write(message2)
            sys.stderr.write(message3)
            sys.exit(self.exit_code)
        return val

    def generate_exit_code(self):
        for val in self.http_response_code[:]:
            if val >= 200 and val < 300:
                self.exit_code = 0
            else:
                # Maybe, this "else" is not needed.
                # but, check the status again
                self.exit_code = 1
                message1 = '\n\nHttp Responses: ' + str(self.http_response_code) + '\n'
                message2 = '[Error]: http response code: ' + str(val) + '\n\n'
                sys.stderr.write(message1)
                sys.stderr.write(message2)
                sys.exit(self.exit_code)


class RescaleJob(RescaleApiResponse):

    # token: you can create the API Key by from Rescale-Platform by your browser.
    # platform:
    #   - US: https://platform.rescale.com/
    #   - JP: https:// platform.rescale.jp/
    def __init__(self, token, platform):
        super(RescaleJob, self).__init__()
        self.token = token
        self.platform = platform

    # add rescale fileIds to the job-json read from file
    def info(self, job_id):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/jobs/" + job_id + "/"
        self.url.append(url)
        res = requests.get(
          url,
          headers = {'Authorization': tokenValue}
        )
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

    #
    # Open/Read cluster Json
    #
    def read(self, filename):
        f = open(filename, 'r')
        s = f.read()
        f.close()
        return s
    #
    # change YAML data to JSON string
    #
    def yaml2json(self, my_yaml):
        my_dict = yaml.load(my_yaml)
        my_json = json.dumps(my_dict)
        return my_json
    def json2yaml(self, my_json):
        my_dict = json.loads(my_json)
        my_yaml = yaml.dump(my_dict)
        return my_yaml
    #
    # add rescale fileIds to the job-json read from file
    #
    def create(self, my_json):

        my_dict = json.loads(my_json)
        # Create Rescale Job with REST API
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/jobs/"
        self.url.append(url)
        res = requests.post(
            url,
            headers = {'Authorization': tokenValue},
            json = my_dict
        )

        # Exit Status
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

    # add rescale fileIds to the job-json read from file
    def submit(self, job_id):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/jobs/" + job_id + "/submit/"
        self.url.append(url)
        res = requests.post(
            url,
            headers = {'Authorization': tokenValue}
        )
        tmp_res = str(res)
        self.extract_http_response_code(tmp_res)
        return self

    # add rescale fileIds to the job-json read from file
    def monitor(self, job_id):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/jobs/" + job_id + "/statuses/"
        self.url.append(url)
        res = requests.get(
          url,
          headers = {'Authorization': tokenValue}
        )
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

    # delete the job
    # DELETE https://platform.rescale.com/api/v2/jobs/{job_id}/
    def delete(self, job_id):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/jobs/" + job_id + "/"
        self.url.append(url)
        res = requests.delete(
          url,
          headers = {'Authorization': tokenValue}
        )
        #print("test:", res.text)
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

    # stop the job
    # POST https://platform.rescale.com/api/v2/jobs/{job_id}/stop/
    def stop(self, job_id):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/jobs/" + job_id + "/stop/"
        self.url.append(url)
        res = requests.post(
          url,
          headers = {'Authorization': tokenValue}
        )
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

    # share the job
    # POST https://platform.rescale.com/api/v2/jobs/{job_id}/share/
    def share(self, job_id, address, message):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/jobs/" + job_id + "/share/"
        self.url.append(url)
        res = requests.post(
            url,
            headers = {'Authorization': tokenValue},
            json = {
                "email": address,
                "message": message
            }
        )

        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

    # List All Jobs
    def listjobs(self, page_size):

        #print(runs)
        tokenValue = 'Token' + ' ' + self.token
        my_dict = {"next": True}
        jobs = []
        page_size = str(page_size)
        max_pages = 1
        ipage = 1   # page number

        # loop of page number
        while my_dict['next']:
            page = str(ipage)
            url = self.platform + "api/v3/jobs/?page=" + page + "&page_size=" + page_size
            print("[url] ", url)
            self.url.append(url)
            res = requests.get(
                url,
                headers = {'Authorization': tokenValue}
            )
            my_json = res.text
            my_dict = json.loads(my_json)

            # loop of files into this page
            for f in my_dict['results'][:]:
                d = f['dateInserted'].split("T")
                tmp_date = d[0].rjust(10)
                #tmp_stat = str(f['jobStatus']['content']).rjust(11)
                tmp_id = f['id'].rjust(8)
                tmp_size = str(int(f['storage'] / 1000000)).rjust(9)
                tmp_app  = str(f['analysisNames']).ljust(32)
                tmp_name = f['name'].ljust(32)
                tmp = tmp_date + tmp_id + tmp_size + " mb " + tmp_app+ " " + tmp_name
                jobs.append(tmp)

            tmp_res = str(res)
            self.extract_http_response_code(tmp_res)
            if max_pages <= ipage:
                break
            ipage+=1    # end of "while my_dict['next']"

        self.list = jobs
        self.generate_exit_code()
        self.text = my_json
        self.generate_exit_code()
        return self


    # add rescale fileIds to the job-json read from file
    # GET: https://platform.rescale.jp/api/v3/jobs/{job_id}/runs/{run_id}/files/
    # [input]
    #   - job_id: JobId in Rescale
    #   - runs: run number in DoE job
    # [output]
    #   - file list including fileId and filename
    def outputfiles(self, job_id, runs):
        tokenValue = 'Token' + ' ' + self.token
        my_dict = {"next": True}
        allfiles = []
        page_size = "256"

        # loop of run number
        irun = 0
        for run_id in runs[:]:
            ipage = 1   # page number
            files_per_run = []
            run_id = str(run_id)

            # loop of page number
            while my_dict['next']:
                page = str(ipage)
                url = self.platform + "api/v3/jobs/" + job_id + "/runs/" + run_id + "/files/?page=" + page + "&page_size=" + page_size
                print("[url] ", url)
                self.url.append(url)
                res = requests.get(
                    url,
                    headers = {'Authorization': tokenValue}
                )
                my_dict = json.loads(res.text)

                # loop of files into this page
                for f in my_dict['results'][:]:

                    d = f['dateUploaded'].split(".")
                    tmp_date = d[0].rjust(19)
                    tmp_runs = run_id.rjust(6)
                    tmp_type = str(f['typeId']).rjust(2)
                    tmp_file = f['id'].rjust(8)
                    tmp_size = str(int(f['decryptedSize'] / 1000)).rjust(9)
                    tmp_path = f['relativePath'].ljust(32)

                    tmp = tmp_date + tmp_type + tmp_file + tmp_runs + tmp_size + " " + tmp_path
                    files_per_run.append(tmp)

                # store the http response code
                tmp_res = str(res)
                self.extract_http_response_code(tmp_res)

                # increment, and next page
                ipage+=1

            allfiles.append([])
            allfiles[irun] = files_per_run
            my_dict = {"next": True}
            irun+=1

        self.list = allfiles
        self.generate_exit_code()
        return self

    def list_all_files(self, page_size):
        tokenValue = 'Token' + ' ' + self.token
        my_dict = {"next": True}
        allfiles = []
        tmp = [1]
        psize = str(page_size)
        # loop of run number
        iter = 0
        for run_id in tmp[:]:
            ipage = 1   # page number
            files_per_run = []
            run_id = str(run_id)

            # loop of page number
            while ipage < 2:
                page = str(ipage)

                url = self.platform + "api/v3/files/" + "?page=" + page + "&page_size=" + psize + "&include_jobs=1&include_keys=0"
                print("[url] ", url)
                self.url.append(url)
                res = requests.get(
                    url,
                    headers = {'Authorization': tokenValue}
                )
                my_dict = json.loads(res.text)
                format_json = json.dumps(my_dict, indent=2, separators=(',', ': '))
                print(format_json)
                #date1 = "dateUploaded__gte=2017-08-31T15:00:00.000Z"
                #date2 = "dateUploaded__lte=2017-09-30T15:00:00.000Z"
                # loop of files into this page
                for f in my_dict['results'][:]:

                    d = f['dateUploaded'].split(".")
                    tmp_date = d[0].rjust(19)
                    tmp_type = str(f['typeId']).rjust(2)
                    tmp_file = f['id'].rjust(8)
                    tmp_size = str(int(f['decryptedSize'] / 1000)).rjust(9)
                    tmp_file_name = f['name'].ljust(20)
                    tmp_information = "----"
                    tmp_job_id = "----".rjust(8)
                    if f['typeId'] == 5:
                        tmp_path = f['path'].rjust(2)
                        match = re.search(r'\/output/job_(.+)\/run[0-9]+\/', tmp_path)
                        job_id = match.group(1)
                        #job_id = f['jobs']['results'][0]['id']
                        if f['jobs']['results']:
                            tmp_information = f['jobs']['results'][0]['name']
                            #tmp_information = "\n" + " ".rjust(47) + tmp_information
                        else:

                            tmp_information = "owner: " + f['owner']
                        tmp_job_id = job_id.rjust(8)
                    tmp = tmp_date + tmp_type + tmp_file + tmp_job_id + tmp_size + " " + tmp_file_name + " " + tmp_information
                    files_per_run.append(tmp)

                # store the http response code
                tmp_res = str(res)
                self.extract_http_response_code(tmp_res)

                # increment, and next page
                ipage+=1
            allfiles.append([])
            allfiles[iter] = files_per_run
            my_dict = {"next": True}
            iter+=1

        self.list = allfiles
        self.generate_exit_code()
        return self

    # input:  FileId
    # output: meta-info of a file by json
    # GET https://platform.rescale.com/api/v3/files/{file_id}/
    def fileinfo(self, file_id):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/files/" + file_id + "/"
        self.url.append(url)
        res = requests.get(
            url,
            headers = {'Authorization': tokenValue}
        )
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

    def updatetype(self, file_id, type_id):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/files/" + file_id + "/"
        self.url.append(url)
        update_json = {"typeId": int(type_id)}
        res = requests.patch(
            url,
            json = update_json,
            headers = {'Authorization': tokenValue}
        )
        #my_dict = json.loads(res.text)
        #print("typeId: ", my_dict['typeId'])
        #tmp_str = '{"typeId": ' + str(my_dict['typeId']) + '}'
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

    def upload(self, files):

        token = self.token
        #token = "asdfjkalsdhgkj;ahsdlk;kfjkla;sdjk"
        platform = self.platform
        dir_path = os.path.dirname(os.path.abspath(__file__))
        rescalecli = dir_path + "/rescale.jar"

        my_cmd = ["java", "-jar", rescalecli, "-X", platform, "--quiet", "upload", "-p", token, "-e", "-f"]
        my_cmd.extend(files)

        res_byte = subprocess.run(my_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        returncode = res_byte.returncode
        if returncode == 0:
            self.text = res_byte.stdout.decode('utf-8')
            self.exit_code = returncode
        else:
            stderr = "\n[error] file-upload was failure with RescaleCLI\n\n"
            sys.stderr.write(' '.join(my_cmd))
            sys.exit(returncode)
        return self

    def sync(self, jobid, files):

        token = self.token
        #token = "asdfjkalsdhgkj;ahsdlk;kfjkla;sdjk"
        platform = self.platform
        dir_path = os.path.dirname(os.path.abspath(__file__))
        rescalecli = dir_path + "/rescale.jar"

        #java -jar /usr/local/bin/rescale.jar \
        #-X https://platform.rescale.jp/ sync \
        #-p ${RESCALE_API_TOKEN} \
        #-j ${JOB_ID} \
        #-f ${FILE_NAME}

        if len(files) == 0:
            my_cmd = ["java", "-jar", rescalecli, "-X", platform, "sync", "-p", token, "-j", jobid]
        else:
            my_cmd = ["java", "-jar", rescalecli, "-X", platform, "sync", "-p", token, "-j", jobid, "-f"]
            my_cmd.extend(files)

        print(' '.join(my_cmd))
        res_byte = subprocess.run(my_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        returncode = res_byte.returncode
        if returncode == 0:
            self.text = res_byte.stdout.decode('utf-8')
            self.exit_code = returncode
        else:
            stderr = "\n[error] file-download was failure with RescaleCLI\n\n"
            sys.stderr.write(stderr)
            sys.stderr.write(' '.join(my_cmd))
            sys.exit(returncode)
        return self

    def skelton(self, outputfile, template):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        template_path = dir_path + "/jobskelton/" + template + ".yml"

        shutil.copy(template_path, outputfile)
        sys.exit(1)

    def sw_info(self):
        tokenValue = 'Token' + ' ' + self.token
        page = "1"
        page_size = "1024"
        url = self.platform + "api/v3/analyses/" + "?page=" + page + "&page_size=" + page_size
        self.url.append(url)
        res = requests.get(
            url,
            headers = {'Authorization': tokenValue}
        )
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

#        my_dict = {"next": True}
#        allitems = []
#        page_size = "512"
#
#        # loop of run number
#        isection = 0
#        ipage = 1   # page number
#        files_per_section = []
#
#        while my_dict['next']:
#            page = str(ipage)
#            url = self.platform + "api/v3/analyses/" + "?page=" + page + "&page_size=" + page_size
#            print("[url] ", url)
#            self.url.append(url)
#            res = requests.get(
#                url,
#                headers = {'Authorization': tokenValue}
#            )
#            my_dict = json.loads(res.text)
#            # loop of files into this page
#            for app in my_dict['results'][:]:
#                tmp_code = str(app['code'])
#                tmp_name = str(app['name'])
#                tmp = tmp_name + ": " + tmp_code
#                print(tmp)
#                files_per_section.append(tmp)
#            # store the http response code
#            tmp_res = str(res)
#            self.extract_http_response_code(tmp_res)
#            # increment, and next page
#            ipage+=1
#
#        allitems.append([])
#        allitems[isection] = files_per_section
#        my_dict = {"next": True}
#
#        self.list = allitems
#        self.generate_exit_code()
#        return self

    def hw_info(self):
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/coretypes/"
        self.url.append(url)
        res = requests.get(
            url,
            headers = {'Authorization': tokenValue}
        )
        self.text = res.text
        self.extract_http_response_code(str(res))
        self.generate_exit_code()
        return self

################################################################################
# Main
################################################################################


def rescale_api_handler(rescale_token, platform):
    args = docopt(__doc__)
    rescale = RescaleJob(rescale_token, platform)
    res = RescaleApiResponse()
    #print(args)

    if args['job']:
        # List All Jobs
        # GET https://platform.rescale.com/api/v2/jobs/
        if args['ls']:
            page_size = 32
            if args['--max']:
                page_size = args['--max']
            res = rescale.listjobs(page_size)
            for val in res.list[:]:
                print(val)
        # Detail of job
        # GET https://platform.rescale.com/api/v2/jobs/{job_id}
        if args['info']:
            job_id = args['JOBID']
            res = rescale.info(job_id)
            res_dict = json.loads(res.text)
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)
        # Create a Job:
        # POST https://platform.rescale.com/api/v2/jobs/
        if args['create']:
            if args['--file']:
                job_config = args['JOBCONFIG']
                # check the extension of the file
                my_path, ext = os.path.splitext(job_config)
                if ext == ".json":
                    my_json = rescale.read(job_config)
                elif ext == ".yml":
                    tmp_str = rescale.read(job_config)
                    my_json = rescale.yaml2json(tmp_str)
                else:
                    message1 = "\n[error] file type should be *.json or *.yml\n\n"
                    message2 = "filename:" + job_config
                    sys.stderr.write(message1)
                    sys.stderr.write(message2)
                    sys.exit(1)
            else:
                my_json = args['JOBCONFIG']

            res = rescale.create(my_json)
            res_dict = json.loads(res.text)
            job_id = res_dict['id']
            job_name = res_dict['name']
            job_owner = res_dict['owner']
            #job_inputfiles = res_dict['analysis'][:][inputFiles][:]['name']

            print("id:", job_id)
            print("name:", job_name)
            print("owner:", job_owner)
            #print("inputFiles: ",job_inputfiles)

            #my_yaml = yaml.dump(res_dict)
            #format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            #print(format_json)
            #print(my_yaml)
        # Submit a Saved Job:
        # POST https://platform.rescale.com/api/v2/jobs/{job_id}/submit/
        elif args['submit']:
            job_id = args['JOBID']
            res = rescale.submit(job_id)
            print(res.text)
        # List Job status history
        # GET https://platform.rescale.com/api/v2/jobs/{job_id}/statuses/
        elif args['monitor']:
            job_id = args['JOBID']
            res = rescale.monitor(job_id)
            res_dict = json.loads(res.text)
            if args['--yaml']:
                my_stdout = yaml.dump(res_dict)
            else:
                my_stdout = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(my_stdout)
        # Delete job
        # DELETE https://platform.rescale.com/api/v2/jobs/{job_id}/
        elif args['delete']:
            job_id = args['JOBID']
            res = rescale.delete(job_id)
            print(res.text)
        # stop the job
        # POST https://platform.rescale.com/api/v2/jobs/{job_id}/stop/
        elif args['stop']:
            job_id = args['JOBID']
            res = rescale.stop(job_id)
            print(res.text)
        # share the job
        # POST https://platform.rescale.com/api/v2/jobs/{job_id}/share/
        elif args['share']:
            job_id = args['JOBID']
            address = args['--email']
            if args['--message']: message = args['--message']
            else: message = "from RescaleAPI"
            res = rescale.share(job_id, address, message)
            res_dict = json.loads(res.text)
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)

    elif args['file']:
        # List Job Output Files
        # GET https://platform.rescale.com/api/v2/jobs/{job_id}/files/
        if args['ls']:
            if args['JOBID']:
                job_id = args['JOBID']
                # for indicated run number
                if args['--run']:
                    runs = args['--run'].split(",")
                    runs = [int(i) for i in runs]
                # for all files
                else:
                    res = rescale.info(job_id)
                    my_dict = json.loads(res.text)
                    run_max = my_dict["expectedRuns"]
                    runs = list(range(1, run_max + 1))
                res = rescale.outputfiles(job_id, runs)
                print("")
                print("-------------------------------------------------------------------")
                print("DATE              TYP  FileID  runs Size(kb) Relative FilePATH")
                print("-------------------------------------------------------------------")

                for files_per_run in res.list[:]:
                    for val in files_per_run:
                        print(val)
            #GET https://platform.rescale.com/api/v3/files/
            else:
                if args['--max']:
                    page_size = args['--max']
                else:
                    page_size = 64
                res = rescale.list_all_files(page_size)
                for files_per_run in res.list[:]:
                    for val in files_per_run:
                        print(val)

        # input: FileId
        # output: meta-info of a file by json
        # GET https://platform.rescale.com/api/v3/files/{file_id}/
        elif args['info']:
            file_id = args['FILEID']
            res = rescale.fileinfo(file_id)
            res_dict = json.loads(res.text)
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)

        elif args['update']:
            file_id = args['FILEID']
            type_id = args['--type-id']
            res = rescale.updatetype(file_id, type_id)
            res_dict = json.loads(res.text)
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)

        elif args['upload']:
            filenames = args['FILENAME']
            res = rescale.upload(filenames)
            res_dict = json.loads(res.text)
            for data in res_dict['files'][:]:
                name = data['name']
                file_id = data['id']
                print(file_id.ljust(8), name)

        elif args['sync']:
            jobid = args['JOBID']
            filenames = args['OUTPUT_FILE']
            res = rescale.sync(jobid, filenames)
            print(res.text)

    # Get a Specific Job
    # GET https://platform.rescale.com/api/v2/jobs/{job_id}/
    elif args['skelton']:
        if args['FILENAME']:
            outputfile = args['FILENAME']
        else:
            outputfile = "job-definition.yml"
        if args['FILENAME']:
            template = args['FILENAME']
        else:
            template = "user_included_mpi"
        res = rescale.skelton(outputfile, template)
    elif args['application']:
        if args['info']:
            res = rescale.sw_info()
            res_dict = json.loads(res.text)
            #my_yaml = yaml.dump(res_dict)
            #print(my_yaml)
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)
            #for files_per_run in res.list[:]:
            #    for val in files_per_run:
            #        print(val)
    elif args['hardware']:
        if args['info']:
            res = rescale.hw_info()
            res_dict = json.loads(res.text)
            my_yaml = yaml.dump(res_dict)
            #format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(my_yaml)
    else:
        if args['JOBID']:
            job_id = args['JOBID']
            res = rescale.info(job_id)
            res_dict = json.loads(res.text)
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)

    return res


if __name__ == '__main__':

    # Setting Token
    for key, val in os.environ.items():
        if key == 'RESCALE_API_TOKEN':
            token = val
        elif key == 'RESCALE_PLATFORM':
            rescale_platform = val

    r = rescale_api_handler(token, rescale_platform)
    sys.exit(r.exit_code)

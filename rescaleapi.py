#!/usr/bin/env python

__doc__ = """{f}

Usage:
    {f} job ls [--max=N]
    {f} job info JOBID
    {f} job create [-f | --file] JSON
    {f} job submit JOBID
    {f} job monitor JOBID
    {f} job delete JOBID
    {f} job stop JOBID
    {f} job share JOBID --email=ADDRESS [--message=MESSAGE]
    {f} file ls JOBID [--run=N]
    {f} file info FILEID
    {f} -h | --help

Options:
    -f --file           Indicate file PATH of jobconfig.json
    --run=N             Indicate "run number" in DoE. Default is all runs.
                        (e.g.) "--run=1,2,3": you can select multiple runs.
    --items=N           Display from the latest job to N old jobs.
                        Default is N=256
    --email=ADDRESS
    --message=MESSAGE
    -h --help           Show this screen and exit.
""".format(f=__file__)

# noinspection PyUnresolvedReferences
from docopt import docopt
import requests
import os
import sys
import json
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

    # Open/Read cluster Json
    def read(self, json_filename):
        f = open(json_filename, 'r')
        my_json = f.read()
        f.close()
        return my_json

    # add rescale fileIds to the job-json read from file
    def create(self, my_json):
        my_dict = json.loads(my_json)
        tokenValue = 'Token' + ' ' + self.token
        url = self.platform + "api/v3/jobs/"
        self.url.append(url)
        res = requests.post(
            url,
            headers = {'Authorization': tokenValue},
            json = my_dict
        )
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
                json_file = args['JSON']
                my_json = rescale.read(json_file)
            else:
                my_json = args['JSON']
            res = rescale.create(my_json)
            res_dict = json.loads(res.text)
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)
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
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)
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
            print("-----------------------------------------------------------")
            print("DATE              TYP  FileID  runs Size(kb) Relative FilePATH")
            print("-----------------------------------------------------------")

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
    # Get a Specific Job
    # GET https://platform.rescale.com/api/v2/jobs/{job_id}/
    else:
        if args['JOBID']:
            job_id = args['JOBID']
            res = rescale.info(job_id)
            res_dict = json.loads(res.text)
            format_json = json.dumps(res_dict, indent=2, separators=(',', ': '))
            print(format_json)

    return res


if __name__ == '__main__':

    #rescale_platform = 'https://platform.rescale.com/'
    rescale_platform = 'https://platform.rescale.jp/'

    # Setting Token
    for key, val in os.environ.items():
        if key == 'RESCALE_API_TOKEN':
            token = val

    r = rescale_api_handler(token, rescale_platform)
    sys.exit(r.exit_code)

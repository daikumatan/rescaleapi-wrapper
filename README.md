this program is my personal source code.
Please use this source code under your responsibility

There are not upload/download commands.
In this regards, you had better use the Rescale CLI.

Japanese doc is here:
http://qiita.com/daikumatan/items/f74c0ca82adfe0ef0730

I'm not good at Python, please tell me if you have a good code.

pre-condition
=======================

## Creating RescaleAPI


- Sign up to rescale.
- log in to rescale.
- create "API KEY" from your account page.
- Copy the "API KEY" displayed in your screen.

**if you cannot create "API Key", you had better contact rescale.**

## Edit your ~/.bashrc

set the API Key and Platform-URL

if JP,

```bash:.bashrc
echo 'export RESCALE_API_KEY=<API KEY>' >> ~/.bashrc
echo 'https://platform.rescale.jp/ >> ~/.bashrc'
```

if US,

```bash:.bashrc
echo 'export RESCALE_API_KEY=<API KEY>' >> ~/.bashrc
echo 'https://platform.rescale.com/ >> ~/.bashrc'
```

How to use rescaleapi command
=====================================

Job list
-----------

If you want to display the job list including **Job-IDs**, Please execute the following command. you can indicate the number of jobs with `--max=<int>`. <int> is positive integer.

```bash:command
rescaleapi.py job ls [--max=<int>]
```

Job information
-----------------


If you want to display the job-information, Please execute the following command. response is json-data.


```bash:command
JOBID='<Job-ID obtained when you create the job>'
rescaleapi.py job info ${JOBID}
```

Create Job (Job Difinition)
------------------------------

you can create the job by using the following command.
(this command doesn't execute the job. Job-difinition is saved in Rescale.)


if you indicate JSON-data directly:

```bash:command
JSON='<JSON-DATA to create rescale-job>'
rescaleapi.py job create ${JSON}
```

else if you indicate JSON-FILE:

```bash:command
JSONFILE=<'JSONFILE job'>
rescaleapi.py job create --file ${JSONFILE}
```

Job submittion (Run)
------------------------------

you can submit the job you created with this command.

```bash:command
JOBID='<Job-ID obtained when you create the job>'
rescaleapi.py job submit ${JOBID}
```

Job Monitor
------------------------------

You can use this command to check the job-status or the end of the job.

```bash:command
JOBID='<Job-ID obtained when you create the job>'
rescaleapi.py job monitor ${JOBID}
```

Job Deletion
------------------------------

You can delete the job with the following command.

```bash:command
JOBID='<Job-ID obtained when you create the job>'
rescaleapi.py job delete ${JOBID}
```

Job Stop
------------------------------

You can stop the running job with the following command.

```bash:command
JOBID='<Job-ID obtained when you create the job>'
rescaleapi.py job stop ${JOBID}
```

Job Sharing
------------------------------

You can share the job to a user account belongint same company account.

```bash:command
JOBID='<Job-ID obtained when you create the job>'
rescaleapi.py job share ${JOBID} --email=ADDRESS [--message="MESSAGE"]
```

File list
---------------------------------

You can take the file list for the Job-ID you indicate.

```bash:command
JOBID='<Job-ID obtained when you create the job>'
rescaleapi.py file ls ${JOBID} [--run=<int>]
```

File Information
---------------------------------

You can take the file-information for the file-ID you indicate.

```bash:command
FILEID='<File-ID obtained when you execute "rescaleapi.py file ls" command>'
rescaleapi.py file info ${FILEID}
```

Help
---------------------------------

```bash:command
rescaleapi.py -h | --help
```
